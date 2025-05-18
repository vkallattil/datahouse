from typing import Callable
from modules.memory import JsonMemoryLog
from modules.commands import registry, CommandExit, CommandClear, MenuResponse, StringResponse, Response
import os
from prompt_toolkit.history import FileHistory
from prompt_toolkit import prompt

memory = JsonMemoryLog("logs/memory_log.json")
history = FileHistory("logs/command_log.txt")

def handle_input(user_input: str) -> Response:
    """
    Handle user input and save it to memory.
    Supports commands starting with '/' and regular input.
    """
    
    if user_input.startswith('/'):
        parts = user_input[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        response = registry.execute(command, args)
        if response is not None:
            memory.save(user_input, response.to_string())
            
            return response
        return StringResponse(f"Unknown command: {command}")
    
    response = StringResponse("Processed: " + user_input)
    memory.save(user_input, response.to_string())
    return response

def handle_menu(menu_response: MenuResponse):
    print(menu_response.prompt)

    for i, option in enumerate(menu_response.options):
        print(f"{i+1}. {option.label}")

    selected_option = input("Pick an option (or q to cancel): ")

    if selected_option == "q":
        return None
    
    if not selected_option.isdigit():
        print("Invalid option selected")
        return None
    
    selected_index = int(selected_option) - 1
    
    if selected_index < 0 or selected_index >= len(menu_response.options):
        print("Invalid option selected")
        return None

    menu_response.options[selected_index].action()

def display_initial_prompt():
    print("KTI Assistant (Phase 1 CLI):")
    print("Type '/help' for a list of commands.")

def run_assistant_cli():
    """
    Run the assistant CLI.
    """
    
    display_initial_prompt()
    
    while True:
        try:
            user_input = prompt(">> ", history=history)
            response = handle_input(user_input)

            if hasattr(response, "options") and hasattr(response, "prompt"):
                handle_menu(response)
            else:
                print(response.to_string())

        except CommandExit:
            break
        except CommandClear:
            os.system('cls' if os.name == 'nt' else 'clear')
            display_initial_prompt()
