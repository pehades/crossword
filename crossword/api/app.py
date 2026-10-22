import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.sse import EventSourceResponse
from langchain_core.messages import HumanMessage

from crossword.api.rate_limit import RateLimiter
from crossword.common.factories import AgentsFactory, ConfigFactory
from crossword.common.logger import create_logger
from crossword.api.models import ChatRequest, ChatStreamEvent

logger = create_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('Building the orchestrator agent')
    app.state.orchestrator_agent = AgentsFactory.get_orchestrator_agent()
    logger.info('Orchestrator agent ready')
    yield


config = ConfigFactory.get_env_config()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=[config.frontend_origin], allow_methods=['*'], allow_headers=['*'])

rate_limiter = RateLimiter(n_requests_allowed=15, window_seconds=3600 * 6)


@app.post('/chat', response_class=EventSourceResponse, dependencies=[Depends(rate_limiter)])
def chat(chat_request: ChatRequest, request: Request):
    thread_id = chat_request.thread_id if chat_request.thread_id else str(uuid.uuid4())
    orchestrator_agent = app.state.orchestrator_agent
    logger.info(f'Chat request from {request.client.host}, thread {thread_id}: {chat_request.message[:100]}')

    yield ChatStreamEvent(thread_id=thread_id)
    try:
        for mode, chunk in orchestrator_agent.stream(
                {'messages': [HumanMessage(content=chat_request.message)]},
                config={'configurable': {'thread_id': thread_id}},
                stream_mode=['messages', 'updates']
        ):
            if mode == 'messages':
                token, metadata = chunk
                if token.content and metadata['langgraph_node'] == 'model' and '|' not in metadata.get('checkpoint_ns', ''):
                    yield ChatStreamEvent(message=token.content)
            if mode == 'updates':
                for node, update in chunk.items():
                    items = update if isinstance(update, list) else [update]
                    for item in items:
                        if node == 'model' and isinstance(item, dict) and item.get('messages') and item['messages'][-1].tool_calls:
                            yield ChatStreamEvent(status='Researching the topic and building your crossword...')
                        if isinstance(item, dict) and item.get('crossword'):
                            logger.info(f'Sending crossword for thread {thread_id}')
                            yield ChatStreamEvent(crossword=item['crossword'])
        logger.info(f'Chat finished for thread {thread_id}')
    except Exception as exc:
        logger.exception(f'Chat failed for thread {thread_id}')
        yield ChatStreamEvent(message='', error=str(exc))


@app.get('/health')
def health():
    return {'status': 'ok'}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000, proxy_headers=True, forwarded_allow_ips='*')
