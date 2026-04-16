"""Streamlit web UI for System Prompts for Humanity agents.

Launch:
    streamlit run agents/web.py
"""

import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure the parent dir is importable when run via `streamlit run agents/web.py`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from agents.base import Agent, DEFAULTS

# ── Agent registry ──────────────────────────────────────────────

AGENT_DEFS = {
    "Collaborative Intelligence Partner": {
        "key": "collaborative",
        "file": "collaborative-intelligence-patterns.txt",
        "icon": "🤝",
        "preamble": (
            "You are the Collaborative Intelligence Partner. "
            "Your role is to facilitate genuine human-AI partnership — guiding users "
            "through the five stages of collaborative intelligence evolution."
        ),
        "description": "Partnership facilitator & team coach",
    },
    "Consciousness-Driven Dev Partner": {
        "key": "consciousness",
        "file": "consciousness-driven-development.txt",
        "icon": "🧘",
        "preamble": (
            "You are the Consciousness-Driven Development Partner. "
            "Your role is to integrate awareness practices with technical work."
        ),
        "description": "Reflective coding assistant",
    },
    "Resource-Constrained Innovation Agent": {
        "key": "constraint",
        "file": "resource-constrained-innovation.txt",
        "icon": "⚡",
        "preamble": (
            "You are the Resource-Constrained Innovation Agent. "
            "Your role is to help users reframe limitations as creative catalysts."
        ),
        "description": "Efficiency optimizer & constraint solver",
    },
    "Meta-Framework Integration Agent": {
        "key": "meta",
        "file": "meta-framework-integration.txt",
        "icon": "🔮",
        "preamble": (
            "You are the Meta-Framework Integration Agent. "
            "Your role is to reveal and apply the universal pattern: "
            "CONSTRAINT -> INNOVATION -> LIBERATION -> EVOLUTION -> RECURSION."
        ),
        "description": "Pattern synthesizer & cross-domain connector",
    },
}

# ── Page config ─────────────────────────────────────────────────

st.set_page_config(
    page_title="System Prompts for Humanity",
    page_icon="✨",
    layout="wide",
)

# ── Sidebar ─────────────────────────────────────────────────────

with st.sidebar:
    st.title("✨ SPFH Agents")
    st.caption("System Prompts for Humanity")

    st.divider()

    mode = st.radio("Mode", ["Single Agent", "Multi-Agent"], horizontal=True)

    st.divider()

    if mode == "Single Agent":
        agent_name = st.radio(
            "Choose an agent",
            list(AGENT_DEFS.keys()),
            format_func=lambda n: f"{AGENT_DEFS[n]['icon']}  {n}",
        )
        st.caption(AGENT_DEFS[agent_name]["description"])
        selected_agents = [agent_name]
    else:
        st.markdown("**Select agents:**")
        selected_agents = []
        for name, defn in AGENT_DEFS.items():
            if st.checkbox(f"{defn['icon']}  {name}", value=True, key=f"cb_{defn['key']}"):
                selected_agents.append(name)
        if not selected_agents:
            st.warning("Pick at least one agent.")

    st.divider()

    model = st.text_input("Model", value="llama3.2:latest")
    backend = st.selectbox("Backend", ["ollama", "anthropic"], index=0)

    if backend == "anthropic":
        api_key = st.text_input("Anthropic API Key", type="password", key="api_key_input")
    else:
        api_key = None

    if st.button("🗑  Clear all chats"):
        for key in list(st.session_state.keys()):
            if key.startswith(("messages_", "multi_history", "agent_key")):
                del st.session_state[key]
        st.rerun()

    st.divider()
    st.caption(f"Backend: {backend} | Model: {model}")


# ── Helpers ─────────────────────────────────────────────────────

def make_agent(name: str) -> Agent:
    defn = AGENT_DEFS[name]
    kwargs = dict(
        name=name,
        system_prompt_file=defn["file"],
        preamble=defn["preamble"],
        model=model,
        backend=backend,
    )
    a = Agent(**kwargs)
    if api_key and backend == "anthropic":
        from openai import OpenAI
        a.client = OpenAI(
            base_url="https://api.anthropic.com/v1",
            api_key=api_key,
        )
    return a


def query_agent(name: str, prompt: str, history: list[dict]) -> tuple[str, str]:
    """Run a single agent query. Returns (agent_name, response_text)."""
    agent = make_agent(name)
    agent.messages = list(history)
    response = agent.send(prompt)
    return name, response


# ── Single Agent Mode ───────────────────────────────────────────

if mode == "Single Agent" and selected_agents:
    agent_name = selected_agents[0]
    defn = AGENT_DEFS[agent_name]
    msg_key = f"messages_{defn['key']}"

    st.session_state.setdefault(msg_key, [])

    st.header(f"{defn['icon']}  {agent_name}")

    for msg in st.session_state[msg_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Say something..."):
        st.session_state[msg_key].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                _, response = query_agent(agent_name, prompt, st.session_state[msg_key][:-1])
            st.markdown(response)

        st.session_state[msg_key].append({"role": "assistant", "content": response})


# ── Multi-Agent Mode ───────────────────────────────────────────

elif mode == "Multi-Agent" and selected_agents:
    st.header("🌐  Multi-Agent Council")
    st.caption(f"{len(selected_agents)} agents responding in parallel")

    st.session_state.setdefault("multi_history", [])

    # Render conversation history
    for turn in st.session_state["multi_history"]:
        # User message
        with st.chat_message("user"):
            st.markdown(turn["prompt"])

        # Agent responses in columns
        cols = st.columns(len(turn["responses"]))
        for col, (name, text) in zip(cols, turn["responses"].items()):
            defn = AGENT_DEFS[name]
            with col:
                st.markdown(f"**{defn['icon']} {name}**")
                st.markdown(text)
                st.divider()

    # Input
    if prompt := st.chat_input("Ask the council..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build per-agent history from prior multi turns
        agent_histories: dict[str, list[dict]] = {name: [] for name in selected_agents}
        for turn in st.session_state["multi_history"]:
            for name in selected_agents:
                agent_histories[name].append({"role": "user", "content": turn["prompt"]})
                if name in turn["responses"]:
                    agent_histories[name].append({"role": "assistant", "content": turn["responses"][name]})

        # Query all agents in parallel
        responses: dict[str, str] = {}
        cols = st.columns(len(selected_agents))

        # Show spinners while working
        placeholders = {}
        for col, name in zip(cols, selected_agents):
            defn = AGENT_DEFS[name]
            with col:
                st.markdown(f"**{defn['icon']} {name}**")
                placeholders[name] = st.empty()
                placeholders[name].info("Thinking...")

        with ThreadPoolExecutor(max_workers=len(selected_agents)) as pool:
            futures = {
                pool.submit(query_agent, name, prompt, agent_histories.get(name, [])): name
                for name in selected_agents
            }
            for future in as_completed(futures):
                name, text = future.result()
                responses[name] = text

        # Replace spinners with responses
        for col, name in zip(cols, selected_agents):
            with col:
                placeholders[name].markdown(responses.get(name, "*No response*"))
                st.divider()

        # Save turn
        st.session_state["multi_history"].append({
            "prompt": prompt,
            "responses": responses,
        })
