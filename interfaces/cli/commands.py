"""Command registry and response handling for the Datahouse CLI.

This module defines the core command system, including command registration,
execution, and response handling. It provides a flexible way to extend the
CLI with new commands and menu-based interactions.
"""

from typing import Callable, Dict, List, Optional, Any, cast
from abc import ABC, abstractmethod
from dataclasses import dataclass
import webbrowser
from prompt_toolkit import print_formatted_text as print
from modules.search import google_search, GoogleSearchError

class Response(ABC):
    """Abstract base class for all command responses.
    
    This class defines the interface that all command responses must implement.
    Responses can be simple text, structured data, or interactive menus.
    """
    
    @abstractmethod
    def to_string(self) -> str:
        """Convert the response to a string representation.
        
        This method should be implemented by all subclasses to provide
        a string representation of the response, typically used for logging
        or displaying in non-interactive contexts.
        
        Returns:
            A string representation of the response.
        """
        pass
    
class StringResponse(Response):
    """A simple text-based response.
    
    This is the most common type of response, used for simple text output
    that will be displayed directly to the user.
    """
    
    def __init__(self, text: str):
        """Initialize with the text content.
        
        Args:
            text: The text content of the response.
        """
        self.text = text

    def to_string(self) -> str:
        """Return the text content directly.
        
        Returns:
            The stored text string.
        """
        return self.text
    
class CommandRegistry:
    """Registry for CLI commands with decorator-based registration.
    
    This class maintains a mapping of command names to their handler functions
    and provides methods to register and execute commands.
    """
    
    def __init__(self):
        """Initialize a new command registry with no commands."""
        self.commands: Dict[str, Callable[[str], Response]] = {}
    
    def register(self, command_name: str) -> Callable:
        """Decorator to register a new command.
        
        Args:
            command_name: The command string that will trigger this function.
            
        Returns:
            A decorator function that registers the command.
            
        Example:
            @registry.register("greet")
            def greet_command(args: str) -> Response:
                return StringResponse("Hello!")
        """
        def decorator(func: Callable[[str], Response]) -> Callable[[str], Response]:
            self.commands[command_name] = func
            return func
        return decorator
    
    def execute(self, command: str, args: str) -> Optional[Response]:
        """Execute a command with the given arguments.
        
        Args:
            command: The command name to execute.
            args: The arguments to pass to the command handler.
            
        Returns:
            The Response from the command, or None if the command doesn't exist.
        """
        if command in self.commands:
            return self.commands[command](args)
        return None

class CommandClear(Exception):
    """Exception raised to signal that the terminal should be cleared.
    
    When raised from a command handler, this will clear the terminal screen
    and redisplay the initial prompt.
    """
    pass

# Create a global registry instance for commands
registry = CommandRegistry()

# Basic command implementations
@registry.register("clear")
def clear_command(args: str) -> Response:
    """Clear the terminal screen.
    
    Args:
        args: Ignored.
        
    Raises:
        CommandClear: To signal the terminal should be cleared.
    """
    raise CommandClear()

@registry.register("help")
def help_command(args: str) -> Response:
    """Display help information about available commands.
    
    Returns:
        A StringResponse with command help information.
    """
    commands = sorted(registry.commands.keys())
    help_text = "Available commands:\n"
    help_text += "\n".join(f"  /{cmd}" for cmd in commands)
    return StringResponse(help_text)