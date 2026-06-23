# NyX — Your AI Coding Companion in the Terminal

NyX is a beginner-friendly CLI coding agent. Think of it as a minimal, Claude CLI-style coding assistant — built in plain Python for learning purposes.

## What NyX Can Do

- 💬 **Chat** about coding questions in the terminal
- 📄 **Create files** — ask NyX to write a new script for you
- ✏️ **Edit files** — NyX can modify existing code with find-and-replace
- 📂 **Read files** — NyX reads your project files to understand context
- 🖥️ **Run commands** — safely execute Python, pytest, pip, and other allowlisted commands
- 🧠 **Remember context** — NyX stores useful facts between sessions in a local JSON file

## Quick Start

### 1. Get an API Key

Go to [NVIDIA Build](https://build.nvidia.com/openai/gpt-oss-120b) and get a free API key.

### 2. Setup

```bash
# Clone or navigate to the project
cd nyx-agent

# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# Then edit .env and paste your NVIDIA API key
```

### 3. Run

```bash
python main.py
```

That's it! You'll see the NyX banner and can start chatting.

---

## 🌍 Run NyX from Any Directory (Global Setup)

You can run `nyx` in any project directory on Windows:

1. **Keep your `.env` key in the `nyx-agent` folder**:
   NyX is configured to load your API key from its installation directory as a fallback, meaning you only need to define the key once in `d:\1 for all\bootcamp\nyx-agent\.env`.

2. **Add the NyX folder to your System PATH**:
   - Press the **Windows Key** and type `env`.
   - Click on **Edit the system environment variables**.
   - Click on the **Environment Variables...** button.
   - Under **User variables** (or **System variables**), find the variable named `Path` and double-click it.
   - Click **New** and add the path to the `nyx-agent` folder:
     `d:\1 for all\bootcamp\nyx-agent`
   - Click **OK** to save and close all dialogs.

3. **Start NyX anywhere**:
   Open a **new** PowerShell or Command Prompt terminal in **any project folder** on your computer and run:
   ```cmd
   nyx
   ```
   Now, NyX will start up and operate in that target directory (creating files, reading files, running commands, and saving memory local to that folder)!

---

## Commands

| Command    | What it does                        |
|------------|-------------------------------------|
| `/help`    | Show available commands             |
| `/exit`    | Quit NyX                            |
| `/memory`  | View stored memories                |
| `/forget`  | Clear all memories                  |
| `/clear`   | Clear conversation (start fresh)    |
| `/files`   | List files in current directory     |

## Example Session

```
You ▸ Create a Python file called hello.py that prints "Hello, World!"

  🔧 Using tool: create_file
  ✓ Result: Created hello.py (3 lines)

NyX ▸ Done! I created hello.py for you. Here's what's in it:

  print("Hello, World!")

  You can run it with: python hello.py

You ▸ Now add a function that greets someone by name

  🔧 Using tool: read_file
  🔧 Using tool: edit_file
  ✓ Result: Edited hello.py: replaced 1 occurrence(s)

NyX ▸ Updated! I added a greet() function. The file now looks like this...

You ▸ Run it

  🔧 Using tool: run_command
  ✓ Result: Hello, World!

NyX ▸ It ran successfully and printed "Hello, World!"
```

## Project Structure

```
nyx-agent/
├── main.py              # CLI entry point and interactive loop
├── agent.py             # The agent loop (think → tool → respond)
├── llm_client.py        # NVIDIA API client (OpenAI-compatible)
├── memory.py            # JSON-based persistent memory
├── prompts.py           # System prompt and tool definitions
├── config.py            # Constants and settings
├── tools/
│   ├── __init__.py      # Tool registry
│   ├── file_tools.py    # Read, create, edit, append files
│   ├── dir_tools.py     # List directory contents
│   └── shell_tools.py   # Safe shell command execution
├── requirements.txt
├── .env.example
└── README.md
```

## How It Works (for learners)

NyX uses a simple **agent loop**:

1. You type a message
2. NyX sends it to the LLM (NVIDIA's gpt-oss-120b) along with tool descriptions
3. The LLM either:
   - **Responds directly** → NyX shows you the response
   - **Calls a tool** (as a JSON object) → NyX executes it and feeds the result back
4. Steps 2-3 repeat until the LLM gives a final text answer
5. Memory is saved for future sessions

The tool calling is done through a simple JSON schema — no complex frameworks needed.

## Safety Features

- **Shell allowlist** — Only safe commands like `python`, `pytest`, `pip`, `ls`, `cat` can run
- **Path sandboxing** — File operations are restricted to your working directory
- **Command timeout** — Shell commands timeout after 30 seconds
- **Conversation trimming** — History is trimmed to keep context manageable

## Tech Stack

- **Python 3.8+** — standard library for most things
- **openai** — to talk to the NVIDIA API (OpenAI-compatible)
- **python-dotenv** — to load the API key from `.env`

That's it. Two dependencies. No frameworks, no databases, no Docker.

## License

MIT — do whatever you want with it. Built for learning.
