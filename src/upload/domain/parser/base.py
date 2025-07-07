from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import Union

from fastapi import UploadFile
from pydantic import BaseModel


class ParserInput(BaseModel):
    """Input data for the parsing process."""
    file: UploadFile


class ParserOutput(BaseModel):
    """Output data from the parsing process."""
    raw_text: Union[str, dict]
    filename: str
    file_extension: Optional[str] = None


class BaseParserService(ABC):
    """Abstract base class for parsers."""

    @abstractmethod
    def process(self, input_data: ParserInput) -> ParserOutput:
        """Parse the input file and extract text content."""
        raise NotImplementedError()
