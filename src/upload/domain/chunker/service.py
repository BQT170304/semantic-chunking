from __future__ import annotations

import hashlib
import math
import re
from typing import Dict
from typing import List

import nltk

from .base import BaseChunkerService
from .base import Chunk
from .base import ChunkerInput
from .base import ChunkerOutput
nltk.download('punkt')
nltk.download('punkt_tab')


class ChunkerService(BaseChunkerService):
    def __init__(self):
        self.chunker = Chunker()

    def process(self, input_data: ChunkerInput) -> ChunkerOutput:
        chunks = self.chunker.chunk_markdown_by_title_and_tokens(
            text=input_data.text,
            filename=input_data.metadata.get('filename', 'unknown'),
            min_heading_level=input_data.metadata.get('min_heading_level', 1),
        )
        return ChunkerOutput(
            chunks=chunks,
        )


class Chunker:
    def __init__(self):
        self.chunk_id = 0

    def chunk_markdown_by_title_and_tokens(self, text: str, filename: str, min_heading_level: int = 1) -> List[
        Chunk
    ]:
        pattern = r'(#{1,6})\s+(.+)'
        matches = list(re.finditer(pattern, text))
        all_chunks = []

        for idx, match in enumerate(matches):
            heading_marks = match.group(1)
            section_title = match.group(2).strip()
            heading_level = len(heading_marks)

            if heading_level < min_heading_level:
                continue

            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            section_content = text[start:end].strip()

            if not section_content:
                continue

            section_chunks = self.smart_chunk_section(section_content, filename, section_title)
            for chunk in section_chunks:
                chunk.heading_level = heading_level

            all_chunks.extend(section_chunks)

        return all_chunks

    def smart_chunk_section(
        self, text: str, filename: str, section_title: str, max_tokens: int = 2048,
        sentence_overlap: int = 2,
    ) -> List[Chunk]:
        if self.is_markdown_table(text):
            return self.handle_table_chunking(text, filename, section_title, max_tokens)

        sentences = nltk.sent_tokenize(text)
        chunks = []
        seen_hashes = set()
        i = 0
        last_chunk_sentences: List[str] = []

        while i < len(sentences):
            token_count = 0
            selected_sentences = []
            j = i

            while j < len(sentences):
                sentence = sentences[j]
                tokens = self.count_tokens(sentence)
                if token_count + tokens > max_tokens:
                    break
                selected_sentences.append(sentence)
                token_count += tokens
                j += 1

            if not selected_sentences:
                i += 1
                continue

            if last_chunk_sentences:
                overlap_count = min(sentence_overlap, len(last_chunk_sentences))
                sentences_to_remove = 0

                for k in range(overlap_count):
                    if (
                        k < len(selected_sentences) and
                        k < len(last_chunk_sentences) and
                        selected_sentences[k].strip() == last_chunk_sentences[-(overlap_count - k)].strip()
                    ):
                        sentences_to_remove = k + 1
                    else:
                        break

                if sentences_to_remove > 0:
                    selected_sentences = selected_sentences[sentences_to_remove:]
                    token_count = self.count_tokens(' '.join(selected_sentences))

                    if not selected_sentences:
                        i += 1
                        continue

            content = ' '.join(selected_sentences).strip()
            content = self.enhance_content_formatting(content)

            if self.is_invalid_table_fragment(content):
                i = j
                continue

            content_hash = hashlib.md5(content.encode()).hexdigest()
            if content_hash in seen_hashes:
                i = j - sentence_overlap if j - sentence_overlap > i else i + 1
                continue

            seen_hashes.add(content_hash)

            chunk_type = 'table' if self.is_markdown_table(content) else 'text'
            content_table_json = self.parse_markdown_table(content) if chunk_type == 'table' else None

            chunk = Chunk(
                id=self.chunk_id,
                content=content,
                filename=filename,
                section_title=section_title,
                position=i,
                tokens=token_count,
                type=chunk_type,
                content_json=content_table_json,
            )
            chunks.append(chunk)
            self.chunk_id += 1

            last_chunk_sentences = selected_sentences[-sentence_overlap:] if len(selected_sentences) >= sentence_overlap else selected_sentences
            i = max(i + len(selected_sentences) - sentence_overlap, i + 1) if j < len(sentences) else j

        return chunks

    def handle_table_chunking(self, table_text: str, filename: str, section_title: str, max_tokens: int = 2048) -> List[
        Chunk
    ]:
        if self.count_tokens(table_text) <= max_tokens:
            chunk = Chunk(
                id=self.chunk_id,
                content=table_text,
                filename=filename,
                section_title=section_title,
                position=0,
                tokens=self.count_tokens(table_text),
                type='table',
                content_json=self.parse_markdown_table(table_text),
            )
            self.chunk_id += 1
            return [chunk]

        table_chunks = self.split_large_markdown_table(table_text, max_tokens)
        chunks = []

        for i, chunk_content in enumerate(table_chunks):
            chunk = Chunk(
                id=self.chunk_id,
                content=chunk_content,
                filename=filename,
                section_title=section_title,
                position=i,
                tokens=self.count_tokens(chunk_content),
                type='table',
                content_json=self.parse_markdown_table(chunk_content),
            )
            chunks.append(chunk)
            self.chunk_id += 1

        return chunks

    def enhance_content_formatting(self, content: str) -> str:
        lines = content.strip().split('\n')
        bullet_count = sum(1 for line in lines if line.strip().startswith('- ') or line.strip().startswith('• '))

        if bullet_count >= 3:
            if any(
                keyword in content.lower() for keyword in
                ['địa chỉ', 'số nhà', 'phường', 'quận', 'tỉnh', 'thành phố']
            ):
                return self.format_address_info(content)
            else:
                return self.format_bullet_points_to_table(content)

        return content

    def format_address_info(self, text: str) -> str:
        lines = text.strip().split('\n')
        address_items = []
        other_items = []
        address_fields = ['Số nhà/Đường', 'Phường/Xã', 'Quận/Huyện', 'Tỉnh/Thành phố', 'Mã bưu chính']

        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                content = line[2:].strip()
                if ':' in content:
                    key, value = content.split(':', 1)
                    key = key.strip()
                    value = value.strip()

                    if any(field in key for field in address_fields):
                        address_items.append({'key': key, 'value': value})
                    else:
                        other_items.append({'key': key, 'value': value})

        result = []
        if address_items:
            result.append('**Địa chỉ:**')
            result.append('| Thông tin | Chi tiết |')
            result.append('| --- | --- |')
            for item in address_items:
                result.append(f"| {item['key']} | {item['value']} |")
            result.append('')

        if other_items:
            result.append('**Thông tin bổ sung:**')
            result.append('| Thông tin | Chi tiết |')
            result.append('| --- | --- |')
            for item in other_items:
                result.append(f"| {item['key']} | {item['value']} |")

        return '\n'.join(result)

    def format_bullet_points_to_table(self, text: str) -> str:
        lines = text.strip().split('\n')
        bullet_items = []

        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('• '):
                content = line[2:].strip()
                if ':' in content:
                    key, value = content.split(':', 1)
                    bullet_items.append({'key': key.strip(), 'value': value.strip()})
                else:
                    bullet_items.append({'key': content, 'value': ''})

        if len(bullet_items) >= 3:
            table_lines = ['| Thông tin | Chi tiết |', '| --- | --- |']
            for item in bullet_items:
                key = item['key']
                value = item['value']
                table_lines.append(f'| {key} | {value} |')
            return '\n'.join(table_lines)

        return text

    def is_markdown_table(self, text: str) -> bool:
        lines = [line.strip() for line in re.split(r'\r?\n', text.strip()) if line.strip()]
        if len(lines) >= 2:
            if '|' in lines[0] and '|' in lines[1]:
                return re.fullmatch(r'\|?[-|:\s]+[-|:\s]+\|?', lines[1]) is not None
        return False

    def is_invalid_table_fragment(self, text: str) -> bool:
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        if len(lines) < 3 and any('|' in line for line in lines):
            has_separator = any(re.fullmatch(r'\|?[-|:\s]+[-|:\s]+\|?', line) for line in lines)
            if not has_separator:
                table_like_lines = [line for line in lines if '|' in line and not line.startswith('#')]
                if table_like_lines and len(table_like_lines) == len(lines):
                    return True
        return False

    def parse_markdown_table(self, markdown: str) -> List[Dict[str, str]]:
        lines = markdown.strip().splitlines()
        table_lines = [line for line in lines if '|' in line]
        if len(table_lines) < 3:
            return []
        headers = [h.strip() for h in table_lines[0].split('|') if h.strip()]
        result = []
        for row_line in table_lines[2:]:
            values = [v.strip() for v in row_line.split('|') if v.strip()]
            if len(values) == len(headers):
                result.append(dict(zip(headers, values)))
        return result

    def split_large_markdown_table(self, table_text: str, max_tokens: int = 2048) -> List[str]:
        lines = [line.strip() for line in table_text.strip().splitlines() if line.strip()]
        table_lines = [line for line in lines if '|' in line]
        if len(table_lines) < 3:
            return [table_text]

        header = table_lines[0]
        separator = table_lines[1]
        rows = table_lines[2:]

        header_tokens = self.count_tokens(header + '\n' + separator)
        chunks = []
        current_rows = [header, separator]
        token_count = header_tokens

        for row in rows:
            row_tokens = self.count_tokens(row)
            if token_count + row_tokens > max_tokens and len(current_rows) > 2:
                chunks.append('\n'.join(current_rows))
                current_rows = [header, separator, row]
                token_count = header_tokens + row_tokens
            else:
                current_rows.append(row)
                token_count += row_tokens

        if len(current_rows) > 2:
            chunks.append('\n'.join(current_rows))

        return chunks

    def count_tokens(self, text: str) -> int:
        words = text.split()
        return math.ceil(len(words) * 1.3)
