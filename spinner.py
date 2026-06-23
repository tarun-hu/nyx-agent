"""
spinner.py — Gen Z loading spinner for NyX.

Shows fun, rotating status messages while the LLM is thinking.
Inspired by Claude CLI's vibes-based loading messages.
"""

import sys
import time
import threading
import random
import itertools


# ─── Gen Z Status Messages ─────────────────────────────────────────
# These rotate while NyX is thinking. Keep it fun and fresh.
THINKING_MESSAGES = [
    "cooking up something fire 🔥",
    "hold my coffee, thinking... ☕",
    "brain cells assembling... 🧠",
    "loading vibes... ✨",
    "crafting the perfect response 💅",
    "neurons go brrrr 🤖",
    "consulting the algorithm 📡",
    "channeling big brain energy 🧬",
    "crunching the bytes 💾",
    "this is giving... genius 💡",
    "main character moment loading 🎬",
    "slay in progress... 💅✨",
    "no cap, thinking hard rn 🧠",
    "generating something bussin 🚀",
    "the AI is in its thinking era 💭",
    "yapping to the cloud ☁️",
    "lowkey processing rn 🔄",
    "highkey about to deliver 📦",
    "wait for it... it's gonna be good 👀",
    "NyX doing NyX things 🐍",
    "building the matrix... 🟢",
    "running on pure caffeine ☕⚡",
    "trust the process fr fr 🙏",
    "downloading more RAM... jk 🃏",
    "teaching electrons to dance 💃",
]

# Spinner animation frames
SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


class GenZSpinner:
    """
    An animated terminal spinner with Gen Z status messages.

    Usage:
        spinner = GenZSpinner()
        spinner.start()
        # ... do LLM call ...
        spinner.stop()

    Or as a context manager:
        with GenZSpinner():
            # ... do LLM call ...
    """

    def __init__(self, message_interval=2.5):
        """
        Args:
            message_interval: Seconds between message rotations.
        """
        self._stop_event = threading.Event()
        self._thread = None
        self._message_interval = message_interval
        self._lock = threading.Lock()

    def start(self):
        """Start the spinner animation in a background thread."""
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the spinner and clean up the line."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)
        # Clear the spinner line
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def _animate(self):
        """Animation loop — runs in a background thread."""
        frames = itertools.cycle(SPINNER_FRAMES)
        messages = list(THINKING_MESSAGES)
        random.shuffle(messages)
        msg_cycle = itertools.cycle(messages)

        current_msg = next(msg_cycle)
        last_switch = time.time()

        while not self._stop_event.is_set():
            # Rotate message every N seconds
            if time.time() - last_switch >= self._message_interval:
                current_msg = next(msg_cycle)
                last_switch = time.time()

            frame = next(frames)
            line = f"\r\033[35m  {frame} {current_msg}\033[0m"

            with self._lock:
                sys.stdout.write(line)
                sys.stdout.flush()

            self._stop_event.wait(0.08)  # ~12 FPS

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
