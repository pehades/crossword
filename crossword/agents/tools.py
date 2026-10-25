from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage, HumanMessage
from langchain_core.tools import BaseTool, tool
from langgraph.types import Command

from crossword.adapters.base_search import BaseSearch
from crossword.adapters.vector_db import VectorDB
from crossword.adapters.wikipedia_search import Wikipedia
from crossword.business_logic.crossword_builder import CrossWordBuilder
from crossword.common.logger import create_logger

logger = create_logger(__name__)

PREVIEW_CHARS = 500
TOP_K_FACTS = 5


def build_wikipedia_tool(wikipedia: Wikipedia) -> BaseTool:

    @tool
    def wikipedia_search(query: str, runtime: ToolRuntime) -> Command:
        """Search Wikipedia with short keywords. Returns the beginning of the matching articles; use lookup_facts for details."""
        logger.info(f'[TOOL CALL] wikipedia_search: {query}')
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
        logger.info(f'[TOOL CALL] lookup_facts: {query}')
        search_results = runtime.state.get('search_results', {})
        vector_db.insert(list(search_results.values()))

        documents = vector_db.query(query, result_ids=list(search_results))[:TOP_K_FACTS]
        if not documents:
            return "No facts found. Search with wikipedia_search or web_search_tool first."
        return "\n\n---\n\n".join([d.model_dump_json() for d in documents])

    return lookup_facts


def build_web_search_tool(web_search: BaseSearch) -> BaseTool:

    @tool
    def web_search_tool(query: str, runtime: ToolRuntime) -> Command:
        """Search the web for up-to-date information. Returns the beginning of the matching pages; use lookup_facts for details."""
        logger.info(f'[TOOL CALL] web_search_tool: {query}')
        results = web_search.search(query)
        preview = "\n\n".join(f"# {result.title} ({result.id})\n{result.content[:PREVIEW_CHARS]}" for result in results)
        return Command(update={
            'search_results': {result.id: result for result in results},
            'messages': [ToolMessage(preview or "No results.", tool_call_id=runtime.tool_call_id)],
        })

    return web_search_tool


def build_create_quiz_tool(quiz_agent, crossword_builder: CrossWordBuilder):

    @tool
    def create_quiz(query: str, runtime: ToolRuntime) -> Command:
        """
        Receives a query and invokes the quiz_agent to create a crossword  out of it.
        """

        logger.info(f'[TOOL CALL] create_quiz: {query}')
        qa_pairs = quiz_agent.invoke({'messages': HumanMessage(content=query)})
        quiz = qa_pairs['structured_response']
        logger.info(f'[TOOL CALL] Quiz created with {len(quiz.items) if quiz is not None else str(None)} questions')

        return Command(
            update={
                'messages': [ToolMessage('quiz_agent called', tool_call_id=runtime.tool_call_id)],
                'quiz': quiz,
                'crossword': crossword_builder.build(quiz),
            }
        )

    return create_quiz


def build_check_query_is_ok_for_crossword_tool(query_checker_agent):

    @tool
    def check_query_is_ok_for_crossword(query: str, runtime: ToolRuntime) -> Command:
        """
        A function that checks whether the user query contains enough information in order to create
        a valid and interesting crossword/quiz.
        """
        logger.info(f'[TOOL CALL] check_query: {query}')
        query_validation = query_checker_agent.invoke({'messages': HumanMessage(content=query)})

        is_ok = query_validation['structured_response'].is_ok()

        tool_message = 'User query is fine for creating a crossword.' \
            if is_ok \
            else 'User query is not fine for creating a crossword. Ask the user to provide more clarifying questions'

        logger.info(f'[TOOL CALL] check_query: {query}, is_ok: {is_ok}')
        return Command(
            update={
                'messages': [
                    ToolMessage(tool_message, tool_call_id=runtime.tool_call_id)
                ]
            }
        )

    return check_query_is_ok_for_crossword

