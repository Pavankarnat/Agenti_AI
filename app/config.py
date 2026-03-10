"""
Configuration module for the Agentic AI application.
Loads environment variables and sets up API keys and settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============== API KEYS ===============
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# =============== LLM CONFIGURATION ===============
# Available models: "gpt-4-turbo", "claude-opus", "gemini-pro"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2000"))

# =============== OBSERVABILITY ===============
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "agentic-ai-research")
LANGFUSE_API_KEY = os.getenv("LANGFUSE_API_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
USE_LANGSMITH = os.getenv("USE_LANGSMITH", "false").lower() == "true"
USE_LANGFUSE = os.getenv("USE_LANGFUSE", "false").lower() == "true"

# =============== APPLICATION SETTINGS ===============
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
MAX_URL_EXTRACTIONS = int(os.getenv("MAX_URL_EXTRACTIONS", "3"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))

# =============== AGENT CONFIGURATION ===============
ENABLE_MULTI_AGENT = os.getenv("ENABLE_MULTI_AGENT", "true").lower() == "true"
AGENT_VERBOSE = os.getenv("AGENT_VERBOSE", "true").lower() == "true"
