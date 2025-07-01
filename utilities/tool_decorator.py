def tool(func):
    """Decorator to mark a function as a tool for agent registration."""
    func._is_tool = True
    return func 