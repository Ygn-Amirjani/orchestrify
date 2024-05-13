from abc import ABC, abstractmethod
from typing import Dict, List

class Repository(ABC):

    @abstractmethod
    def create(self, data: Dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def read(self, id: str) -> Dict[str, str]:
        raise NotImplementedError
    
    @abstractmethod
    def read_all(self) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def update(self, id: str, data: Dict[str, str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> None:
        raise NotImplementedError
