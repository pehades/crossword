from pydantic import BaseModel, Field


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
