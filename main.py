"""
main.py — Entry point for NyX, your CLI coding agent.

Run this file to start chatting:
    python main.py

Slash commands:
    /help    — Show available commands
    /exit    — Quit NyX
    /memory  — View stored memories
    /clear   — Clear conversation history
    /files   — List files in current directory
"""

import os
import sys

# Fix Windows terminal encoding so special characters print correctly
if sys.platform == "win32":
    os.system("")  # Enable ANSI escape codes on Windows
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import config
import memory
from agent import Agent
from tools.dir_tools import list_directory


# ─── Terminal Colors ────────────────────────────────────────────────
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
MAGENTA = "\033[35m"


def print_banner():
    """Show the startup banner."""
    banner = f"""
{CYAN}{BOLD}
    _   _        __  __
   | \\ | |_   _ \\ \\/ /
   |  \\| | | | | \\  /
   | |\\  | |_| | /  \\
   |_| \\_|\\__, |/_/\\_\\
          |___/
{RESET}
{DIM}    Your AI coding companion in the terminal{RESET}
{DIM}    v{config.AGENT_VERSION} | Model: {config.MODEL_NAME}{RESET}
{DIM}    Working directory: {os.getcwd()}{RESET}
{DIM}    Type /help for commands{RESET}
"""
    print(banner)


def print_help():
    """Show the help menu."""
    help_text = f"""
{YELLOW}{BOLD}NyX Commands:{RESET}
  {GREEN}/help{RESET}    — Show this help message
  {GREEN}/exit{RESET}    — Quit NyX
  {GREEN}/memory{RESET}  — View stored memories
  {GREEN}/forget{RESET}  — Clear all memories
  {GREEN}/clear{RESET}   — Clear conversation history (start fresh)
  {GREEN}/files{RESET}   — List files in current directory

{YELLOW}{BOLD}What NyX can do:{RESET}
  - Chat about coding questions
  - Create new files and scripts
  - Read and edit existing files
  - Run safe shell commands (python, pytest, pip, etc.)
  - Remember context between sessions

{DIM}Just type naturally — NyX figures out what tools to use.{RESET}
"""
    print(help_text)


def handle_slash_command(command, agent):
    """
    Handle slash commands. Returns True if a command was handled.
    """
    cmd = command.strip().lower()

    if cmd == "/help":
        print_help()
        return True

    elif cmd == "/exit" or cmd == "/quit":
        print(f"\n{CYAN}Goodbye! NyX will remember your context for next time.{RESET}\n")
        sys.exit(0)

    elif cmd == "/memory":
        print(f"\n{MAGENTA}{memory.get_summary()}{RESET}\n")
        return True

    elif cmd == "/forget":
        memory.clear()
        print(f"\n{YELLOW}Memory cleared.{RESET}\n")
        return True

    elif cmd == "/clear":
        agent.__init__()  # Re-initialize the agent
        print(f"\n{YELLOW}Conversation cleared. Starting fresh.{RESET}\n")
        return True

    elif cmd == "/files":
        print(f"\n{DIM}{list_directory('.')}{RESET}\n")
        return True

    return False


def main():
    """Main interactive loop."""

    # Check for API key early
    if not config.API_KEY:
        print(f"\n{YELLOW}[!] NVIDIA_API_KEY not found!{RESET}")
        print(f"Set it in a .env file or as an environment variable:")
        print(f"  1. Create a .env file with: NVIDIA_API_KEY=your-key-here")
        print(f"  2. Or run: {'set' if os.name == 'nt' else 'export'} NVIDIA_API_KEY=your-key-here\n")
        sys.exit(1)

    print_banner()

    # Load memory and show count
    mem_entries = memory.load()
    if mem_entries:
        print(f"{DIM}  >> Loaded {len(mem_entries)} memories from previous sessions{RESET}\n")

    # Create the agent
    agent = Agent()

    # Interactive loop
    while True:
        try:
            # Prompt for input
            user_input = input(f"{GREEN}{BOLD}You ▸ {RESET}").strip()

            # Skip empty input
            if not user_input:
                continue

            # Handle slash commands
            if user_input.startswith("/"):
                if handle_slash_command(user_input, agent):
                    continue
                else:
                    print(f"{YELLOW}Unknown command: {user_input}. Type /help for options.{RESET}\n")
                    continue

            # Send to agent
            print()  # Blank line before response
            response = agent.run(user_input)
            print(f"\n{CYAN}{BOLD}NyX ▸{RESET} {response}\n")

        except KeyboardInterrupt:
            print(f"\n\n{CYAN}Interrupted. Goodbye!{RESET}\n")
            sys.exit(0)

        except EOFError:
            print(f"\n\n{CYAN}Goodbye!{RESET}\n")
            sys.exit(0)

        except Exception as e:
            print(f"\n{YELLOW}[!] Error: {e}{RESET}\n")


if __name__ == "__main__":
    main()
