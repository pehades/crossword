import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.sse import EventSourceResponse
from langchain_core.messages import AIMessageChunk, HumanMessage


from crossword.common.factories import AgentsFactory
from crossword.api.models import ChatRequest, ChatStreamEvent


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.orchestrator_agent = AgentsFactory.get_orchestrator_agent()
    yield


app = FastAPI(lifespan=lifespan)


@app.post('/chat', response_class=EventSourceResponse)
def chat(chat_request: ChatRequest):
    thread_id = chat_request.thread_id if chat_request.thread_id else str(uuid.uuid4())
    orchestrator_agent = app.state.orchestrator_agent

    yield ChatStreamEvent(thread_id=thread_id)
    try:
        for mode, chunk in orchestrator_agent.stream(
                {'messages': [HumanMessage(content=chat_request.message)]},
                config={'configurable': {'thread_id': thread_id}},
                stream_mode=['messages', 'updates']
        ):
            if mode == 'messages':
                token, metadata = chunk
                if token.content and metadata['langgraph_node'] == 'model':
                    yield ChatStreamEvent(message=token.content)
            if mode == 'updates':
                for node, update in chunk.items():
                    updates = update if isinstance(chunk, list) else [update]
                    for update in updates:
                        if 'quiz' in update:
                            yield ChatStreamEvent(message='', quiz=update['quiz'])
    except Exception as exc:
        yield ChatStreamEvent(message='', error=str(exc))


@app.get('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
