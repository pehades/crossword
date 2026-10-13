from typing import Annotated, NotRequired

from langchain.agents import AgentState
from pydantic import BaseModel, Field

from crossword.adapters.base_search import SearchResult


class QuestionAnswer(BaseModel):
    question: str = Field(description="The crossword clue")
    answer: str = Field(description="The answer to the clue, a single word or a short name")


class Quiz(BaseModel):
    items: list[QuestionAnswer]


def merge_search_results(left: dict[str, SearchResult] | None, right: dict[str, SearchResult]) -> dict[str, SearchResult]:
    # tools may run in parallel, so merge their results instead of overwriting
    return {**(left or {}), **right}


class QuizState(AgentState):
    search_results: NotRequired[Annotated[dict[str, SearchResult], merge_search_results]]
