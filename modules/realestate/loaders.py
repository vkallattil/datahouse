from llama_cloud_services import LlamaExtract
from utilities.config import LLAMA_CLOUD_API_KEY
from modules.realestate.schemas import RentalProperty

extractor = LlamaExtract(api_key=LLAMA_CLOUD_API_KEY)

try:
    agent = extractor.get_agent("PropertyExtractor")
except Exception as e:
    print(f"Error finding agent, creating new one: {e}")
    agent = extractor.create_agent(name="PropertyExtractor", data_schema=RentalProperty)

def extract_property(file_path: str) -> RentalProperty:
    raw_data = agent.extract(file_path)
    return RentalProperty(**raw_data.data)