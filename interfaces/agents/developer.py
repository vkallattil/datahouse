from interfaces.agents.chat import ChatAgent

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
        # Future: Initialize resources, tools, or agent integrations here.
