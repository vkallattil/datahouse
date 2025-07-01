"""
Optimized DatahouseAgent - primary entry point and orchestrator for the Datahouse system.
"""

from dataclasses import dataclass, field
from openai import OpenAI
from typing import Dict, Any, List
from .prompts import SYSTEM_PROMPT
from .tool_registry import ToolRegistry
import logging

logger = logging.getLogger(__name__)

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
        """Process user message: log tool selection, execution, results, and generate a response."""
        selected_tools = self.tool_registry.select_tool(message)
        # Combined log for tool selection and parameter extraction
        tool_param_log = []
        tool_results = {}
        self.messages.append(Message("user", message))

        if not selected_tools:
            # No tools needed, skip tool logs
            completion = self.client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=[{"role": m.role, "content": m.content} for m in self.messages]
            )
            response = completion.choices[0].message.content
            self.messages.append(Message("assistant", response))
            return response

        # For each selected tool, extract parameters and execute
        for tool_name, score in selected_tools:
            params = self.tool_registry.extract_parameters(message, tool_name)
            tool_param_log.append(f"{tool_name} (score={score:.3f}): {params}")
            success, result, error = self.tool_registry.execute_tool(tool_name, params)
            tool_results[tool_name] = result if success else f"Error: {error}"

        if tool_param_log:
            logger.info("Tool selection and parameter extraction:\n" + "\n".join(tool_param_log))

        # Combined log for tool execution response
        tool_exec_log = []
        for tool_name, result in tool_results.items():
            if (
                isinstance(result, list)
                and result
                and isinstance(result[0], dict)
                and 'url' in result[0] and 'content' in result[0]
            ):
                tool_exec_log.append(f"{tool_name} results:")
                for idx, entry in enumerate(result, 1):
                    url = entry.get('url', '')
                    content = entry.get('content', '')
                    preview = (content[:120] + '...') if len(content) > 120 else content
                    tool_exec_log.append(f"  [{idx}] URL: {url}\n      Content: {preview}")
            else:
                tool_exec_log.append(f"{tool_name} result: {result}")
        if tool_exec_log:
            logger.info("Tool execution response:\n" + "\n".join(tool_exec_log))

        # Build context for LLM response
        tool_context = "\n".join([
            f"Tool: {name}\nResult: {tool_results[name]}" for name in tool_results
        ])
        self.messages.append(Message("developer", tool_context))
        self.messages.append(Message("developer", "Respond to the user, using the tool results above as context."))
        completion = self.client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": m.role, "content": m.content} for m in self.messages]
        )
        response = completion.choices[0].message.content

        self.messages.append(Message("assistant", response))
        return response
    
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
