def read_notes() -> str:
    with open("notes.txt", "r") as f:
        return f.read()

def write_notes(content: str) -> None:
    with open("notes.txt", "w") as f:
        f.write(content)
  