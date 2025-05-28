from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, TypeVar, Generic, Type
  
# Type variables for input/output types
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')

@dataclass
class Message(Generic[InputT]):
    """Basic message container for agent communication."""
    content: InputT
    metadata: Dict[str, Any] = None

class Tool(ABC, Generic[InputT, OutputT]):
    """Base class for all tools that agents can use."""
    
    @abstractmethod
    async def __call__(self, input: InputT) -> OutputT:
        """Execute the tool with the given input."""
        pass

class Agent(ABC, Generic[InputT, OutputT]):
    """Base class for all agents."""
        
    @abstractmethod
    async def process(self, message: Message[InputT]) -> OutputT:
        """Process an incoming message and return a response."""
        pass
    
class AgentFactory:
    """Simple factory for creating agent instances."""
    _registry: Dict[str, Type[Agent]] = {}
    
    @classmethod
    def register(cls, name: str, agent_cls: Type[Agent]) -> None:
        """Register an agent class with the factory."""
        cls._registry[name] = agent_cls
    
    @classmethod
    def create(cls, name: str, **kwargs) -> Agent:
        """Create a new agent instance by name."""
        if name not in cls._registry:
            raise ValueError(f"Unknown agent type: {name}")
        return cls._registry[name](**kwargs)