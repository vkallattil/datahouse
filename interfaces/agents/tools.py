from interfaces.agents.types import InputT, OutputT
from abc import ABC, abstractmethod
from typing import Generic

class Tool(ABC, Generic[InputT, OutputT]):
    """Base class for all tools that agents can use."""
    
    @abstractmethod
    async def __call__(self, input: InputT) -> OutputT:
        """Execute the tool with the given input."""
        pass
