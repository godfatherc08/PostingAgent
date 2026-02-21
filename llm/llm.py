import os
from langchain.chat_models import init_chat_model
import dotenv
import cohere
from langchain_cohere import ChatCohere

dotenv.load_dotenv()

COHEREKEY = os.getenv("COHERE_API_KEY")

model = init_chat_model(
    "command-xlarge-nightly",
    temperature=0.2,
    model_provider="cohere",
    timeout=120
)
