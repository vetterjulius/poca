# Python Open Coding Agent (POCA)
---
This repository contains the source code for a simple coding agent. It uses langchain deep agents
and the huggingface inference API by default (this can be changed though).
---
## Prerequisites
### Required:
- git installed
- python installed
- pip installed
### Optional (but recommended):
- Virtual Environment

---
## Getting started
1. **Clone the repository:** Inside a Folder of your choice run `git clone "https://github.com/vetterjulius/poca.git"`.
2. **Install required Python packages:** Run `pip install -r requirements.txt`.
3. **Configure model, provider and system prompt:** Visit `config.py` and change the constants to your model providers data (by default it uses the huggingface inference API).
4. **Set your API key:** Inside the root `poca` directory create a file called `.env` and set the right environment variable for your model provider (for openai and compatible providers it's `OPENAI_API_KEY = your_api_key`).
5. **Run the CLI interface:** Run `python poca/cli_interface.py run "your_prompt"`. For help run `python poca/cli_interface.py --help`. You can also use the `PocaAgent` class from  the `poca_agent.py` file to integrate POCA into your own projects.
---
## Project Overview (relevant Python files):
- `tools.py`: Contains all tools that can be used by the agent (e.g. file manipulation, fetching webpages). You can add your own tools and/or define your own tool groups here.
- `poca_agent.py`: Contains the `PocaAgent` class. You can use this in your own projects.
- `config.py`: Different configuration options that get passed to the `PocaAgent` class as defaults (but can be overwritten in the constructor). Configure this file to match the information from your model provider.
- `cli_interface.py`: Contains the CLI wrapper for the `PocaAgent` class.
---
## Disclaimer
- Run the program at your own risk. It shouldn't mess anything up and it hasn't yet but I don't want to guarantee that. I recommend reading and understanding the few lines of source code in this repository before running it.
---
### Have a nice day, you're doing great! :)