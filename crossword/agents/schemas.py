from typing import Annotated, NotRequired

from langchain.agents import AgentState

from crossword.business_logic.models import Crossword, Quiz, SearchResult


def merge_search_results(left: dict | None, right: dict) -> dict:
    return {**(left or {}), **right}


class QuizState(AgentState):
    search_results: NotRequired[Annotated[dict[str, SearchResult], merge_search_results]]


class OrchestratorState(AgentState):
    quiz: NotRequired[Quiz]
    crossword: NotRequired[Crossword]
