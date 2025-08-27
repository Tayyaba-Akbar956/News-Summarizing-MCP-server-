from mcp.server.fastmcp import FastMCP
import requests
from textblob import TextBlob

mcp = FastMCP("NewsFetcher")
api_key = "a31b92c3696a4325bacf3dc803fdc06a"

@mcp.tool(
        name = "fetch_news",
        title = "Fetch News Articles",
        description = "Fetches news articles based on a given topic",
)
def fetch_news(topic: str, limit: int = 5) -> list:
    url = f"https://newsapi.org/v2/everything?q={topic}&apiKey={api_key}"
    response = requests.get(url).json()
    articles = response.get("articles", [])[:limit]
    return [{"title": article["title"], "content": article["content"]} for article in articles]


@mcp.resource(uri = "summarizer://news_sources",
              mime_type="text/plain",
)
def news_sources() -> list:
    url = f"https://newsapi.org/v2/top-headlines/sources?apiKey={api_key}"
    response = requests.get(url).json()
    return [source["name"] for source in response.get("sources", [])]

@mcp.resource(
        uri = "summarizer://api_status",
        mime_type="application/json",
)
def api_status() -> dict:
    return {"note": "Check NewsAPI dashboard for rate limits"}

@mcp.prompt()
def news_summarizing_prompt(
    topic: str,
    time_frame: str = "7 days",
    tone: str = "neutral",
    focus: str = "broad overview",
    
    
) -> str:
    return """Search for and summarize recent news articles on {topic} 
    from credible sources published within the last {time_frame}. Provide a concise summary 
      (100-150 words per article, covering 3-5 articles) that includes the main points,
        key findings, and any significant quotes or data. Organize summaries in bullet points, 
        each with the article title, source, publication date, and a brief analysis of its relevance 
        to {topic}. Ensure the tone is {tone} and focus on {focus}. 
        Exclude opinion pieces or unverified sources unless specified. If no relevant articles are found, 
        suggest alternative topics or sources. Include a short concluding paragraph synthesizing common 
        themes or trends across the articles."""


app = mcp.streamable_http_app()

