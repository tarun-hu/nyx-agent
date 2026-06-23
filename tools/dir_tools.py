"""
tools/dir_tools.py — Directory listing tool.
Lists files recursively with sensible depth and count limits.
"""

import os

import config


def list_directory(path=".", max_depth=None):
    """
    List files and folders in a directory tree.

    Args:
        path:      Directory to list (default: current directory)
        max_depth: How many levels deep to recurse (default: from config)

    Returns:
        A formatted string showing the directory tree.
    """
    if max_depth is None:
        max_depth = config.MAX_DIR_DEPTH

    # Make sure max_depth is an int
    max_depth = int(max_depth)

    cwd = os.getcwd()
    full_path = os.path.normpath(os.path.join(cwd, path))

    # Safety: don't go above the working directory
    if not full_path.startswith(cwd):
        return f"Path '{path}' is outside the working directory. Blocked for safety."

    if not os.path.exists(full_path):
        return f"Directory not found: {path}"

    if not os.path.isdir(full_path):
        return f"Not a directory: {path}"

    # Folders to skip (common noise)
    skip_dirs = {
        "__pycache__", ".git", "node_modules", ".venv", "venv",
        ".mypy_cache", ".pytest_cache", ".tox", "dist", "build",
        ".eggs", "*.egg-info",
    }

    lines = [f"Directory: {path}/"]
    file_count = 0

    def walk(dir_path, prefix, depth):
        nonlocal file_count

        if depth > max_depth or file_count >= config.MAX_FILES_SHOWN:
            return

        try:
            entries = sorted(os.listdir(dir_path))
        except PermissionError:
            lines.append(f"{prefix}[permission denied]")
            return

        # Separate dirs and files
        dirs = []
        files = []
        for name in entries:
            if name.startswith(".") and name != ".env.example":
                continue  # Skip hidden files (except .env.example)
            full = os.path.join(dir_path, name)
            if os.path.isdir(full):
                if name not in skip_dirs:
                    dirs.append(name)
            else:
                files.append(name)

        # Show files first, then directories
        for name in files:
            if file_count >= config.MAX_FILES_SHOWN:
                lines.append(f"{prefix}... (truncated)")
                return
            full = os.path.join(dir_path, name)
            size = os.path.getsize(full)
            size_str = _format_size(size)
            lines.append(f"{prefix}[F] {name}  ({size_str})")
            file_count += 1

        for name in dirs:
            lines.append(f"{prefix}[D] {name}/")
            walk(os.path.join(dir_path, name), prefix + "  ", depth + 1)

    walk(full_path, "  ", 0)

    if file_count == 0:
        lines.append("  (empty)")

    return "\n".join(lines)


def _format_size(size_bytes):
    """Format file size in a human-readable way."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def create_directory(path):
    """
    Create a new directory.
    All paths are relative to the current working directory for safety.
    """
    from tools.file_tools import _safe_path
    try:
        full_path = _safe_path(path)
        if os.path.exists(full_path):
            if os.path.isdir(full_path):
                return f"Directory already exists: {path}"
            else:
                return f"Path exists but is a file: {path}"
        os.makedirs(full_path, exist_ok=True)
        return f"Created directory: {path}"
    except Exception as e:
        return f"Error creating directory '{path}': {e}"
