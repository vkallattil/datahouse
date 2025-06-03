from pathlib import Path
from interfaces.agents.base import Agent, Message
from interfaces.agents.openai_context import OpenAIChatContextManager
from interfaces.agents.tools import Tool
from interfaces.agents.registries import (
    ContextResource, DocumentationLink, ToolEntry,
    ContextResourceRegistry, DocumentationLinkRegistry, ToolRegistry
)

class DatahouseAgent(Agent[str, str]):
    """
    The DatahouseAgent is the primary entry point and orchestrator for the Datahouse system.

    It is a broadly knowledgeable agent with access to tools, resources, and the web, enabling it to interpret user requests, coordinate workflows, and autonomously solve a wide range of problems. The agent leverages dynamic registries and integrations to research, analyze, and deliver comprehensive solutions, acting as the interface between users and the full capabilities of the Datahouse system.
    """

    def __init__(self):
        """
        Initialize the DatahouseAgent with registries for context resources, documentation links, and tools.
        These registries enable extensible, dynamic access to system knowledge and capabilities, supporting autonomous research and broad problem-solving.
        """
        super().__init__()
        self.system_prompt = (
            "You are the DatahouseAgent, the primary entry point and orchestrator for the Datahouse system. "
            "You possess broad knowledge across domains and have access to a suite of tools, resources, and the web to fulfill your objectives. "
            "Your responsibilities include interpreting and executing user requests, leveraging available capabilities to research, analyze, and solve problems, and coordinating complex workflows. "
            "Your role is to ensure seamless, intelligent interaction with the Datahouse system and to provide users with comprehensive, actionable results."
        )
        self.context_manager = OpenAIChatContextManager(self.system_prompt)

        # Dynamic registries
        self.context_resource_registry = ContextResourceRegistry()
        self.documentation_link_registry = DocumentationLinkRegistry()
        self.tool_registry = ToolRegistry()

    def process(self, message: Message[str]) -> str:
        """
        Process a user message by leveraging the agent's knowledge, tools, and web access to generate a comprehensive response.
        
        Args:
            message: The user input or request to process.
        Returns:
            The generated response based on available resources and reasoning.
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        self.context_manager.add_user_message(message.content)
        return self.context_manager.get_response()
