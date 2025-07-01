import logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(name)s] %(message)s'
)
from interfaces.cli.core import run_assistant_cli

def main():
    run_assistant_cli()

if __name__ == "__main__":
    main()