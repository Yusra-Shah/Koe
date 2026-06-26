import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
CLERK_SECRET_KEY = os.getenv("CLERK_SECRET_KEY", "")
FIRESTORE_PROJECT = os.getenv("FIRESTORE_PROJECT", "")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "koe_analytics")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8081")
MODEL_BUCKET = os.getenv("MODEL_BUCKET", "")
TTS_LANGUAGE_CODES = os.getenv("TTS_LANGUAGE_CODES", "en-US,ur-PK").split(",")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8080"))
