import json
from openai import OpenAI
from .prompts import SYSTEM_PROMPT
from .tool_selector import ToolSelector
from typing import Callable
from modules.search import google_search
from modules.crawl import get_page

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
            {"role": "developer", "content": self.system_prompt}
        ]

        self.client = OpenAI()
        self.tool_selector = ToolSelector(self.client)

    def clear_messages(self):
        """Clear the chat history."""
        self.messages = [
            {"role": "developer", "content": self.system_prompt}
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
