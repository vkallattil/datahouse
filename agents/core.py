"""
Optimized DatahouseAgent - primary entry point and orchestrator for the Datahouse system.
"""

from dataclasses import dataclass, field
from openai import OpenAI
from typing import Dict, Any, List
from .prompts import SYSTEM_PROMPT
from .tool_registry import ToolRegistry

@dataclass
class AgentConfig:
    """Configuration for the DatahouseAgent."""
    system_prompt: str = SYSTEM_PROMPT
    cache_dir: str = "cache"

@dataclass
class Message:
    """Represents a chat message."""
    role: str
    content: str

class DatahouseAgent:
    """Optimized DatahouseAgent with simplified structure and better performance."""
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.client = OpenAI()
        self.tool_registry = ToolRegistry(self.client, self.config.cache_dir)
        self.messages = [Message("developer", self.config.system_prompt)]
    
    def clear_messages(self) -> None:
        """Clear chat history, keeping system prompt."""
        self.messages = [Message("developer", self.config.system_prompt)]
    
    def process(self, message: str) -> str:
        """Process user message and return tool selection or response."""
        selected_tools = self.tool_registry.select_tool(message)
        
        if not selected_tools:
            return "No specific tools needed for this request."
        
        tool_list = [f"{name} ({score:.3f})" for name, score in selected_tools]
        return f"Tools needed: {', '.join(tool_list)}"
    
    def register_tool(self, name: str, function, parameter_schema: Dict[str, Any], description: str = "") -> None:
        """Register a new tool with the agent."""
        self.tool_registry.register_tool(name, function, parameter_schema, description)
    
    def unregister_tool(self, name: str) -> bool:
        """Remove a tool from the agent."""
        return self.tool_registry.unregister_tool(name)
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tool names."""
        return self.tool_registry.get_available_tools()
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get comprehensive tool information."""
        return {
            "available_tools": self.get_available_tools(),
            "tool_details": self.tool_registry.get_tool_info(),
            "cache_info": self.tool_registry.get_cache_info()
        }
