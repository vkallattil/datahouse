from interfaces.cli.core import run_assistant_cli
from modules.realestate.loaders import PropertyExtractor

def main():
    extractor = PropertyExtractor()
    property = extractor.extract("rental_pro_forma.pdf")
    print(property)
    # run_assistant_cli()

if __name__ == "__main__":
    main()