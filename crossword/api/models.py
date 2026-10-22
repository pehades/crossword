from pydantic import BaseModel, Field

from crossword.business_logic.models import Crossword, Quiz


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    thread_id: str | None = None


class ChatStreamEvent(BaseModel):
    thread_id: str | None = None
    message: str = ''
    status: str | None = None
    quiz: Quiz | None = None
    crossword: Crossword | None = None
    error: str | None = None
