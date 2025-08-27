**NEWS_AGENT_WITH_MCP**

This project is a small experiment where I built a news summarizing agent using MCP (Model Context Protocol). The agent can take news text, process it through prompts/tools, and return a summary in a neat way.
I made this while learning MCP step by step, so the code is split into three main files that each handle a different part of the agent.

***Project Structure***

- **main.py**
This is the entry point. It starts the MCP server and brings everything together so the agent can run.

- **prompted_agent.py**
This file handles the logic for prompting. Basically, it defines how the news summarizer should “think” when asked to summarize text.

- **tool_agent.py**
This file contains the tool functions that the agent can use. In this case, the main tool is summarizing news content.
