"""
tools/file_tools.py — File reading, creation, and editing tools.
All paths are relative to the current working directory for safety.
"""

import os


def _safe_path(path):
    """
    Resolve a file path safely. Prevents escaping the working directory.
    Returns the absolute path if it's within cwd, or raises an error.
    """
    cwd = os.getcwd()
    # Resolve to absolute path based on cwd
    full_path = os.path.normpath(os.path.join(cwd, path))

    # Security check: make sure the path is inside the working directory
    if not full_path.startswith(cwd):
        raise ValueError(f"Path '{path}' is outside the working directory. Blocked for safety.")

    return full_path


def read_file(path):
    """Read and return the contents of a file."""
    full_path = _safe_path(path)

    if not os.path.exists(full_path):
        return f"File not found: {path}"

    if not os.path.isfile(full_path):
        return f"Not a file: {path}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Show line numbers for easier reference
        lines = content.split("\n")
        numbered = [f"{i+1:4d} | {line}" for i, line in enumerate(lines)]
        return f"Contents of {path} ({len(lines)} lines):\n" + "\n".join(numbered)

    except UnicodeDecodeError:
        return f"Cannot read {path}: file appears to be binary."
    except IOError as e:
        return f"Error reading {path}: {e}"


def create_file(path, content):
    """
    Create a new file with the given content.
    Will NOT overwrite an existing file — use overwrite_file for that.
    """
    full_path = _safe_path(path)

    if os.path.exists(full_path):
        return f"File already exists: {path}. Use overwrite_file to replace it."

    # Create parent directories if they don't exist
    parent_dir = os.path.dirname(full_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        lines = content.count("\n") + 1
        return f"Created {path} ({lines} lines)"
    except IOError as e:
        return f"Error creating {path}: {e}"


def overwrite_file(path, content):
    """
    Overwrite an existing file with new content.
    Also works for creating new files.
    """
    full_path = _safe_path(path)

    # Create parent directories if they don't exist
    parent_dir = os.path.dirname(full_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        lines = content.count("\n") + 1
        return f"Wrote {path} ({lines} lines)"
    except IOError as e:
        return f"Error writing {path}: {e}"


def append_file(path, content):
    """Append content to the end of an existing file."""
    full_path = _safe_path(path)

    if not os.path.exists(full_path):
        return f"File not found: {path}. Use create_file to make a new one."

    try:
        with open(full_path, "a", encoding="utf-8") as f:
            f.write(content)
        return f"Appended to {path}"
    except IOError as e:
        return f"Error appending to {path}: {e}"


def edit_file(path, find_text, replace_text):
    """
    Edit a file by finding a specific text and replacing it.
    This is a simple find-and-replace approach.

    Args:
        path:         Path to the file
        find_text:    The exact text to find in the file
        replace_text: The text to replace it with
    """
    full_path = _safe_path(path)

    if not os.path.exists(full_path):
        return f"File not found: {path}"

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            original = f.read()

        if find_text not in original:
            return (
                f"Could not find the specified text in {path}.\n"
                f"Searched for:\n---\n{find_text}\n---\n"
                f"Make sure the text matches exactly (including whitespace)."
            )

        # Count occurrences
        count = original.count(find_text)

        # Do the replacement
        updated = original.replace(find_text, replace_text)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(updated)

        return f"Edited {path}: replaced {count} occurrence(s)"

    except UnicodeDecodeError:
        return f"Cannot edit {path}: file appears to be binary."
    except IOError as e:
        return f"Error editing {path}: {e}"
