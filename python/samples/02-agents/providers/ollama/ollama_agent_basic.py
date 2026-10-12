# Copyright (c) Microsoft. All rights reserved.

import asyncio
import itertools
from datetime import datetime

from agent_framework import Agent, tool
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


# --- Original fixed-query examples (kept for reference, not run by default) ---
#
# async def non_streaming_example() -> None:
#     """Example of non-streaming response (get the complete result at once)."""
#     agent = Agent(
#         client=OllamaChatClient(),
#         name="TimeAgent",
#         instructions="You are a helpful time agent answer in one sentence.",
#         tools=get_time,
#     )
#     query = "What time is it in Seattle? Use a tool call"
#     result = await agent.run(query)
#     print(f"Result: {result}\n")
#
# async def streaming_example() -> None:
#     """Example of streaming response (get results as they are generated)."""
#     agent = Agent(
#         client=OllamaChatClient(),
#         name="TimeAgent",
#         instructions="You are a helpful time agent answer in one sentence.",
#         tools=get_time,
#     )
#     query = "What time is it in San Francisco? Use a tool call"
#     async for chunk in agent.run(query, stream=True):
#         if chunk.text:
#             print(chunk.text, end="", flush=True)


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
    # OllamaChatClient() with no arguments reads OLLAMA_MODEL (which model to
    # use, e.g. "llama3.2") and OLLAMA_HOST (defaults to
    # http://localhost:11434) from environment variables.
    agent = Agent(
        client=OllamaChatClient(),
        name="Assistant",
        instructions="You are a helpful assistant. Use the get_time tool when asked about the time.",
        tools=get_time,
    )

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


async def main() -> None:
    print("=== Basic Ollama Chat Client Agent Example (interactive) ===")
    await interactive_chat()


if __name__ == "__main__":
    asyncio.run(main())
