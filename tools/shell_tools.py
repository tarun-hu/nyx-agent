"""
tools/shell_tools.py — Safe shell command execution.
Only allows commands from a small allowlist defined in config.py.
"""

import subprocess
import shlex
import platform

import config


def run_command(command):
    """
    Run a shell command if it's in the allowlist.

    Args:
        command: The full command string (e.g. "python script.py")

    Returns:
        The command output (stdout + stderr) or an error message.
    """
    command = command.strip()
    if not command:
        return "No command provided."

    # Check if the command starts with an allowed program
    if not _is_allowed(command):
        allowed = ", ".join(config.ALLOWED_COMMANDS)
        return (
            f"Command blocked for safety: '{command}'\n"
            f"Allowed commands: {allowed}\n"
            f"NyX only runs commands from this allowlist."
        )

    try:
        # Use shell=True on Windows for better compatibility
        is_windows = platform.system() == "Windows"

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,  # 30-second timeout to prevent hanging
            cwd=None,    # Run in the current working directory
        )

        output_parts = []
        if result.stdout:
            output_parts.append(result.stdout)
        if result.stderr:
            output_parts.append(f"[stderr] {result.stderr}")

        output = "\n".join(output_parts).strip()
        if not output:
            output = "(no output)"

        # Add return code info if the command failed
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"

        return output

    except subprocess.TimeoutExpired:
        return f"Command timed out after 30 seconds: '{command}'"
    except Exception as e:
        return f"Error running command: {e}"


def _is_allowed(command):
    """
    Check if a command starts with one of the allowed command prefixes.
    Compares against config.ALLOWED_COMMANDS.
    """
    cmd_lower = command.lower().strip()

    for allowed in config.ALLOWED_COMMANDS:
        # Check if the command starts with the allowed prefix
        # "python" should match "python script.py" but not "pythonstuff"
        if cmd_lower == allowed or cmd_lower.startswith(allowed + " "):
            return True

    return False
