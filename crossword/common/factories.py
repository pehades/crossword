import os
from functools import cache

import chromadb
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from tavily import TavilyClient

from crossword import REPOSITORY_DIR
from crossword.adapters.vector_db import VectorDB
from crossword.adapters.wikipedia_search import Wikipedia
from crossword.agents.prompts import QUIZ_AGENT_PROMPT
from crossword.agents.schemas import Quiz, QuizState
from crossword.common.env_config import EnvConfig
from crossword.adapters.web_search import WebSearchEngine
from crossword.agents.tools import build_lookup_facts_tool, build_web_search_tool, build_wikipedia_tool


class ConfigFactory:

    @classmethod
    @cache
    def get_env_config(cls) -> EnvConfig:
        # load_dotenv also exports to os.environ, which is where langsmith reads its settings
        load_dotenv(REPOSITORY_DIR / '.env')
        return EnvConfig(
            nebius_api_key=os.environ['NEBIUS_API_KEY'],
            tavily_api_key=os.environ['TAVILY_API_KEY'],
            wikipedia_headers=os.environ['WIKIPEDIA_HEADERS'],
        )


class AdaptersFactory:

    @classmethod
    def get_web_search_engine(cls) -> WebSearchEngine:

        config = ConfigFactory.get_env_config()
        return WebSearchEngine(
            client=TavilyClient(api_key=config.tavily_api_key)
        )

    @classmethod
    def get_wikipedia_search(cls) -> Wikipedia:
        config = ConfigFactory.get_env_config()
        return Wikipedia(headers={'User-Agent': config.wikipedia_headers})

    @classmethod
    def get_vector_db(cls) -> VectorDB:
        return VectorDB(
            client=chromadb.PersistentClient(os.path.join(REPOSITORY_DIR, 'chromadb.db'))
        )


class LLMFactory:

    @classmethod
    def get_chat_model(cls) -> BaseChatModel:
        config = ConfigFactory.get_env_config()
        return ChatOpenAI(
            model=config.llm_model,
            base_url=config.llm_base_url,
            api_key=config.nebius_api_key
        )


class ToolsFactory:

    @classmethod
    def get_research_tools(cls) -> list[BaseTool]:
        return [
            build_wikipedia_tool(AdaptersFactory.get_wikipedia_search()),
            build_lookup_facts_tool(AdaptersFactory.get_vector_db()),
            build_web_search_tool(AdaptersFactory.get_web_search_engine()),
        ]


class AgentsFactory:

    @classmethod
    def get_quiz_agent(cls):
        return create_agent(
            model=LLMFactory.get_chat_model(),
            system_prompt=QUIZ_AGENT_PROMPT,
            tools=ToolsFactory.get_research_tools(),
            state_schema=QuizState,
            response_format=Quiz,
            checkpointer=InMemorySaver()
        )
