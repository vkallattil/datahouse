from pathlib import Path
from interfaces.agents.chat import ChatAgent
from interfaces.agents.tools import Tool
from interfaces.agents.registries import ContextResource, DocumentationLink, ToolEntry, Registry

class DevelopmentManager(ChatAgent):
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
        # Compose a specialized system prompt for the DevelopmentManager
        dev_manager_prompt = (
            "You are the DevelopmentManager agent. "
            "You maintain comprehensive project context, including design specifications, requirements, and stakeholder preferences. "
            "Your responsibilities include receiving and interpreting feature requests, researching and evaluating existing solutions, "
            "conceptualizing and assessing approaches for alignment with project goals, and determining the best course of action. "
            "You autonomously decide whether to delegate tasks or execute them directly, and you present completed features for review. "
            "Your role is to ensure thoughtful, well-informed project development and coordination."
        )
        super().__init__(system_prompt=dev_manager_prompt)

        # Dynamic registries
        self.context_resource_registry = Registry[ContextResource]()
        self.documentation_link_registry = Registry[DocumentationLink]()
        self.tool_registry = Registry[ToolEntry]()

        # Example usage (commented):
        # self.context_resource_registry.register(ContextResource(
        #     name="design_spec",
        #     description="Project design specifications markdown file.",
        #     path=Path("docs/design_spec.md")
        # ))
        # self.documentation_link_registry.register(DocumentationLink(
        #     name="project_overview",
        #     description="Overview of the project documentation.",
        #     url="https://company.com/docs/project_overview"
        # ))
        # self.tool_registry.register(ToolEntry(
        #     name="example_tool",
        #     description="A tool that demonstrates example functionality.",
        #     tool=Tool  # Replace with actual Tool subclass or instance
        # ))