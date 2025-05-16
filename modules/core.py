from modules.memory import JsonMemoryLog
from modules.commands import registry, CommandExit, CommandClear
import os

PATH_TO_MEMORY_LOG = "logs/memory_log.json"

memory = JsonMemoryLog(PATH_TO_MEMORY_LOG)

def handle_input(user_input: str) -> str:
    """
    Handle user input and save it to memory.
    Supports commands starting with '/' and regular input.
    """
    
    if user_input.startswith('/'):
        # Split into command and args
        parts = user_input[1:].split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Execute command if it exists
        result = registry.execute(command, args)
        if result is not None:
            memory.save(user_input, result)
            return result
        
        return f"Unknown command: {command}"
    
    # Handle regular input
    response = "Processed: " + user_input
    memory.save(user_input, response)
    return response

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
            user_input = input(">> ")
            response = handle_input(user_input)
            print(response)
        except CommandExit:
            break
        except CommandClear:
            os.system('cls' if os.name == 'nt' else 'clear')
            display_initial_prompt()
