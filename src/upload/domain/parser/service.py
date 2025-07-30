from __future__ import annotations

import os

from .base import BaseParserService
from .base import ParserInput
from .base import ParserOutput
from .extractor import ExtractorService
from .parser import Parser


class ParserService(BaseParserService):
    def __init__(self):
        self.extractor = ExtractorService()
        self.parser = Parser()

    async def process(self, input_data: ParserInput) -> ParserOutput:
        extracted_text = self.extractor.extract(input_data.file)
        raw_text = await self.parser.parse(extracted_text)


        _, ext = os.path.splitext(input_data.file.filename.lower())
        return ParserOutput(
            raw_text=raw_text,
            filename=input_data.file.filename,
            file_extension=ext,
        )
