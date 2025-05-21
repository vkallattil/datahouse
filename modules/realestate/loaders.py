from llama_cloud_services import LlamaExtract
from utilities.config import LLAMA_CLOUD_API_KEY
from pydantic import BaseModel

extractor = LlamaExtract(api_key=LLAMA_CLOUD_API_KEY)

class Property(BaseModel):
    name: str
    vacancy_rate: float
    number_of_units: int
    rent_escalation_rate: float

class PropertyExtractor:
    def __init__(self):
        self.agent = extractor.create_agent(name="PropertyExtractor", data_schema=Property)

    def extract(self, file_path: str) -> Property:
        return self.agent.extract(file_path).data

    def __del__(self):
        extractor.delete_agent(self.agent.id)