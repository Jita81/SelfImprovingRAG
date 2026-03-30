import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Allow importing the FastAPI app in tests without a real API key (LLM calls are mocked in focused tests).
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key-for-pytest") 