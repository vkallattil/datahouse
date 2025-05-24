from llama_cloud_services import LlamaExtract
from utilities.config.env import LLAMA_CLOUD_API_KEY
from modules.realestate.schemas import Property

extractor = LlamaExtract(api_key=LLAMA_CLOUD_API_KEY)

try:
    agent = extractor.get_agent("PropertyExtractor")
except Exception as e:
    print(f"Error finding agent, creating new one: {e}")
    agent = extractor.create_agent(name="PropertyExtractor", data_schema=Property)

def extract_property(file_path: str) -> Property:
    raw_data = agent.extract(file_path)
    return Property(**raw_data.data)