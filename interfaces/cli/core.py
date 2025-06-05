"""Core functionality for the Command Line Interface (CLI) of the Datahouse application.

This module provides the main loop and input handling for the CLI, including command
processing and menu navigation.
"""

import os
from typing import Optional, Any
from prompt_toolkit import prompt, history as hs
from interfaces.cli.commands import (
    registry, CommandExit, CommandClear, 
    MenuResponse, StringResponse, Response
)
from interfaces.agents.core import DatahouseAgent

datahouse_agent = DatahouseAgent()

def handle_input(user_input: str) -> Response:
    """Process user input and return an appropriate response.
    
    This function handles both command inputs (starting with '/') and regular text inputs.
    Commands are executed through the command registry, while regular text is processed
    as a general input.
    
    Args:
        user_input: The raw input string from the user.
        
    Returns:
        A Response object containing the result of processing the input.
        
    Example:
        >>> handle_input("/help")
        <StringResponse with help text>
        >>> handle_input("Hello, world!")
        <StringResponse with processed text>
    """
    
    # Handle command inputs
    if not user_input:
        return StringResponse("")
        
    if user_input.startswith('/'):
        parts = user_input[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Execute command through registry
        response = registry.execute(command, args)
        if response is not None:
            return response
            
        return StringResponse(f"Unknown command: {command}")
    
    # Process non-command input through the DatahouseAgent
    
    try:
        response = datahouse_agent.process(user_input)
        return StringResponse(response)
    except Exception as e:
        return StringResponse(f"Error generating CLI response: {str(e)}")

def handle_menu_response(menu_response: MenuResponse) -> Optional[Any]:
    """Display a menu and handle user selection.
    
    This function presents a menu to the user with the provided options and
    executes the corresponding action when a valid selection is made.
    
    Args:
        menu_response: A MenuResponse object containing the menu prompt and options.
        
    Returns:
        The result of the selected menu action, or None if no valid selection was made.
        
    Example:
        >>> options = [
        ...     MenuOption("Option 1", lambda: print("Selected 1")),
        ...     MenuOption("Option 2", lambda: print("Selected 2"))
        ... ]
        >>> menu = MenuResponse("Choose an option:", options)
        >>> handle_menu_response(menu)
    """
    if not menu_response.options:
        print("No options available.")
        return None
        
    # Display menu prompt and options
    print(menu_response.prompt)
    print("-" * 40)
    
    for i, option in enumerate(menu_response.options, 1):
        print(f"{i}. {option.label}")
    
    # Get user selection
    selected_option = input("Pick an option (or q to cancel): ").strip()
    
    if selected_option.lower() == 'q':
        print("Operation cancelled.")
        return None
    
    # Validate input
    if not selected_option.isdigit():
        print("Please enter a valid number.")
        return None
    
    selected_index = int(selected_option) - 1
    
    if not (0 <= selected_index < len(menu_response.options)):
        print(f"Please enter a number between 1 and {len(menu_response.options)}")
        return None
    
    # Execute the selected action
    try:
        return menu_response.options[selected_index].action()
    except Exception as e:
        print(f"Error executing action: {e}")
        return None

def display_initial_prompt() -> None:
    """Display the initial welcome message and help instructions.

    This function is called when the CLI starts and after clearing the screen.
    It provides users with basic information about how to interact with the application.
    """
    print("=" * 50)
    print("Type '/help' to see available commands.")
    print("Type '/exit' to quit the application.")
    print("=" * 50 + "\n")

def run_assistant_cli() -> None:
    """Start and run the CLI application.

    This is the main entry point for the CLI. It initializes the interface,
    handles user input in a loop, and processes commands until the user exits.

    The function handles various exceptions and provides appropriate feedback
    to the user. It also manages the command history and screen clearing.

    Raises:
        KeyboardInterrupt: If the user presses Ctrl+C to exit.

    Example:
        To start the CLI, simply call:
        >>> run_assistant_cli()
    """
    display_initial_prompt()

    while True:
        try:
            user_input = prompt(">> ").strip()

            if not user_input:
                continue

            response = handle_input(user_input)

            if hasattr(response, "options") and hasattr(response, "prompt"):
                handle_menu_response(response)
            else:
                print("\n" + response.to_string() + "\n")

        except CommandExit:
            print("Exiting Datahouse CLI. Goodbye!")
            break
            
        except CommandClear:
            os.system('cls' if os.name == 'nt' else 'clear')
            datahouse_agent.clear_messages()
            display_initial_prompt()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Type '/help' for assistance or '/exit' to quit.")