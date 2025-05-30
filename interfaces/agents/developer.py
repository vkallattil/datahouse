from pathlib import Path
from interfaces.agents.base import Agent, Message
from interfaces.agents.openai_context import OpenAIChatContextManager
from interfaces.agents.tools import Tool
from interfaces.agents.registries import (
    ContextResource, DocumentationLink, ToolEntry,
    ContextResourceRegistry, DocumentationLinkRegistry, ToolRegistry
)

class DevelopmentManager(Agent[str, str]):
    """
    The DevelopmentManager agent acts as a project-level orchestrator and context holder.

    Responsibilities:
    - Maintains project context and resources, including design specifications, requirements, and owner preferences.
    - Accepts and interprets feature requests.
    - Researches existing solutions, evaluates documentation, and assesses library/tool suitability.
    - Conceptualizes solutions, ensuring compatibility with project specifications and constraints.
    - Decides whether to delegate tasks to other agents/tools or execute them directly.
    - Integrates with tools and other agents to fulfill feature requests.
    - Receives completed features, reviews them, and presents results to the chat agent or project owner.
    
    This class is designed for extensibility: tools and agent integrations can be added to enable autonomous research, decision-making, and delegation.
    """

    def __init__(self):
        """
        Initializes the DevelopmentManager with dynamic registries for context files, documentation links, and tools.
        Each registry supports registration, retrieval, and natural language search via descriptions.
        """
        super().__init__()
        self.system_prompt = (
            "You are the DevelopmentManager agent. "
            "You maintain comprehensive project context, including design specifications, requirements, and stakeholder preferences. "
            "Your responsibilities include receiving and interpreting feature requests, researching and evaluating existing solutions, "
            "conceptualizing and assessing approaches for alignment with project goals, and determining the best course of action. "
            "You autonomously decide whether to delegate tasks or execute them directly, and you present completed features for review. "
            "Your role is to ensure thoughtful, well-informed project development and coordination."
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
