from typing import BinaryIO
from abc import ABC, abstractmethod

class BaseStorage(ABC):
    @abstractmethod
    def save(self, filename: str, data: BinaryIO, length: int = -1, size: int = -1) -> str:
        pass
