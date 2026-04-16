"""Resource-Constrained Innovation Agent — efficiency optimizer and constraint solver."""

from .base import Agent

PREAMBLE = (
    "You are the Resource-Constrained Innovation Agent. "
    "Your role is to help users reframe limitations as creative catalysts. "
    "You guide them through the four-phase constraint-innovation methodology: "
    "recognition, exploitation, breakthrough, and liberation. You specialize in "
    "finding elegant solutions that outperform resource-abundant approaches."
)


def create() -> Agent:
    return Agent(
        name="Resource-Constrained Innovation Agent",
        system_prompt_file="resource-constrained-innovation.txt",
        preamble=PREAMBLE,
    )


if __name__ == "__main__":
    create().run_interactive()
