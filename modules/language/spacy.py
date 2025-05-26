import spacy
from spacy.tokens import Doc
from typing import List, Dict

# Load the English language model
nlp = spacy.load("en_core_web_lg")

class SpacyDocument:
    def __init__(self, text: str):
        self.doc = nlp(text)

    def get_entities(self) -> List[Dict[str, str]]:
        """
        Get the entities from the document.
        """

        return [{"text": ent.text, "label": ent.label_} for ent in self.doc.ents]

    def summarize(self) -> str:
        """
        Summarize the document.
        """

        return self.doc.summary()