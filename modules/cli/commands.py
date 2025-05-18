from typing import Callable, Dict, Optional
import json
import webbrowser
from modules.web import get_google_search_results
from abc import ABC, abstractmethod
from prompt_toolkit import print_formatted_text as print

class Response(ABC):
    @abstractmethod
    def to_string(self) -> str:
        pass
    
class StringResponse(Response):
    def __init__(self, text: str):
        self.text = text

    def to_string(self) -> str:
        return self.text
    
class MenuOption:
    def __init__(self, label: str, action: Callable):
        self.label = label
        self.action = action

    def __str__(self):
        return self.label

class MenuResponse(Response):
    def __init__(self, prompt: str, options: list[MenuOption]):
        self.prompt = prompt
        self.options = options

    def to_string(self) -> str:
        # Summarize for memory log
        return f"[Menu] {self.prompt} ({len(self.options)} options)"

class CommandRegistry:
    def __init__(self):
        self.commands: Dict[str, Callable] = {}
    
    def register(self, command_name: str):
        def decorator(func: Callable):
            self.commands[command_name] = func
            return func
        return decorator
    
    def execute(self, command: str, args: str) -> Optional[Response]:
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
def help_command(args: str) -> Response:
    return StringResponse("Available commands:\n" + "\n".join(f"/{cmd}" for cmd in registry.commands.keys()))

@registry.register("echo")
def echo_command(args: str) -> Response:
    return StringResponse(args)

def create_open_action(link):
    return lambda: webbrowser.open(link)

@registry.register("search")
def search_command(args: str) -> Response:
    results = get_google_search_results(args)
    if results is None:
        return StringResponse("Error: Failed to retrieve search results")
    
    options = []
    for result in results:
        options.append(
            MenuOption(
                label=result["link"], 
                action=create_open_action(result["link"])
            )
        )
    
    return MenuResponse("Select a search result to open: ", options)

@registry.register("crawl")
def crawl_command(args: str) -> Response:
    return StringResponse("TODO: Crawl Tool Implementation")