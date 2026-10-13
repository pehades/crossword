import os

import chromadb
from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

from crossword import REPOSITORY_DIR
from crossword.adapters.vector_db import VectorDB
from crossword.adapters.wikipedia_search import Wikipedia
from crossword.agents.prompts import QUIZ_AGENT_PROMPT
from crossword.agents.schemas import Quiz, QuizState
from crossword.common.env_config import EnvConfig
from crossword.adapters.web_search import WebSearchEngine
from crossword.agents.tools import build_lookup_facts_tool, build_web_search_tool, build_wikipedia_tool


class AdaptersFactory:

    @classmethod
    def get_web_search_engine(cls) -> WebSearchEngine:

        config = EnvConfig()
        return WebSearchEngine(
            client=TavilyClient(api_key=config.tavily_api_key)
        )

    @classmethod
    def get_wikipedia_search(cls) -> Wikipedia:
        config = EnvConfig()
        return Wikipedia(headers={'User-Agent': config.wikipedia_headers})

    @classmethod
    def get_vector_db(cls) -> VectorDB:
        return VectorDB(
            client=chromadb.PersistentClient(os.path.join(REPOSITORY_DIR, 'chromadb.db'))
        )


class LLMFactory:

    @classmethod
    def get_chat_model(cls) -> BaseChatModel:
        config = EnvConfig()
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
            response_format=Quiz
        )
