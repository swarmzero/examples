import os

import agentops
from dotenv import load_dotenv
from swarmzero import Agent
from tavily import TavilyClient

load_dotenv()
agentops.init(os.getenv("AGENTOPS_API_KEY"))
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


async def web_search(query: str) -> dict:
    response = tavily_client.search(query)
    results = []
    for result in response["results"][:3]:
        results.append({"title": result["title"], "url": result["url"], "content": result["content"]})
    return results


async def extract_from_urls(urls: list[str]) -> dict:
    response = tavily_client.extract(urls=urls)

    if response["failed_results"]:
        print(f"Failed to extract from {response['failed_results']}")

    results = []
    for result in response["results"]:
        results.append({"url": result["url"], "raw_content": result["raw_content"]})

    return results


if __name__ == "__main__":
    my_agent = Agent(
        name="workflow-assistant",
        functions=[
            web_search,
            extract_from_urls,
        ],
        config_path="./swarmzero_config.toml",
        instruction="You are a helpful assistant that can search the web and extract information from a given URL.",
    )

    my_agent.run()  # see agent API at localhost:8000/docs
