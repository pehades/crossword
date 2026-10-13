from crossword import REPOSITORY_DIR

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvConfig(BaseSettings):

    model_config = SettingsConfigDict(env_file=os.path.join(REPOSITORY_DIR, '.env'))

    nebius_api_key: str
    tavily_api_key: str
    wikipedia_headers: str

    llm_model: str = 'Qwen/Qwen3.8-27B'
    llm_base_url: str = 'https://api.tokenfactory.nebius.com/v1/'
