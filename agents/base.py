"""Base agent class for System Prompts for Humanity agents.

Supports two backends:
  - "ollama"    (default) — local models via Ollama's OpenAI-compatible API
  - "anthropic" — Claude models via Anthropic API (requires ANTHROPIC_API_KEY)

Set SPFH_BACKEND=anthropic to switch, or pass --backend on the CLI.
"""

import os
import sys
from pathlib import Path

# Ensure stdout handles unicode on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from openai import OpenAI


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "system-prompts"

# Defaults per backend
DEFAULTS = {
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "llama3.2:latest",
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "api_key": os.environ.get("ANTHROPIC_API_KEY", ""),
        "model": "claude-sonnet-4-6",
    },
}


def load_system_prompt(filename: str) -> str:
    """Load a system prompt .txt file from the system-prompts directory."""
    path = PROMPTS_DIR / filename
    return path.read_text(encoding="utf-8")


def get_backend() -> str:
    return os.environ.get("SPFH_BACKEND", "ollama").lower()


class Agent:
    """A conversational agent backed by a system prompt framework."""

    def __init__(
        self,
        name: str,
        system_prompt_file: str,
        model: str | None = None,
        preamble: str = "",
        backend: str | None = None,
    ):
        self.name = name
        self.backend = backend or get_backend()
        cfg = DEFAULTS[self.backend]
        self.model = model or cfg["model"]

        self.client = OpenAI(
            base_url=cfg["base_url"],
            api_key=cfg["api_key"],
        )

        self.system_prompt = load_system_prompt(system_prompt_file)
        if preamble:
            self.system_prompt = preamble + "\n\n" + self.system_prompt
        self.messages: list[dict] = []

    def send(self, user_message: str) -> str:
        """Send a message and get a response, maintaining conversation history."""
        self.messages.append({"role": "user", "content": user_message})

        all_messages = [
            {"role": "system", "content": self.system_prompt},
            *self.messages,
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=all_messages,
            max_tokens=4096,
        )
        assistant_text = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    def reset(self):
        """Clear conversation history."""
        self.messages = []

    def run_interactive(self):
        """Run the agent in an interactive terminal loop."""
        print(f"\n{'=' * 60}")
        print(f"  {self.name}")
        print(f"{'=' * 60}")
        print(f"  Backend: {self.backend} | Model: {self.model}")
        print(f"  Type 'quit' to exit, 'reset' to clear history")
        print(f"{'=' * 60}\n")

        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye.")
                break

            if not user_input:
                continue
            if user_input.lower() == "quit":
                print("Goodbye.")
                break
            if user_input.lower() == "reset":
                self.reset()
                print("[Conversation reset]\n")
                continue

            try:
                response = self.send(user_input)
                print(f"\n{self.name}: {response}\n")
            except Exception as e:
                print(f"\n[Error: {e}]\n")
