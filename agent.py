"""
agent.py — The core agent loop for NyX.

This is the brain of the agent. It:
1. Sends the user's message to the LLM
2. Checks if the LLM wants to use a tool
3. Executes the tool and feeds the result back
4. Repeats until the LLM gives a final text response
"""

import json
import re

import config
import llm_client
import prompts
from spinner import GenZSpinner
from tools import execute_tool


class Agent:
    def __init__(self):
        """Initialize the agent with an LLM client and conversation history."""
        self.client = llm_client.create_client()
        self.messages = []
        self._reset_system_prompt()

    def _reset_system_prompt(self):
        """Rebuild the system prompt (picks up fresh memory context)."""
        system_prompt = prompts.build_system_prompt()

        # If there's already a system message, replace it
        if self.messages and self.messages[0]["role"] == "system":
            self.messages[0]["content"] = system_prompt
        else:
            self.messages.insert(0, {"role": "system", "content": system_prompt})

    def run(self, user_message):
        """
        Process a user message through the agent loop.

        The loop:
        1. Add the user message to conversation history
        2. Call the LLM
        3. If the LLM returns a tool call → execute it → feed result back → repeat
        4. If the LLM returns normal text → return it to the user

        Returns:
            The final text response from the agent.
        """
        # Add user message
        self.messages.append({"role": "user", "content": user_message})

        # Agent loop: keep going until we get a final text response
        for round_num in range(config.MAX_TOOL_ROUNDS):
            # Refresh system prompt to include latest memory (picks up changes dynamically)
            self._reset_system_prompt()

            # Call the LLM (with Gen Z spinner ✨)
            with GenZSpinner():
                response = llm_client.chat(self.client, self.messages)
            content = response["content"]

            # Show reasoning if present (dimmed for readability)
            if response["reasoning"]:
                print(f"\033[2m  [thinking...]\033[0m")

            # Try to parse a tool call from the response
            tool_call = self._parse_tool_call(content)

            if tool_call:
                tool_name = tool_call["tool"]
                params = tool_call.get("params", {})

                
                print(f"\033[36m  >> Using tool: {tool_name}\033[0m")
                if params:
                    # Show compact params (truncate long content)
                    display_params = {}
                    for k, v in params.items():
                        if isinstance(v, str) and len(v) > 80:
                            display_params[k] = v[:80] + "..."
                        else:
                            display_params[k] = v
                    print(f"\033[2m     {display_params}\033[0m")

                # Execute the tool (ask for review/approval if it's a modifying or shell tool)
                modifying_tools = [
                    "create_file", "overwrite_file", "append_file", 
                    "edit_file", "create_directory", "run_command"
                ]
                if tool_name in modifying_tools:
                    try:
                        confirm = input(
                            f"\033[33m\033[1m  [Review Required] Allow executing tool '{tool_name}'? (yes/no) [yes]: \033[0m"
                        ).strip().lower()
                    except (KeyboardInterrupt, EOFError):
                        confirm = "no"

                    if confirm not in ["", "y", "yes"]:
                        print(f"\033[31m  [cancelled] Execution of tool '{tool_name}' declined by user.\033[0m")
                        result = "Tool execution was declined/cancelled by the user."
                    else:
                        result = execute_tool(tool_name, params)
                else:
                    result = execute_tool(tool_name, params)

                # Show a brief result preview
                result_preview = result[:150] + "..." if len(result) > 150 else result
                print(f"\033[32m  [ok] Result: {result_preview}\033[0m")

                # Add the assistant's tool call and the result to the conversation
                self.messages.append({"role": "assistant", "content": content})
                self.messages.append({
                    "role": "user",
                    "content": f"[TOOL RESULT for {tool_name}]\n{result}\n[/TOOL RESULT]\n\nNow continue. If you need another tool, call it. Otherwise, give your final response to the user."
                })

            else:
                # No tool call — this is the final response
                self.messages.append({"role": "assistant", "content": content})

                # Trim conversation history if it gets too long
                self._trim_history()

                return content

        # If we hit the max rounds, force a response
        return "I've used too many tools in a row. Here's what I've done so far — please check the results above and let me know how to proceed."

    def _parse_tool_call(self, text):
        """
        Try to extract a tool call JSON from the LLM's response.

        The LLM is instructed to respond with ONLY a JSON object when using a tool.
        This function handles several formats:
        - Plain JSON: {"tool": "...", "params": {...}}
        - JSON in code blocks: ```json\n{...}\n```
        - JSON with some surrounding text (we try to extract it)

        Returns:
            A dict with "tool" and "params" keys, or None if not a tool call.
        """
        text = text.strip()

        # Strategy 1: Try to parse the entire response as JSON
        parsed = self._try_parse_json(text)
        if parsed and "tool" in parsed:
            return parsed

        # Strategy 2: Look for JSON in a code block
        code_block_match = re.search(r"```(?:json)?\s*\n?(\{.*?\})\s*\n?```", text, re.DOTALL)
        if code_block_match:
            parsed = self._try_parse_json(code_block_match.group(1))
            if parsed and "tool" in parsed:
                return parsed

        # Strategy 3: Find the first { ... } in the text
        brace_match = re.search(r"\{.*\}", text, re.DOTALL)
        if brace_match:
            parsed = self._try_parse_json(brace_match.group(0))
            if parsed and "tool" in parsed:
                return parsed

        # No tool call found
        return None

    def _try_parse_json(self, text):
        """Safely try to parse a string as JSON. Returns dict or None."""
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, TypeError):
            pass
        return None

    def _trim_history(self):
        """
        Keep conversation history manageable.
        Keeps the system prompt + the last 40 messages.
        """
        max_messages = 42  # system + 40 conversation turns + buffer

        if len(self.messages) > max_messages:
            # Keep system prompt (index 0) and last N messages
            self.messages = [self.messages[0]] + self.messages[-(max_messages - 1):]

    def btw(self, question):
        """
        Handle a /btw side-conversation.

        Sends the question to the LLM with minimal context (just the system prompt)
        and does NOT add the exchange to the main conversation history.

        Args:
            question: The user's side-question.

        Returns:
            The LLM's response to the side question.
        """
        side_messages = [
            {"role": "system", "content": prompts.build_system_prompt()},
            {"role": "user", "content": question},
        ]

        with GenZSpinner():
            response = llm_client.chat(self.client, side_messages)

        return response["content"]
