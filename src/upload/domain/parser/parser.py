from __future__ import annotations

import json
import re

from dotenv import load_dotenv
from shared.logging.logger import get_logger

from .markdown_generator import NovaMarkdownGenerator

logger = get_logger(__name__)
load_dotenv()


class Parser:
    def __init__(self, region_name=None, model_id=None):
        self.generator = NovaMarkdownGenerator(
            region_name=region_name, model_id=model_id,
        )

    async def parse(self, raw_text: str) -> str:
        logger.info('Starting document parsing', input_length=len(raw_text))

        # Get JSON structure from NovaMarkdownGenerator
        json_output = await self.generator.generate(raw_text)

        logger.info(
            'Received JSON output from generator', output_length=len(json_output),
        )

        # Parse the JSON output and merge with raw text
        markdown_content = self._merge_json_with_raw_text(json_output, raw_text)

        logger.info(
            'Completed document parsing', output_length=len(markdown_content),
        )
        return markdown_content

    def _merge_json_with_raw_text(self, json_output: str, raw_text: str) -> str:
        """
        Merge the JSON header structure with raw text to create structured markdown.
        """
        try:
            # Extract JSON from the output (in case there's additional text)
            json_match = re.search(r'\{.*\}', json_output, re.DOTALL)
            if not json_match:
                logger.warning(
                    'No JSON found in generator output, returning formatted raw text',
                )
                return self._format_as_basic_markdown(raw_text)

            # Parse the JSON
            headers_json = json.loads(json_match.group())
            logger.info(
                'Successfully parsed JSON headers',
                headers=list(headers_json.keys()),
            )

            # Create a copy of text lines to modify
            text_lines = raw_text.split('\n')

            # Replace original header lines with formatted markdown headers
            for level in ['h1', 'h2', 'h3', 'h4']:
                if level in headers_json:
                    markdown_prefix = '#' * int(level[1])  # h1 -> #, h2 -> ##, etc.

                    for header_text in headers_json[level]:
                        # Find and replace the matching text line
                        header_found_idx = self._find_header_line_index(
                            header_text, text_lines,
                        )

                        if header_found_idx >= 0:
                            # Replace the original line with formatted markdown header
                            text_lines[header_found_idx] = f'{markdown_prefix} {header_text}'

            # Format content lines (key-value pairs, etc.)
            formatted_lines = []
            for line in text_lines:
                line_stripped = line.strip()
                if line_stripped:
                    # Check if it's already a header (starts with #)
                    if line_stripped.startswith('#'):
                        formatted_lines.append(line_stripped)
                    # Keep table formatting and other content as is
                    else:
                        formatted_lines.append(line_stripped)
                else:
                    # Preserve empty lines
                    formatted_lines.append('')

            return '\n'.join(formatted_lines).strip()

        except json.JSONDecodeError as e:
            logger.error('Failed to parse JSON output', error=str(e))
            return self._format_as_basic_markdown(raw_text)
        except Exception as e:
            logger.error('Error merging JSON with raw text', error=str(e))
            return self._format_as_basic_markdown(raw_text)

    def _find_header_line_index(self, header_text: str, text_lines: list) -> int:
        """
        Find the index of the header line in the text that matches the header_text.
        """
        # First try exact match
        for i, line in enumerate(text_lines):
            if line.strip() == header_text.strip():
                return i

        # Then try partial match by removing numbering prefixes
        header_clean = re.sub(r'^[A-Z]\d*\.?\s*', '', header_text).strip().lower()

        for i, line in enumerate(text_lines):
            line_clean = re.sub(
                r'^[A-Z]\d*\.?\s*', '', line.strip(),
            ).strip().lower()
            # Check if the core text matches (at least 70% of words)
            header_words = header_clean.split()
            line_words = line_clean.split()

            if header_words and line_words:
                common_words = set(header_words) & set(line_words)
                if len(common_words) >= len(header_words) * 0.7:
                    return i

        return -1

    def _format_as_basic_markdown(self, raw_text: str) -> str:
        """
        Basic markdown formatting when JSON parsing fails.
        """
        lines = raw_text.split('\n')
        markdown_lines = []

        for line in lines:
            line = line.strip()
            if not line:
                markdown_lines.append('')
                continue

            # Basic header detection
            if re.match(r'^[A-Z]\.\s', line):  # A. Header pattern
                markdown_lines.append(f'## {line}')
            elif re.match(r'^[A-Z]\.\d+\.', line):  # A.1. Header pattern
                markdown_lines.append(f'### {line}')
            elif line.isupper() and len(line) > 10:  # All caps likely header
                markdown_lines.append(f'# {line}')
            else:
                markdown_lines.append(line)

        return '\n'.join(markdown_lines)
