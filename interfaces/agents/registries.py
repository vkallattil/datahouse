from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional, List, Any

@dataclass
class ContextResource:
    """
    Represents a context resource that can be either a file or a directory.
    """
    name: str
    description: str
    path: Path

@dataclass
class DocumentationLink:
    name: str
    description: str
    url: str

@dataclass
class ToolEntry:
    name: str
    description: str
    tool: Any  # Can be Tool class or instance

from typing import TypeVar, Generic

T = TypeVar("T")

class Registry(Generic[T]):
    def __init__(self):
        self.entries: Dict[str, T] = {}

    def register(self, entry: T):
        self.entries[entry.name] = entry

    def get(self, name: str) -> Optional[T]:
        return self.entries.get(name)

    def list(self) -> List[T]:
        return list(self.entries.values())

    def find_by_description(self, query: str) -> List[T]:
        query_lower = query.lower()
        return [e for e in self.entries.values() if query_lower in e.description.lower() or query_lower in e.name.lower()]
