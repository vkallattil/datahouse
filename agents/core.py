import json
from openai import OpenAI
from .prompts import SYSTEM_PROMPT
from .tool_selector import ToolSelector
from .tool_registry import ToolRegistry
from typing import Dict, Any, List, Tuple

class DatahouseAgent():
    """
    The DatahouseAgent is the primary entry point and orchestrator for the Datahouse system.

    It is a broadly knowledgeable agent with access to the web, enabling it to interpret user requests, coordinate workflows, and autonomously solve a wide range of problems. 
    """

    def __init__(self):
        """
        Initialize the DatahouseAgent's OpenAI chat context.
        """

        self.system_prompt = SYSTEM_PROMPT

        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        self.client = OpenAI()
        self.tool_selector = ToolSelector(self.client)
        self.tool_registry = ToolRegistry()

    def clear_messages(self):
        """Clear the chat history."""
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    def process(self, message: str) -> str:
        """
        Process a user message by leveraging the agent's knowledge and web access to generate a response.
        
        Args:
            message: The user input or request to process.
        Returns:
            The generated response based on available resources and reasoning.
        Raises:
            OpenAIError: If there's an error with the API call.
        """

        # Use the tool selector to determine which tools to use
        selected_tools = self.tool_selector.select_tool(message)
        
        if not selected_tools:
            return "No specific tools needed for this request."
        else:
            # Format the response to show all selected tools
            tool_list = []
            for tool_name, score in selected_tools:
                tool_list.append(f"{tool_name} (Score: {score:.3f})")
            
            return f"Tools needed: {', '.join(tool_list)}"

    def register_tool(self, 
                     name: str, 
                     function, 
                     parameter_schema: Dict[str, Any],
                     description: str = "") -> None:
        """
        Register a new tool with the agent.
        
        Args:
            name: Tool name
            function: The function to execute
            parameter_schema: Schema defining required parameters and types
            description: Tool description
        """
        self.tool_registry.register_tool(name, function, parameter_schema, description)

    def unregister_tool(self, name: str) -> bool:
        """
        Remove a tool from the agent.
        
        Args:
            name: Tool name to remove
            
        Returns:
            True if tool was removed, False if not found
        """
        return self.tool_registry.unregister_tool(name)

    def get_available_tools(self) -> List[str]:
        """Get a list of all available tool names."""
        return self.tool_registry.get_available_tools()

    def get_tool_info(self) -> Dict[str, Any]:
        """Get information about the tool selector and available tools."""
        return {
            "available_tools": self.get_available_tools(),
            "tool_details": self.tool_registry.get_tool_info(),
            "tool_selector_info": self.tool_selector.get_cache_info()
        }
