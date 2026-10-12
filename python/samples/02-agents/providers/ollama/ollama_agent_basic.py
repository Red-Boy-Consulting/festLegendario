# Copyright (c) Microsoft. All rights reserved.

import asyncio
import itertools
import os
import shutil
from datetime import datetime

from agent_framework import Agent, MCPStdioTool, tool
from agent_framework.ollama import OllamaChatClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

"""
Ollama Agent Basic Example

This sample demonstrates implementing an Ollama agent with basic tool usage,
running interactively: it keeps asking the console for a question and lets
you talk to the agent about anything, instead of a fixed canned query.

Ensure to install Ollama and have a model running locally before running the sample
Not all Models support function calling, to test function calling try llama3.2 or qwen3:4b
Set the model to use via the OLLAMA_MODEL environment variable or modify the code below.
https://ollama.com/

Optional Playwright browser automation (MCP):
Set ENABLE_PLAYWRIGHT_MCP=1 and have Node.js/npx installed to give the agent
browser automation tools (navigate, click, screenshot, etc.) served by the
official @playwright/mcp server (started automatically as a child process,
no separate setup required beyond Node.js). https://github.com/microsoft/playwright-mcp

"""


# NOTE: approval_mode="never_require" is for sample brevity. Use "always_require" in production;
# see samples/02-agents/tools/function_tool_with_approval.py
# and samples/02-agents/tools/function_tool_with_approval_and_sessions.py.
# This function is exposed to the model as a "tool" it can call by name
# (the model decides when to invoke it based on the user's query).
@tool(approval_mode="never_require")
def get_time(location: str) -> str:
    """Get the current time."""
    return f"The current time in {location} is {datetime.now().strftime('%I:%M %p')}."


async def _spinner(stop_event: asyncio.Event) -> None:
    """Print a rotating "thinking" indicator until stop_event is set.

    Local models can take a few seconds before the first streamed token
    arrives; this gives the user visible feedback that the agent is
    working instead of an apparently frozen terminal.
    """
    frames = itertools.cycle("|/-\\")
    while not stop_event.is_set():
        print(f"\rAgent: {next(frames)} pensando...", end="", flush=True)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=0.15)
        except asyncio.TimeoutError:
            pass
    # Clear the spinner line before the caller prints the real answer.
    print("\r" + " " * 40, end="", flush=True)


async def interactive_chat() -> None:
    """Keep asking the console for questions until the user exits.

    Type a question and press Enter to get a streamed answer. Type
    "exit", "quit", "salir", "fin" or "adios" (or press Ctrl+C) to stop.
    """
    no_browser_instructions = (
        "You are a general-purpose helpful assistant that can discuss any topic. "
        "You have access to a get_time tool that returns the current time for a "
        "specific city. Only call that tool when the user explicitly asks what time "
        "it is somewhere AND names a city. For greetings, general knowledge, how-to "
        "questions, or anything else, just answer directly in plain text — never ask "
        "the user for their location and never mention the get_time tool unless it "
        "was actually used. You do NOT have web browser automation tools (e.g. "
        "Playwright) in this session. If asked whether you can browse the web, "
        "click, navigate, or take screenshots, say honestly that you don't have "
        "that capability right now — never claim you can do it when you can't."
    )
    with_browser_instructions = no_browser_instructions.replace(
        "You do NOT have web browser automation tools (e.g. "
        "Playwright) in this session. If asked whether you can browse the web, "
        "click, navigate, or take screenshots, say honestly that you don't have "
        "that capability right now — never claim you can do it when you can't.",
        "You also have browser automation tools (Playwright: navigate, click, "
        "screenshot, etc.) available — use them whenever the user asks you to "
        "browse or check a website.",
    )
    # base_instructions is what gets used if Playwright fails to connect and we
    # fall back below; it must truthfully say the browser tools are NOT available.
    base_instructions = no_browser_instructions
    tools: list[object] = [get_time]
    instructions = no_browser_instructions

    # Playwright MCP gives the agent browser automation tools (navigate, click,
    # screenshot, etc.). It's optional because it requires Node.js/npx AND
    # internet access (npx downloads the package on first use); only enable
    # it if explicitly requested via ENABLE_PLAYWRIGHT_MCP=1.
    playwright_enabled = os.environ.get("ENABLE_PLAYWRIGHT_MCP") == "1"
    if playwright_enabled and shutil.which("npx") is None:
        print("ENABLE_PLAYWRIGHT_MCP=1 pero no se encontró 'npx' en el PATH; se omite Playwright MCP.")
        playwright_enabled = False

    if playwright_enabled:
        # MCPStdioTool launches the MCP server as a child process and talks to
        # it over stdin/stdout, exposing its tools to the agent automatically.
        tools.append(
            MCPStdioTool(
                name="playwright",
                description="Browser automation tools (navigate, click, screenshot, etc.).",
                command="npx",
                args=["-y", "@playwright/mcp@latest"],
            )
        )
        instructions = with_browser_instructions

    # OllamaChatClient() with no arguments reads OLLAMA_MODEL (which model to
    # use, e.g. "llama3.2") and OLLAMA_HOST (defaults to
    # http://localhost:11434) from environment variables.
    agent = Agent(
        client=OllamaChatClient(),
        name="Assistant",
        instructions=instructions,
        tools=tools,
    )

    # Entering the agent's context starts any MCP child process (e.g.
    # Playwright) and connects to it. If that connection hangs (e.g. no
    # internet to download the Playwright MCP package) or fails, give up
    # after PLAYWRIGHT_MCP_TIMEOUT_SECONDS and fall back to running without
    # it instead of leaving the user stuck on the "pensando..." spinner.
    # 60s because the *first* run of `npx @playwright/mcp@latest` has to
    # download the npm package (and npx itself resolving it) which can take
    # well over 15s even with a working internet connection; subsequent runs
    # are cached by npx and connect almost instantly.
    PLAYWRIGHT_MCP_TIMEOUT_SECONDS = 60
    if playwright_enabled:
        print("Conectando Playwright MCP (puede tardar ~1 min la primera vez mientras se descarga)...")
    try:
        if playwright_enabled:
            await asyncio.wait_for(agent.__aenter__(), timeout=PLAYWRIGHT_MCP_TIMEOUT_SECONDS)
        else:
            await agent.__aenter__()
    except Exception as exc:  # noqa: BLE001 - deliberately broad: any MCP/network failure falls back
        if not playwright_enabled:
            raise
        print(
            f"No se pudo conectar Playwright MCP ({exc.__class__.__name__}); "
            "continuando sin esa herramienta (revisa tu conexión a internet)."
        )
        tools = [get_time]
        agent = Agent(
            client=OllamaChatClient(),
            name="Assistant",
            instructions=base_instructions,
            tools=tools,
        )
        await agent.__aenter__()

    try:
        # create_session() keeps conversation history across turns, so the
        # agent remembers earlier questions/answers within the same run.
        session = agent.create_session()

        print("Escribe tu pregunta (o 'exit'/'quit'/'salir'/'fin' para salir):")
        while True:
            try:
                query = input("\nUser: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not query:
                continue
            if query.lower() in {"exit", "quit", "salir", "fin", "adios", "adiós"}:
                break

            # Show an animated "thinking" spinner while we wait for the model's
            # first token (local models can take a few seconds before they
            # start streaming output).
            stop_spinner = asyncio.Event()
            spinner_task = asyncio.create_task(_spinner(stop_spinner))

            first_chunk = True
            # stream=True yields the response incrementally as text chunks, useful
            # for showing output to a user as it's generated instead of waiting
            # for the full response.
            async for chunk in agent.run(query, session=session, stream=True):
                if chunk.text:
                    if first_chunk:
                        # First real token arrived: stop the spinner and print
                        # the "Agent:" prefix before the actual answer.
                        stop_spinner.set()
                        await spinner_task
                        print("\rAgent: ", end="", flush=True)
                        first_chunk = False
                    print(chunk.text, end="", flush=True)

            if first_chunk:
                # The model never produced any text; still clear the spinner.
                stop_spinner.set()
                await spinner_task
            print()
    finally:
        # Always shut down the agent/MCP child process cleanly, even if the
        # loop above exited via break, Ctrl+C, or an unexpected error.
        await agent.__aexit__(None, None, None)


async def main() -> None:
    print("=== Basic Ollama Chat Client Agent Example (interactive) ===")
    await interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
