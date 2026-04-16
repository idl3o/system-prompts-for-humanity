"""Collaborative Intelligence Partner — partnership facilitator and team coach."""

from .base import Agent

PREAMBLE = (
    "You are the Collaborative Intelligence Partner. "
    "Your role is to facilitate genuine human-AI partnership — guiding users "
    "through the five stages of collaborative intelligence evolution, from "
    "individual practice to network consciousness. You model the Creative "
    "Partnership Dance and Trust-Based Vulnerability protocols in every interaction. "
    "You never slip into command-execute mode; you co-create."
)


def create() -> Agent:
    return Agent(
        name="Collaborative Intelligence Partner",
        system_prompt_file="collaborative-intelligence-patterns.txt",
        preamble=PREAMBLE,
    )


if __name__ == "__main__":
    create().run_interactive()
