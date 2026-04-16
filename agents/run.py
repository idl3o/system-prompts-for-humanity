#!/usr/bin/env python3
"""CLI entry point for System Prompts for Humanity agents.

Usage:
    python -m agents.run                          # interactive menu (Ollama)
    python -m agents.run collaborative            # launch specific agent
    python -m agents.run consciousness
    python -m agents.run constraint
    python -m agents.run meta
    python -m agents.run --list                   # list available agents
    python -m agents.run --api collaborative      # single-shot (reads stdin)
    python -m agents.run --backend anthropic meta # use Claude API instead
    python -m agents.run --model gpt-oss:20b collaborative  # override model
"""

import argparse
import sys

from . import (
    collaborative_intelligence,
    consciousness_driven,
    resource_constrained,
    meta_framework,
)

AGENTS = {
    "collaborative": ("Collaborative Intelligence Partner", collaborative_intelligence.create),
    "consciousness": ("Consciousness-Driven Dev Partner", consciousness_driven.create),
    "constraint": ("Resource-Constrained Innovation Agent", resource_constrained.create),
    "meta": ("Meta-Framework Integration Agent", meta_framework.create),
}


def pick_interactive() -> str:
    print("\n  System Prompts for Humanity — Agents\n")
    for i, (key, (label, _)) in enumerate(AGENTS.items(), 1):
        print(f"  [{i}] {label}  ({key})")
    print()
    while True:
        choice = input("Pick an agent (number or name): ").strip().lower()
        if choice in AGENTS:
            return choice
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(AGENTS):
                return list(AGENTS.keys())[idx]
        except ValueError:
            pass
        print("Invalid choice. Try again.")


def main():
    parser = argparse.ArgumentParser(description="Run an SPFH agent")
    parser.add_argument("agent", nargs="?", choices=list(AGENTS.keys()), help="Agent to launch")
    parser.add_argument("--list", action="store_true", help="List available agents")
    parser.add_argument("--api", action="store_true", help="Single-shot mode: read prompt from stdin, print response")
    parser.add_argument("--backend", choices=["ollama", "anthropic"], default=None, help="Backend (default: ollama)")
    parser.add_argument("--model", default=None, help="Override model")
    args = parser.parse_args()

    if args.list:
        for key, (label, _) in AGENTS.items():
            print(f"  {key:15s}  {label}")
        return

    agent_key = args.agent or pick_interactive()
    label, factory = AGENTS[agent_key]
    agent = factory()

    if args.backend:
        from .base import DEFAULTS
        agent.backend = args.backend
        cfg = DEFAULTS[args.backend]
        from openai import OpenAI
        agent.client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
        if not args.model:
            agent.model = cfg["model"]

    if args.model:
        agent.model = args.model

    if args.api:
        prompt = sys.stdin.read().strip()
        if not prompt:
            print("Error: no input on stdin", file=sys.stderr)
            sys.exit(1)
        print(agent.send(prompt))
    else:
        agent.run_interactive()


if __name__ == "__main__":
    main()
