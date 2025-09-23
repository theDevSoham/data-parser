from abc import ABC, abstractmethod
from typing import Dict, Any

class Storage(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    def upsert_post(self, doc: Dict[str, Any]) -> None:
        """Insert or update a post document."""
        pass
