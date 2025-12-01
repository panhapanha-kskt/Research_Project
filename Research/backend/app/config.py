from dotenv import load_dotenv
import os
from pathlib import Path

# -------------------------------------------------------------------
# Load environment variables from the project's .env file
# Works for:
# - Normal python execution
# - Virtualenv
# - Docker containers
# - Uvicorn reload mode
# -------------------------------------------------------------------

# Determine BASE_DIR = backend/app/
BASE_DIR = Path(__file__).resolve().parent

# The .env file is in: backend/.env
ENV_PATH = BASE_DIR.parent / ".env"

# Load the .env file
load_dotenv(dotenv_path=ENV_PATH)

# -------------------------------------------------------------------
# Configuration values
# -------------------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# IMPORTANT: Remove "changeme" fallback so you immediately see errors
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise RuntimeError("❌ API_KEY not found in .env! Backend cannot start.")

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise RuntimeError("❌ FERNET_KEY missing in .env! Generate a key first.")

RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
RATE_LIMIT_PERIOD = int(os.getenv("RATE_LIMIT_PERIOD", "60"))

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# -------------------------------------------------------------------
# Debug print (optional – remove in production)
# -------------------------------------------------------------------
# print("Loaded .env from:", ENV_PATH)
# print("API_KEY:", API_KEY)
