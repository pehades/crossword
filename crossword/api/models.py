from pydantic import BaseModel

from crossword.business_logic.models import Quiz


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


class ChatStreamEvent(BaseModel):
    message: str = ''
    quiz: Quiz | None = None
    error: str | None = None
