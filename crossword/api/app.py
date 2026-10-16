import json
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from langchain_core.messages import AIMessageChunk, HumanMessage
from starlette.responses import StreamingResponse


from crossword.common.factories import AgentsFactory
from crossword.api.models import ChatRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.orchestrator_agent = AgentsFactory.get_orchestrator_agent()
    yield


app = FastAPI(lifespan=lifespan)


def sse(event: str, data: dict) -> str:
    return f'event: {event}\ndata: {json.dumps(data)}\n\n'


def token_stream(chat_request: ChatRequest):
    thread_id = chat_request.thread_id if chat_request.thread_id else str(uuid.uuid4())
    orchestrator_agent = app.state.orchestrator_agent

    yield sse('start', {'thread_id': thread_id})
    try:
        for message_chunk, metadata in orchestrator_agent.stream(
                {'messages': [HumanMessage(content=chat_request.message)]},
                config={'configurable': {'thread_id': thread_id}},
                stream_mode='messages'
        ):
            if isinstance(message_chunk, AIMessageChunk) and message_chunk.content and metadata['langgraph_node'] == 'model':
                yield sse('token', {'content': message_chunk.content})
    except Exception as exc:
        yield sse('error', {'detail': str(exc)})
    yield sse('end', {})


@app.post('/chat')
def chat(chat_request: ChatRequest):

    return StreamingResponse(token_stream(chat_request), media_type="text/event-stream",)


@app.get('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
