from typing import Generic, Dict, Any
from dataclasses import dataclass
from interfaces.agents.types import InputT

@dataclass
class Message(Generic[InputT]):
    """Basic message container for agent communication."""
    content: InputT
    metadata: Dict[str, Any] = None
