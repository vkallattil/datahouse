import networkx as nx
from typing import Any

from interfaces.agents.base import Agent

class AgentGraph:
    """
    Graph-based agent team using networkx for agent collaboration and delegation.
    Each agent is a node, and edges define possible delegation/communication paths.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_agent(self, name: str, agent: Agent):
        self.graph.add_node(name, agent=agent)

    def connect(self, from_agent: str, to_agent: str):
        self.graph.add_edge(from_agent, to_agent)

    def process(self, message: Any, start_agent: str) -> Any:
        """
        Process a message by passing it to the specified agent.
        No delegation or edge traversal is performed.
        """
        agent = self.graph.nodes[start_agent]["agent"]
        return agent.process(message)
