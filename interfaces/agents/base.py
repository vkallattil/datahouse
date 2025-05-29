from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, TypeVar, Generic
from interfaces.agents.messages import Message
from interfaces.agents.tools import Tool
from interfaces.agents.types import InputT, OutputT
  
class Agent(ABC, Generic[InputT, OutputT]):
    """Base class for all agents."""
        
    @abstractmethod
    async def process(self, message: Message[InputT]) -> OutputT:
        """Process an incoming message and return a response."""
        pass