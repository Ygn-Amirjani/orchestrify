from abc import ABC, abstractmethod
from typing import Dict, List

class Repository(ABC):
    """
    Abstract base class defining methods for basic CRUD operations.
    """

    @abstractmethod
    def create(self, data: Dict[str, str]) -> None:
        """Create a new entry in the repository."""
        raise NotImplementedError

    @abstractmethod
    def read(self, id: str) -> Dict[str, str]:
        """Retrieve an entry from the repository by its ID."""
        raise NotImplementedError
    
    @abstractmethod
    def read_all(self) -> List[str]:
        """Retrieve all entries from the repository."""
        raise NotImplementedError

    @abstractmethod
    def update(self, id: str, data: Dict[str, str]) -> None:
        """Update an entry in the repository."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: str) -> None:
        """Delete an entry from the repository."""
        raise NotImplementedError
