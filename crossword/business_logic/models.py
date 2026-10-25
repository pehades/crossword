from typing import Literal

from pydantic import BaseModel, Field, computed_field


class DBDocument(BaseModel):
    chunk_id: str
    document_id: str
    url: str
    query: str
    score: float
    document: str


class SearchResult(BaseModel):
    id: str
    url: str
    source: str
    title: str
    content: str


class QuestionAnswer(BaseModel):
    question: str = Field(description="The crossword clue/question")
    answer: str = Field(description="The answer to the clue, a single word or a short name")
    chunk_id: str = Field(description="The chunk_id of the document that supports the answer,"
                                         " e.g. if the document is Document(chunk_id=1, document='relevant passage') then 1.")


class Quiz(BaseModel):
    items: list[QuestionAnswer]


class PlacedWord(BaseModel):
    number: int
    direction: Literal['across', 'down']
    row: int
    col: int
    answer: str
    clue: str
    chunk_id: str


class Crossword(BaseModel):
    rows: int
    cols: int
    words: list[PlacedWord]
    unplaced: list[QuestionAnswer] = []


class QueryCheck(BaseModel):
    interpretations: list[str] = Field(..., description=(
        "The different things the key term of the request could refer to. "
        "Only list two interpretations if they are unrelated subjects that share a name "
        "(e.g. Mercury the planet vs. Mercury the element). "
        "Different aspects, sub-areas or angles of the same subject are ONE interpretation."
    ))
    has_topic: bool = Field(..., description="Does the request name any topic at all?")
    clarifying_question: str | None = Field(None, description="If the request has no topic or several interpretations, "
                                                              "a short question to ask the user, listing the options.")

    def is_ok(self) -> bool:
        return self.has_topic and len(self.interpretations) == 1

