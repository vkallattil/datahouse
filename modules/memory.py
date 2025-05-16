# modules/memory_interface.py
from abc import ABC, abstractmethod
from datetime import datetime
import os
import json
from typing import List, Dict, TypedDict, get_type_hints
from utilities.logger import logger

class MemoryLog(ABC):
    @abstractmethod
    def save(self, user_input: str, assistant_response: str): ...

    @abstractmethod
    def _read_log(self) -> List[Dict]: ...

    @abstractmethod
    def _write_log(self, log: List[Dict]) -> None: ...

class MemoryLogEntry(TypedDict):
    timestamp: str
    user_input: str
    assistant_response: str

def validate_memory_log_entry(entry: dict) -> bool:
    """
    Validate that a dictionary matches the MemoryLogEntry structure.
    
    Args:
        entry (dict): Dictionary to validate
        
    Returns:
        bool: True if valid, raises TypeError if invalid
    """
    required_fields = get_type_hints(MemoryLogEntry)
    
    # Check all required fields exist and are correct type
    for field, expected_type in required_fields.items():
        if field not in entry:
            raise TypeError(f"Missing required field: {field}")
        if not isinstance(entry[field], str):
            raise TypeError(f"Field {field} must be a string")
    
    return True

class JsonMemoryLog(MemoryLog):
    def __init__(self, path: str):
        """
        Initialize the memory log.
        
        Args:
            path (str): The path to the memory log file
        """

        self.path = path
        self._initialize_log()

    def _initialize_log(self) -> None:
        """
        Validate provided log file path exists - if not, create an empty file. Clear the log (this initializes the file with an empty JSON array).
        """
        
        if not os.path.exists(self.path):
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w') as f:
                json.dump([], f)

        self._clear_log()

    def _clear_log(self) -> None:
        with open(self.path, 'w') as f:
            json.dump([], f)
        
    def _read_log(self) -> List[Dict]:
        """
        Read the existing log from the JSON file.
        
        Returns:
            List[Dict]: The log data read from the file
        """

        with open(self.path, "r") as f:
            return json.load(f)
                    
    def _write_log(self, log: List[MemoryLogEntry]) -> None:
        """
        Write the log to the JSON file.
        
        Args:
            log (List[Dict]): The log data to write
        """

        with open(self.path, "w") as f:
            json.dump(log, f, indent=2)

    def _append_entry(self, entry: MemoryLogEntry) -> None:
        """
        Append an entry to the existing log file while maintaining valid JSON array structure.
        
        Args:
            entry (MemoryLogEntry): The log entry to append
            
        Raises:
            TypeError: If entry doesn't match MemoryLogEntry structure
        """
        validate_memory_log_entry(entry)
        log = self._read_log()
        log.append(entry)
        self._write_log(log)

    def save(self, user_input: str, assistant_response: str):
        """
        Save the user input and assistant response to the memory log.
        
        Args:
            user_input (str): The user input to save
            assistant_response (str): The assistant response to save
        """

        self._append_entry(MemoryLogEntry(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            assistant_response=assistant_response
        ))
