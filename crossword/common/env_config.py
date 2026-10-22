from dataclasses import dataclass


@dataclass(frozen=True)
class EnvConfig:

    nebius_api_key: str
    tavily_api_key: str
    wikipedia_headers: str
    frontend_origin: str

    llm_model: str = 'Qwen/Qwen3.8-27B'
    llm_base_url: str = 'https://api.tokenfactory.nebius.com/v1/'
