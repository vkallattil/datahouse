from typing import Callable, Dict, Optional

class CommandRegistry:
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
    
    def register(self, command_name: str):
        def decorator(func: Callable):
            self.commands[command_name] = func
            return func
        return decorator
    
    def execute(self, command: str, args: str) -> Optional[str]:
        if command in self.commands:
            return self.commands[command](args)
        return None

class CommandExit(Exception):
    """Raised when the assistant should exit"""
    pass

class CommandClear(Exception):
    """Raised when the terminal should be cleared"""
    pass

# Create global registry instance
registry = CommandRegistry()

# Define some basic commands
@registry.register("exit")
def exit_command(args: str) -> str:
    print("Goodbye!")
    raise CommandExit()

@registry.register("clear")
def clear_command(args: str) -> str:
    raise CommandClear()

@registry.register("help")
def help_command(args: str) -> str:
    return "Available commands:\n" + "\n".join(f"/{cmd}" for cmd in registry.commands.keys())

@registry.register("echo")
def echo_command(args: str) -> str:
    return args

@registry.register("crawl")
def crawl_command(args: str) -> str:
    return "TODO: Crawl Tool Implementation"

@registry.register("search")
def search_command(args: str) -> str:
    return "TODO: Search Tool Implementation"