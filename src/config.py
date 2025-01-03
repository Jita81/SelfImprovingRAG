from langchain_openai import ChatOpenAI
import os

def get_llm():
    """Get the LLM instance configured from environment variables."""
    if "OPENAI_API_KEY" not in os.environ:
        raise EnvironmentError("OPENAI_API_KEY environment variable is not set")
        
    return ChatOpenAI(
        model="gpt-4-1106-preview",  # This is GPT-4 Turbo
        temperature=0
    ) 