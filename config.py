"""
config.py — Central configuration for NyX agent.
All constants live here so they're easy to find and change.
"""

import os
from dotenv import load_dotenv

# Load .env file with support for global or local setups
# 1. Load from CWD first (project-specific overrides)
load_dotenv()

# 2. Fallback: Load from the NyX installation directory (where your working API key is)
agent_dir = os.path.dirname(os.path.abspath(__file__))
agent_env = os.path.join(agent_dir, ".env")
if os.path.exists(agent_env):
    load_dotenv(agent_env, override=False)

# 3. Fallback: Load from user home directory (~/.nyx/.env)
home_dir = os.path.expanduser("~")
home_env = os.path.join(home_dir, ".nyx", ".env")
if os.path.exists(home_env):
    load_dotenv(home_env, override=False)


# ─── NVIDIA API Settings ───────────────────────────────────────────
API_BASE_URL = "https://integrate.api.nvidia.com/v1"
API_KEY = os.getenv("NVIDIA_API_KEY", "")
MODEL_NAME = "openai/gpt-oss-120b"

# ─── LLM Parameters ───────────────────────────────────────────────
TEMPERATURE = 0.6
TOP_P = 0.9
MAX_TOKENS = 4096

# ─── Agent Settings ───────────────────────────────────────────────
MAX_TOOL_ROUNDS = 10          # Max consecutive tool calls before forcing a reply
MEMORY_FILE = ".nyx_memory.json"

# ─── Shell Safety ──────────────────────────────────────────────────
# Only these commands are allowed to run. Anything else is blocked.
ALLOWED_COMMANDS = [
    "python", "python3", "py",
    "pytest",
    "pip", "pip3",
    "ls", "dir",
    "cat", "type",
    "echo",
    "pwd",
    "cd",
    "head", "tail",
    "git",
    "npm", "npx", "node",
]

# ─── Directory Listing ─────────────────────────────────────────────
MAX_DIR_DEPTH = 3             # How deep to recurse when listing files
MAX_FILES_SHOWN = 100         # Cap on number of files shown

# ─── Agent Identity ────────────────────────────────────────────────
AGENT_NAME = "NyX"
AGENT_VERSION = "1.0.0"
