
import os

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


def search_web(query: str, max_results: int = 5) -> dict:
    """Search the web and return results with source URLs."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Please provide a search query.")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError("The web search API key is not configured.")

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query.strip(),
        max_results=max(1, min(max_results, 5)),
        search_depth="basic",
    )

    results = []

    for item in response.get("results", []):
        url = item.get("url")
        title = item.get("title")
        content = item.get("content")

        if not url or not title:
            continue

        results.append({
            "title": str(title)[:300],
            "url": str(url),
            "snippet": str(content or "")[:1200],
        })

    return {
        "query": query.strip(),
        "results": results,
    }
