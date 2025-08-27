import asyncio
import os
from dotenv import load_dotenv, find_dotenv

from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel, Runner,RunConfig
from agents.mcp import MCPServerStreamableHttp, MCPServerStreamableHttpParams


_: bool = load_dotenv(find_dotenv())

# URL of our standalone MCP server (from shared_mcp_server)
MCP_SERVER_URL = "http://localhost:8000/mcp/" # Ensure this matches your running server

gemini_api_key = os.getenv("GEMINI_API_KEY")

#Reference: https://ai.google.dev/gemini-api/docs/openai
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

config = RunConfig(
    model = model,
    model_provider=client,
    tracing_disabled = True
) 

async def main():
    # 1. Configure parameters for the MCPServerStreamableHttp client
    # These parameters tell the SDK how to reach the MCP server.
    mcp_params = MCPServerStreamableHttpParams(url=MCP_SERVER_URL)

    async with MCPServerStreamableHttp(params=mcp_params, name="MySharedMCPServerClient",cache_tools_list=True) as mcp_server:
        try:
            prompts_result = await mcp_server.list_prompts()
            for prompt in prompts_result.prompts:
                print(f"Prompt: {prompt.name} - {prompt.description}")

            tools = await mcp_server.list_tools()
            print(f"Tools: {tools}")
 
            assistant = Agent(
                name="MyMCPConnectedAssistant",
                instructions="You are a helpful assistant connected to an MCP server with various tools.",
                mcp_servers=[mcp_server],
                model=model
            )

            result = await Runner.run(assistant,
                                    input("Enter your query: "),
                                    run_config= config)
            print(f"\n\n[AGENT RESPONSE]: {result.final_output}")

        except Exception as e:
            print(f"An error occurred during agent setup or tool listing: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An unhandled error occurred in the agent script: {e}")

