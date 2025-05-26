import spacy
from spacy.tokens import Doc
from typing import List, Dict

# Load the English language model
nlp = spacy.load("en_core_web_lg")

class SpacyDocument:
    """A document processed using spaCy's natural language processing.
    
    This class provides an interface to various NLP capabilities using spaCy, including entity recognition and text summarization.
    """
    
    def __init__(self, text: str):
        """Initialize a new document for NLP processing.
        
        Args:
            text: The raw text to be processed.
        """
        self.doc = nlp(text)

    def get_entities(self) -> List[Dict[str, str]]:
        """Extract named entities from the document.
        
        Returns:
            A list of dictionaries, where each dictionary contains:
            - 'text': The entity text
            - 'label': The entity type (e.g., PERSON, ORG, GPE, etc.)
            
        Example:
            >>> doc = SpacyDocument("Apple is looking at buying U.K. startup for $1 billion")
            >>> doc.get_entities()
            [{'text': 'Apple', 'label': 'ORG'}, {'text': 'U.K.', 'label': 'GPE'}, ...]
        """
        return [{"text": ent.text, "label": ent.label_} for ent in self.doc.ents]

    def summarize(self) -> str:
        """Generate a summary of the document.
        
        Note:
            This uses spaCy's built-in summarization which is based on extractive summarization techniques. For more advanced summarization, consider using a transformer-based model.
            
        Returns:
            A string containing the document summary.
            
        Raises:
            NotImplementedError: If the spaCy model doesn't support summarization.
        """
        if not hasattr(self.doc, 'summary'):
            raise NotImplementedError("The current spaCy model doesn't support summarization.")
        return self.doc.summary()