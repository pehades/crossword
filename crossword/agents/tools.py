from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, tool
from langgraph.types import Command

from crossword.adapters.base_search import BaseSearch
from crossword.adapters.vector_db import VectorDB
from crossword.adapters.wikipedia_search import Wikipedia

PREVIEW_CHARS = 500
TOP_K_FACTS = 5


def build_wikipedia_tool(wikipedia: Wikipedia) -> BaseTool:

    @tool
    def wikipedia_search(query: str, runtime: ToolRuntime) -> Command:
        """Search Wikipedia with short keywords. Returns the beginning of the matching articles; use lookup_facts for details."""
        results = wikipedia.search(query)
        preview = "\n\n".join(f"# {result.title}\n{result.content[:PREVIEW_CHARS]}" for result in results)
        return Command(update={
            'search_results': {result.id: result for result in results},
            'messages': [ToolMessage(preview or "No results.", tool_call_id=runtime.tool_call_id)],
        })

    return wikipedia_search


def build_lookup_facts_tool(vector_db: VectorDB) -> BaseTool:

    @tool
    def lookup_facts(query: str, runtime: ToolRuntime) -> str:
        """Retrieve the most relevant passages for a specific question from everything found so far with wikipedia_search and web_search_tool."""
        search_results = runtime.state.get('search_results', {})
        vector_db.insert(list(search_results.values()))

        documents = vector_db.query(query, result_ids=list(search_results))[:TOP_K_FACTS]
        if not documents:
            return "No facts found. Search with wikipedia_search or web_search_tool first."
        return "\n\n---\n\n".join(documents)

    return lookup_facts


def build_web_search_tool(web_search: BaseSearch) -> BaseTool:

    @tool
    def web_search_tool(query: str, runtime: ToolRuntime) -> Command:
        """Search the web for up-to-date information. Returns the beginning of the matching pages; use lookup_facts for details."""
        results = web_search.search(query)
        preview = "\n\n".join(f"# {result.title} ({result.id})\n{result.content[:PREVIEW_CHARS]}" for result in results)
        return Command(update={
            'search_results': {result.id: result for result in results},
            'messages': [ToolMessage(preview or "No results.", tool_call_id=runtime.tool_call_id)],
        })

    return web_search_tool
