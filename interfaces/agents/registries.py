from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Optional, List
from interfaces.agents.tools import Tool

@dataclass
class ContextResource:
    """
    Represents a context resource that can be either a file or a directory.
    """
    name: str
    description: str
    path: Path

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "path": str(self.path)
        }

class ContextResourceRegistry:
    def __init__(self):
        self.entries: Dict[str, ContextResource] = {}

    def register(self, name: str, description: str, path: Path):
        self.entries[name] = ContextResource(name, description, path)

    def get(self, name: str) -> Optional[ContextResource]:
        return self.entries.get(name)

    def list(self) -> List[ContextResource]:
        return list(self.entries.values())

@dataclass
class DocumentationLink:
    """
    Represents a documentation link.
    """
    name: str
    description: str
    url: str

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url
        }

class DocumentationLinkRegistry:
    def __init__(self):
        self.entries: Dict[str, DocumentationLink] = {}

    def register(self, name: str, description: str, url: str):
        self.entries[name] = DocumentationLink(name, description, url)

    def get(self, name: str) -> Optional[DocumentationLink]:
        return self.entries.get(name)

    def list(self) -> List[DocumentationLink]:
        return list(self.entries.values())

@dataclass
class ToolEntry:
    """
    Represents a tool entry.
    """
    name: str
    description: str
    tool: Tool

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "tool": self.tool
        }

class ToolRegistry:
    def __init__(self):
        self.entries: Dict[str, ToolEntry] = {}

    def register(self, name: str, description: str, tool: Tool):
        if name in self.entries:
            raise ValueError(f"Tool {name} already registered")
            
        self.entries[name] = ToolEntry(name, description, tool)

    def get(self, name: str) -> Optional[Tool]:
        return self.entries.get(name).tool

    def list(self) -> List[ToolEntry]:
        return list(self.entries.values())