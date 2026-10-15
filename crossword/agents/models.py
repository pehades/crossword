from pydantic import BaseModel


class DBDocument(BaseModel):
    id: str
    url: str
    query: str
    score: float
    document: str
