"""
memory.py — Simple JSON-based memory for NyX.
Stores useful facts, recent tasks, and project context between sessions.
The memory file lives in the current working directory.
"""

import json
import os
from datetime import datetime

import config


def _memory_path():
    """
    Return the full path to the memory file.
    Searches upwards from CWD for project root indicators (.git, .env, or memory file).
    If none found, defaults to global user home directory ~/.nyx/.
    """
    current = os.path.abspath(os.getcwd())
    while True:
        if any(os.path.exists(os.path.join(current, marker)) for marker in [".git", ".env", config.MEMORY_FILE]):
            return os.path.join(current, config.MEMORY_FILE)
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    # Fallback to user home directory for global memory
    home_dir = os.path.expanduser("~")
    global_dir = os.path.join(home_dir, ".nyx")
    try:
        os.makedirs(global_dir, exist_ok=True)
        return os.path.join(global_dir, config.MEMORY_FILE)
    except Exception:
        # Final fallback to CWD if home directory is read-only or not accessible
        return os.path.join(os.getcwd(), config.MEMORY_FILE)


def load():
    """
    Load memory from disk. Returns a list of memory entries.
    Each entry is a dict: {"text": "...", "timestamp": "..."}
    If the file doesn't exist yet, returns an empty list.
    """
    path = _memory_path()
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Make sure it's a list
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save(entries):
    """Save the full list of memory entries to disk."""
    path = _memory_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"  [Warning] Could not save memory: {e}")


def add(text):
    """Add a new fact or note to memory. Avoids duplicate entries."""
    text = text.strip()
    if not text:
        return "Memory text cannot be empty."

    entries = load()
    # Check for duplicate text (case-insensitive and ignoring outer spaces)
    for entry in entries:
        if entry.get("text", "").strip().lower() == text.lower():
            # Update the timestamp on the existing entry
            entry["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save(entries)
            return f"Updated existing memory: {text}"

    entries.append({
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })
    save(entries)
    return f"Saved to memory: {text}"


def clear():
    """Clear all memory entries."""
    save([])
    return "Memory cleared."


def get_summary():
    """Return a formatted string of all memory entries (for display)."""
    entries = load()
    if not entries:
        return "No memories stored yet."

    lines = []
    for i, entry in enumerate(entries, 1):
        ts = entry.get("timestamp", "?")
        text = entry.get("text", "")
        lines.append(f"  {i}. [{ts}] {text}")

    return f"Memory ({len(entries)} entries):\n" + "\n".join(lines)


def get_context_for_llm():
    """
    Return memory as a compact string to include in the LLM prompt.
    This helps the agent remember things from past sessions.
    """
    entries = load()
    if not entries:
        return "No stored memories."

    lines = [f"- {e['text']}" for e in entries[-20:]]  # Last 20 entries max
    return "Stored memories:\n" + "\n".join(lines)
