from __future__ import annotations

from .base import BaseParserService
from .base import ParserInput
from .base import ParserOutput


class ParserService(BaseParserService):
    def process(self, input_data: ParserInput) -> ParserOutput:
        return ParserOutput(
            raw_text='',
            filename=input_data.file.filename,
            file_extension='',
        )
