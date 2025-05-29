from interfaces.agents.chat import ChatAgent
import os

from utilities.env import PROJECT_ROOT

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
        
        # Tool registry: add your tool instances here
        self.tools = {}

        # Use PROJECT_ROOT env variable if set, else default to two levels above this file
        if not PROJECT_ROOT:
            raise ValueError("PROJECT_ROOT environment variable is not set.")
            
        self.project_root = PROJECT_ROOT

    def register_tool(self, name, tool):
        """Register a tool instance with a given name."""
        self.tools[name] = tool

    async def use_tool(self, tool_name, input):
        """Call a registered tool by name with the given input."""
        tool = self.tools.get(tool_name)
        
        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found.")
        
        return await tool(input)
