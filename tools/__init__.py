"""
tools/__init__.py — Central tool registry.
Maps tool names to their handler functions so the agent can look them up.
"""

from tools.file_tools import read_file, create_file, overwrite_file, append_file, edit_file
from tools.dir_tools import list_directory, create_directory
from tools.shell_tools import run_command

import memory


def _save_memory_wrapper(**kwargs):
    """Robust wrapper for memory saving to prevent TypeError on parameter mismatch."""
    text = kwargs.get("text") or kwargs.get("fact") or kwargs.get("content") or kwargs.get("memory")
    if not text:
        if kwargs:
            # If the model used a different parameter name, take the first value
            text = next(iter(kwargs.values()))
    if not text:
        return "Error: No text parameter provided to save_memory."
    return memory.add(str(text))


def _read_memory_wrapper(*args, **kwargs):
    """Robust wrapper for memory reading to prevent TypeError on parameter mismatch."""
    return memory.get_context_for_llm()


# ─── Tool Registry ─────────────────────────────────────────────────
# Each key is the tool name the LLM will use.
# Each value is the function that handles that tool.
TOOL_MAP = {
    "read_file": read_file,
    "create_file": create_file,
    "overwrite_file": overwrite_file,
    "append_file": append_file,
    "edit_file": edit_file,
    "list_directory": list_directory,
    "create_directory": create_directory,
    "run_command": run_command,
    "save_memory": _save_memory_wrapper,
    "read_memory": _read_memory_wrapper,
}


def execute_tool(tool_name, params):
    """
    Look up a tool by name and run it with the given params.

    Args:
        tool_name: String name of the tool (e.g. "read_file")
        params:    Dict of parameters to pass to the tool function

    Returns:
        String result of the tool execution.
    """
    if tool_name not in TOOL_MAP:
        return f"Unknown tool: '{tool_name}'. Available: {', '.join(TOOL_MAP.keys())}"

    handler = TOOL_MAP[tool_name]

    try:
        # If params is a dict, unpack it as keyword arguments
        if isinstance(params, dict) and params:
            result = handler(**params)
        else:
            result = handler()
        return str(result)
    except TypeError as e:
        return f"Tool '{tool_name}' parameter error: {e}"
    except Exception as e:
        return f"Tool '{tool_name}' failed: {e}"
