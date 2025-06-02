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
    The DatahouseAgent acts as the main entry point for the Datahouse agent system.

    Responsibilities:
    - Maintains project context and resources, including design specifications, requirements, and owner preferences.
    - Accepts and interprets feature requests.
    - Researches existing solutions, evaluates documentation, and assesses library/tool suitability.
    - Conceptualizes solutions, ensuring compatibility with project specifications and constraints.
    - Integrates with tools and other agents to fulfill feature requests.
    - Receives completed features, reviews them, and presents results to the chat agent or project owner.
    
    This class is designed for extensibility: tools and agent integrations can be added to enable autonomous research and decision-making.
    """

    def __init__(self):
        """
        Initializes the DatahouseAgent with dynamic registries for context files, documentation links, and tools.
        Each registry supports registration, retrieval, and natural language search via descriptions.
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
        """Generate a text response using the OpenAI API.
        
        Args:
            message: The input prompt to send to the model.
        Returns:
            The generated text response.
        Raises:
            OpenAIError: If there's an error with the API call.
        """
        self.context_manager.add_user_message(message.content)
        return self.context_manager.get_response()
