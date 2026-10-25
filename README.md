# Crossword

> Work in progress

An AI agent that creates crosswords about any topic you ask for.

**Demo:** [crossword.pehades.com](https://crossword.pehades.com)

## How it works

Tell it what your crossword should be about, e.g. "make me a crossword about the Roman Empire".
If your request is vague or could mean different things, it will ask you to be more specific first.

After a short research step, the crossword appears next to the chat, ready to solve.
Stuck on a word? Reveal it letter by letter.
You can also ask for changes, like a different focus or easier clues, and get a new crossword.

## Architecture

The backend follows a hexagonal (ports and adapters) architecture:

- `business_logic`: the domain models and the crossword builder, with no dependency on external services
- `adapters`: Wikipedia, web search and the vector database, behind common interfaces
- `agents`: the LangChain agents, their tools and prompts
- `api`: the FastAPI app that streams the chat over SSE
- `common`: config and factories, where all the dependencies are wired together

This keeps the core logic independent of the providers, so an adapter can be swapped or faked in tests.

## Evals

The `evals` folder contains LangSmith evaluations. For example, `orchestrator_routing.py` checks
that the orchestrator creates a quiz only when the request has a clear topic, and asks for clarification otherwise.

## Stack

LangChain / LangGraph, FastAPI, React with assistant-ui, Docker, deployed on Hetzner.
