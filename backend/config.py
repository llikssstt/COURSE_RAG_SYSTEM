from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
CHROMA_DIR = DATA_DIR / "chroma"
MODEL_CACHE_DIR = DATA_DIR / "models"
BGE_LOCAL_MODEL_DIR = MODEL_CACHE_DIR / "bge-small-zh-v1.5"
DB_PATH = DATA_DIR / "app.db"

for path in (DATA_DIR, UPLOAD_DIR, CHROMA_DIR, MODEL_CACHE_DIR):
    path.mkdir(parents=True, exist_ok=True)

# Keep model/cache files inside the project workspace on Windows.
os.environ.setdefault("HF_HOME", str(DATA_DIR / "hf_home"))
os.environ.setdefault("HF_HUB_CACHE", str(DATA_DIR / "hf_cache"))


# LLM settings. Set MOCK_MODE=true only for offline debugging.
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

OPENAI_COMPATIBLE_BASE_URL = os.getenv(
    "OPENAI_COMPATIBLE_BASE_URL", "https://api.deepseek.com"
)
OPENAI_COMPATIBLE_API_KEY = os.getenv("OPENAI_COMPATIBLE_API_KEY") or os.getenv("DEEPSEEK_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "deepseek-chat")

# Embedding settings. Default follows the all-in-rag style: local Chinese BGE.
# Set EMBEDDING_PROVIDER=mock when you need a fully offline fallback.
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "bge")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "512"))
EMBEDDING_FALLBACK_TO_MOCK = os.getenv("EMBEDDING_FALLBACK_TO_MOCK", "true").lower() == "true"

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "700"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
