import asyncio
import os
from dotenv import load_dotenv, find_dotenv

# Import necessary classes for agents, models, and MCP client
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner, RunConfig
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams, MCPServer

# Load environment variables from a .env file
_: bool = load_dotenv(find_dotenv())

# URL of the  MCP server
MCP_SERVER_URL = "http://localhost:8000/mcp/" 

gemini_api_key = os.getenv("GEMINI_API_KEY")

client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Define the model to be used by the agent
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", # Use the flash model for fast responses
    openai_client=client
)

config = RunConfig(
    model = model,
    model_provider=client,
    tracing_disabled = True
) 

async def get_instructions_from_prompt(mcp_server: MCPServer, prompt_name: str, **kwargs) -> str:
    """
    Fetches agent instructions from a named prompt on the MCP server.

    Args:
        mcp_server: The MCP client instance connected to the server.
        prompt_name: The name of the prompt to retrieve (e.g., "news_summarizing_prompt").
        **kwargs: Parameters to pass to the prompt template.
    
    Returns:
        A string containing the formatted instructions for the agent.
    """
    print(f"Getting instructions from prompt: {prompt_name}")
    try:
        # Call the MCP server's get_prompt endpoint
        prompt_result = await mcp_server.get_prompt(prompt_name, kwargs)
        # Extract the text content from the response
        content = prompt_result.messages[0].content
        if hasattr(content, "text"):
            instructions = content.text
        else:
            instructions = str(content)
        print("Generated instructions successfully.")
        return instructions
    except Exception as e:
        print(f"Failed to get instructions from prompt '{prompt_name}': {e}")
        # Return a fallback instruction in case of an error
        return f"You are a helpful assistant. Error retrieving prompt: {e}"


async def main():
    """Main function to run the agent with a news summarization prompt."""
    print("=== NEWS SUMMARIZER DEMO ===")

    # Configure the MCP client to connect to the specified URL
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)

    # Use an async context manager for the MCP server client
    async with MCPServerStreamableHttp(
        name="NewsClient",
        params=mcp_params,
        cache_tools_list=True
    ) as mcp_server:
            try:
                # 1. Get agent instructions from the MCP server's prompt
                instructions = await get_instructions_from_prompt(
                    mcp_server,
                    "news_summarizing_prompt",
                    topic="AI in healthcare",
                    time_frame="the last month",
                    tone="informative",
                    focus="key developments and breakthroughs"
                )

                agent = Agent(
                    name="News Summarizer Agent",
                    instructions=instructions,
                    mcp_servers=[mcp_server], # Pass the MCP client instance
                    model=model
                )
                
                query = """Summarize the latest news on AI in healthcare the last month,informative,key developments and breakthroughs"""
                print(f"\nRunning agent with query: '{query}'")
                
                result = await Runner.run(starting_agent=agent, input=query,run_config=config)
                
                print("\n" + "=" * 50 + "\n")
                print("Final Agent Response:")
                print(result.final_output)

            except Exception as e:
                print(f"An error occurred during agent execution: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An unhandled error occurred in the script: {e}")
