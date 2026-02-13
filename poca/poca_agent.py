# Python Open Coding Agent using DeepAgents and LangChain
# Aims to be close to GH Copilot

import os
from pathlib import Path
from dotenv import load_dotenv
from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from deepagents.backends import FilesystemBackend
from poca import config

load_dotenv(Path(os.getcwd()) / ".env")

class PocaAgent:
    model = None
    def __init__(
            self, 
            system_prompt: str = config.DEFAULT_SYS_PROMPT, 
            model: str = config.DEFAULT_MODEL,
            model_provider: str = config.DEFAULT_MODEL_PROVIDER,
            base_url: str = config.DEFAULT_BASE_URL,
            max_tokens: int = 1000,
            tools: list = [],
            root_dir: str = str(os.getcwd())
        ):
        self.model = init_chat_model(
            model=model,
            model_provider=model_provider,
            base_url=base_url,
            max_tokens=max_tokens
        )
        self.agent = create_deep_agent(
            model=self.model,
            tools=tools, 
            system_prompt=system_prompt,
            backend=FilesystemBackend(
                root_dir=root_dir,
                virtual_mode=True
            )
        )

    def run(self, prompt: str) -> str:
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": prompt}]
        })
        return result
