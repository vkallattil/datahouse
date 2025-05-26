"""Command registry and response handling for the Datahouse CLI.

This module defines the core command system, including command registration,
execution, and response handling. It provides a flexible way to extend the
CLI with new commands and menu-based interactions.
"""

from typing import Callable, Dict, List, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from prompt_toolkit import print_formatted_text as print

# Third-party imports
import webbrowser

# Local application imports
from utilities.language.openai import openai_client

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
    
@dataclass
class MenuOption:
    """Represents a single option in a menu.
    
    Attributes:
        label: The text shown to the user for this option.
        action: A callable that will be executed when this option is selected.
    """
    label: str
    action: Callable[[], Any]
    
    def __str__(self) -> str:
        """Return the label when converted to string.
        
        Returns:
            The label text of this menu option.
        """
        return self.label

class MenuResponse(Response):
    """A response that presents a menu of options to the user.
    
    This type of response pauses command processing and displays an interactive
    menu from which the user can select an option.
    """
    
    def __init__(self, prompt: str, options: List[MenuOption]):
        """Initialize with a prompt and list of options.
        
        Args:
            prompt: The message displayed above the menu options.
            options: A list of MenuOption instances to display.
        """
        self.prompt = prompt
        self.options = options

    def to_string(self) -> str:
        """Generate a summary of the menu for logging purposes.
        
        Returns:
            A string in the format: "[Menu] <prompt> (X options)"
        """
        return f"[Menu] {self.prompt} ({len(self.options)} options)"

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

class CommandExit(Exception):
    """Exception raised to signal that the CLI should exit.
    
    When raised from a command handler, this will cause the main loop to
    terminate cleanly.
    """
    pass


class CommandClear(Exception):
    """Exception raised to signal that the terminal should be cleared.
    
    When raised from a command handler, this will clear the terminal screen
    and redisplay the initial prompt.
    """
    pass

# Create a global registry instance for commands
registry = CommandRegistry()

# Basic command implementations

@registry.register("exit")
def exit_command(args: str) -> Response:
    """Exit the application.
    
    Args:
        args: Ignored.
        
    Raises:
        CommandExit: To signal the main loop to terminate.
    """
    raise CommandExit()


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
    
    Args:
        args: If provided, show detailed help for a specific command.
        
    Returns:
        A StringResponse with command help information.
    """
    if args:
        # Show detailed help for a specific command
        cmd = args.strip().lower()
        if cmd in registry.commands:
            doc = registry.commands[cmd].__doc__
            return StringResponse(doc or f"No documentation available for /{cmd}")
        return StringResponse(f"Unknown command: /{cmd}")
    
    # Show list of all commands
    commands = sorted(registry.commands.keys())
    help_text = "Available commands (type '/help <command>' for details):\n"
    help_text += "\n".join(f"  /{cmd}" for cmd in commands)
    return StringResponse(help_text)


@registry.register("echo")
def echo_command(args: str) -> Response:
    """Echo the provided arguments back to the user.
    
    Args:
        args: The text to echo back.
        
    Returns:
        A StringResponse containing the input text.
        
    Example:
        /echo Hello, world!
    """
    return StringResponse(args)


@registry.register('chat')
def chat_command(args: str) -> Response:
    """Generate a response using OpenAI's language model.
    
    This command sends the provided prompt to OpenAI's API and returns
    the generated response. It requires a valid OPENAI_API_KEY to be set.
    
    Args:
        args: The prompt to send to the language model.
        
    Returns:
        A StringResponse with the generated text or an error message.
        
    Example:
        /chat Write a haiku about artificial intelligence
    """
    if not args:
        return StringResponse(
            "Please provide a prompt.\n"
            "Usage: /chat <your prompt>\n"
            "Example: /chat Write a one-sentence bedtime story about a unicorn"
        )
    
    if not openai_client:
        return StringResponse(
            "Error: OpenAI client not initialized.\n"
            "Please set the OPENAI_API_KEY environment variable with a valid API key."
        )
    
    try:
        response = openai_client.generate_response(args)
        return StringResponse(response.strip())
    except Exception as e:
        return StringResponse(f"Error: {str(e)}")