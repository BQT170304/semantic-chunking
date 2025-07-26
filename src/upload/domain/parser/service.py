from __future__ import annotations

import os

from .base import BaseParserService
from .base import ParserInput
from .base import ParserOutput
from .extractor import ExtractorService
from .markdown_generator import NovaMarkdownGenerator


class ParserService(BaseParserService):
    def __init__(self):
        self.extractor = ExtractorService()
        self.parser = NovaMarkdownGenerator()

    def process(self, input_data: ParserInput) -> ParserOutput:
        extracted_text = self.extractor.extract(input_data.file)
        raw_text = self.parser.generate(extracted_text)

        _, ext = os.path.splitext(input_data.file.filename.lower())
        return ParserOutput(
            raw_text=raw_text,
            filename=input_data.file.filename,
            file_extension=ext,
        )
