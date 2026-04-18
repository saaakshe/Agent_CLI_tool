from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# LLM CONFIG (Ollama)
# =========================================================
MODEL_NAME = os.getenv("MODEL_NAME", "llama3")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL.rstrip('/')}/api/chat"
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT", "90"))

# =========================================================
# DAEMON CONFIG
# =========================================================
DAEMON_HOST = os.getenv("DAEMON_HOST", "127.0.0.1")
DAEMON_PORT = int(os.getenv("DAEMON_PORT", 9800))
DAEMON_URL = f"http://{DAEMON_HOST}:{DAEMON_PORT}"
DAEMON_START_TIMEOUT = float(os.getenv("DAEMON_START_TIMEOUT", "12"))

# =========================================================
# MEMORY CONFIG
# =========================================================
SHORT_TERM_LIMIT = int(os.getenv("SHORT_TERM_LIMIT", 10))
TOP_K_MEMORY = int(os.getenv("TOP_K_MEMORY", 5))
MEMORY_FILE_PATH = Path(os.getenv("MEMORY_FILE_PATH", DATA_DIR / "memory.json")).resolve()
HISTORY_FILE_PATH = Path(os.getenv("HISTORY_FILE_PATH", DATA_DIR / "history.json")).resolve()

# =========================================================
# DAEMON LIFECYCLE
# =========================================================
PID_FILE_PATH = Path(os.getenv("PID_FILE_PATH", DATA_DIR / "agent.pid")).resolve()

# =========================================================
# APP SETTINGS
# =========================================================
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", BASE_DIR)).resolve()
