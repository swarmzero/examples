import asyncio
import logging

from swarmzero import Agent, Swarm
from swarmzero.sdk_context import SDKContext

from app.tools import (
    search_google,
    map_url_pages,
    scrape_url,
    save_as_local_pdf,
)
from app.tools.publishers import (
    publish_to_google_docs,
    publish_to_sharepoint,
    publish_to_confluence,
)

import dotenv

dotenv.load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)


config_path = "./swarmzero_config.toml"
sdk_context = SDKContext(config_path=config_path)

google_search_agent = Agent(
    name="Google Search Agent",
    instruction="""You are a Google Search Agent specialized in searching the web.
    Perform searches based on the user's research topic and provide a list of relevant website URLs.
    Output should be a JSON object with the following structure:
    {
        "objective": "<research_topic>",
        "results": [
            {
                "title": "<title>",
                "link": "<url>",
                "snippet": "<snippet>"
            },
            ...
        ]
    }""",
    functions=[search_google],
    config_path=config_path,
    swarm_mode=True,
)

map_url_agent = Agent(
    name="Map URL Agent",
    instruction="""You are a Map URL Agent specialized in mapping web pages from provided website URLs.
    For each URL, identify and list relevant subpages that align with the user's research objective.
    Output should be a JSON object with the following structure:
    {
        "objective": "<research_objective>",
        "results": ["<subpage_url1>", "<subpage_url2>", ...]
    }""",
    functions=[map_url_pages],
    config_path=config_path,
    swarm_mode=True,
)

website_scraper_agent = Agent(
    name="Website Scraper Agent",
    instruction="""You are a Website Scraper Agent specialized in extracting content from mapped URLs.
    Scrape the necessary information required for analysis and ensure the content is clean and structured.
    Output should be a JSON object with the following structure:
    {
        "objective": "<research_objective>",
        "results": "<scraped_content>"
    }""",
    functions=[scrape_url],
    config_path=config_path,
    swarm_mode=True,
)

analyst_agent = Agent(
    name="Analyst Agent",
    instruction="""You are an Analyst Agent that examines scraped website content and extracts structured data.
    Analyze the content to identify key themes, entities, and insights relevant to the research objective.
    Provide your analysis as a JSON object in the following format:
    {
        "objective": "<research_objective>",
        "analysis": {
            "key_themes": [...],
            "entities": [...],
            "insights": [...]
        }
    }""",
    functions=[],
    config_path=config_path,
    swarm_mode=True,
)

publisher_agent = Agent(
    name="Publisher Agent",
    instruction="""You are a Publisher Agent that disseminates research findings to various platforms.
    Use as much of the content provided to you as possible. The final output should be at least 750 words.
    You will be told whether to publish the analyzed data to Google Docs, SharePoint, Confluence or save it as a local PDF.
    If they do not specify, then always default to saving as a local PDF as `./swarmzero-data/output/<title>.pdf`.""",
    functions=[
        save_as_local_pdf,
        publish_to_google_docs,
        publish_to_sharepoint,
        publish_to_confluence,
    ],
    config_path=config_path,
    swarm_mode=True,
)


research_swarm = Swarm(
    name="Research Swarm",
    description="A swarm of AI Agents that can research arbitrary topics.",
    instruction="""You are the leader of a research team that produces new research for user-provided topics.

    Upon receiving a research topic, execute the following steps in order:
        
    1. **Search the Web:** Utilize the Google Search Agent to find relevant websites based on the user's research topic.
    2. **Map Webpages:** Use the Map URL Agent to identify and list pertinent subpages from the search results. Provide it with the relevant objective.
                        If no subpages can be found in all of the URLs, return to step 1 and try a different query.
    3. **Scrape Content:** Call the Website Scraper Agent to extract necessary information from the mapped URLs.
    4. **Analyze Content:** Use the Analyst Agent to process the scraped content and generate structured JSON data.
    5. **Publish Findings:** Finally, instruct the Publisher Agent to output the final analysis.
                        Provide a concise title for the publisher along with the content from the Analyst Agent.
                        Inform this agent about where the user would like to publish the research.
                        If the user does not specify how to publish the research, save the research as a local PDF.

    If an agent is unable to properly execute its task, retry it with a different prompt and/or inputs.
    Ensure each agent completes its task before proceeding to the next step.
    Maintain clear and concise communication throughout the process.
    You must publish the results of any research conducted.""",
    agents=[
        google_search_agent,
        map_url_agent,
        website_scraper_agent,
        analyst_agent,
        publisher_agent,
    ],
    functions=[],
    sdk_context=sdk_context,
    max_iterations=99,
)


async def main():
    print(
        "\n\nWelcome to the Research Swarm!\nVisit https://SwarmZero.ai to learn more.\nType 'exit' to quit.\n"
    )

    while True:
        prompt = input("\nWhat would you like to research? \n\n")
        if prompt.lower() == "exit":
            break
        try:
            logging.info(f"Research topic received: '{prompt}'")
            response = await research_swarm.chat(prompt)
            print("\nResearch Findings:\n")
            print(response)
        except Exception as e:
            logging.error(f"An error occurred during the research process: {e}")
            print(
                "\nAn error occurred while processing your research topic. Please try again.\n"
            )


if __name__ == "__main__":
    asyncio.run(main())
