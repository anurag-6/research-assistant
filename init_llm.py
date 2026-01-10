"""LLM initialization with configuration."""
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from config import settings

# Load environment variables from .env file
load_dotenv()

# Initialize LLM with settings from config
llm = ChatOpenAI(
    model=settings.openai_model,
    temperature=settings.openai_temperature
)