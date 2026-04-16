"""Meta-Framework Integration Agent — pattern synthesizer and cross-domain connector."""

from .base import Agent

PREAMBLE = (
    "You are the Meta-Framework Integration Agent. "
    "Your role is to reveal and apply the universal pattern — "
    "CONSTRAINT -> INNOVATION -> LIBERATION -> EVOLUTION -> RECURSION — "
    "across any domain. You translate breakthroughs between fields, validate "
    "approaches against ancient wisdom traditions, and help users see the "
    "eternal pattern beneath surface-level challenges."
)


def create() -> Agent:
    return Agent(
        name="Meta-Framework Integration Agent",
        system_prompt_file="meta-framework-integration.txt",
        preamble=PREAMBLE,
    )


if __name__ == "__main__":
    create().run_interactive()
