import time

from fastapi import HTTPException
from starlette.requests import Request


class RateLimiter:

    def __init__(self, n_requests_allowed: int, window_seconds: int):
        self.requests_per_client: dict[str, list] = dict()
        self.n_requests_allowed = n_requests_allowed
        self.window_seconds = window_seconds

    def client_can_do_request(self, client_id: str) -> bool:
        current_request_time = time.time()
        self.requests_per_client[client_id] = [
            request_time for request_time in self.requests_per_client.get(client_id, [])
            if request_time > current_request_time - self.window_seconds
        ]
        if len(self.requests_per_client[client_id]) >= self.n_requests_allowed:
            return False
        self.requests_per_client[client_id].append(current_request_time)
        return True

    # FastAPI calls this when the instance is used as a dependency
    def __call__(self, request: Request):
        if not self.client_can_do_request(client_id=request.client.host):
            raise HTTPException(status_code=429, detail='Too many requests')
