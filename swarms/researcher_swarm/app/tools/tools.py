import os
import logging

from dotenv import load_dotenv
from fpdf import FPDF
from firecrawl import FirecrawlApp
from serpapi.google_search import GoogleSearch

from app.tools.structures import (
    GoogleSearchResults,
    SearchResult,
    MapURLResult,
    ScrapedContent,
)

load_dotenv()

firecrawl_app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

logging.basicConfig(level=logging.INFO)


def search_google(query: str, objective: str) -> GoogleSearchResults:
    """
    Perform a Google search using SerpAPI and return structured results.

    This function executes a Google search query through SerpAPI and processes the results
    into a structured format using the GoogleSearchResults data class.

    Args:
        query (str): The search query to be executed
        objective (str): The purpose or goal of the search, used for context

    Returns:
        GoogleSearchResults: A structured object containing search results including titles,
            links, and snippets

    Raises:
        Exception: If no organic search results are found in the API response

    Example:
        >>> results = search_google("python programming", "Learn Python basics")
        >>> print(results.results[0].title)
    """
    logging.info(f"Searching Google with query: '{query}' for objective: '{objective}'")
    search_params = {
        "engine": "google",
        "q": query,
        "api_key": os.getenv("SERP_API_KEY"),
    }
    search = GoogleSearch(search_params)
    search_results = search.get_dict().get("organic_results", [])

    if not search_results:
        raise Exception("No organic results found from SerpAPI.")

    structured_results = [
        SearchResult(
            title=result.get("title", ""),
            link=result.get("link", ""),
            snippet=result.get("snippet", ""),
        )
        for result in search_results
        if result.get("link")
    ]

    return GoogleSearchResults(objective=objective, results=structured_results)


def map_url_pages(url: str, objective: str, search_query: str) -> MapURLResult:
    """
    Map all pages of a website that match a search query using Firecrawl.

    This function crawls a website and identifies relevant pages based on a search query,
    returning the results in a structured format.

    Args:
        url (str): The base URL of the website to map
        objective (str): The purpose or goal of the mapping operation
        search_query (str): Query string to filter relevant pages

    Returns:
        MapURLResult: A structured object containing the list of matching URLs found

    Example:
        >>> results = map_url_pages("https://example.com", "Find pricing pages", "pricing")
        >>> for url in results.results:
        ...     print(url)
    """
    logging.info(
        f"Mapping URLs for website: '{url}' with search query: '{search_query}' and objective: '{objective}'"
    )
    map_status = firecrawl_app.map_url(url, params={"search": search_query})

    if map_status.get("status") == "success":
        links = map_status.get("links", [])
        top_links = [link for link in links if link]
        return MapURLResult(objective=objective, results=top_links)
    else:
        return MapURLResult(objective=objective, results=[])


def scrape_url(url: str, objective: str) -> ScrapedContent:
    """
    Scrape content from a specified URL using Firecrawl.

    This function extracts content from a webpage and returns it in a structured format.
    The content is converted to markdown format for better readability and processing.

    Args:
        url (str): The URL to scrape content from
        objective (str): The purpose or goal of the scraping operation

    Returns:
        ScrapedContent: A structured object containing the scraped content

    Raises:
        Exception: If scraping fails or returns empty content

    Example:
        >>> content = scrape_url("https://example.com/about", "Extract company information")
        >>> print(content.results)
    """
    logging.info(f"Scraping URL: '{url}' with objective: '{objective}'")
    scrape_result = firecrawl_app.scrape_url(url, params={"formats": ["markdown"]})

    if not scrape_result:
        raise Exception("Scraping failed or returned empty content.")

    content = scrape_result["markdown"]
    if not content:
        raise Exception(f"No content retrieved from {url}")

    return ScrapedContent(objective=objective, results=content)


def save_as_local_pdf(title: str, results_text: str, pdf_output_path: str) -> str:
    """
    Generate a PDF file containing the provided text content.

    This function creates a formatted PDF document with a header and the provided content.
    The PDF is saved to the specified local path, creating directories if needed.

    Args:
        title (str): The title of the content to be included in the PDF
        results_text (str): The text content to be included in the PDF
        pdf_output_path (str): The full path where the PDF should be saved

    Returns:
        str: The absolute path to the created PDF file, or None if creation fails

    Raises:
        OSError: If there are permission issues or problems creating directories
        Exception: For any other errors during PDF creation

    Example:
        >>> text = "Sample report content\\nWith multiple lines"
        >>> pdf_path = save_as_local_pdf(text, "output/report.pdf")
        >>> print(f"PDF saved to: {pdf_path}")
    """
    try:
        pdf = FPDF()
        pdf.add_page()

        # header
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, title, ln=True, align="C")
        pdf.ln(10)  # line break

        # content
        pdf.set_font("Arial", size=12)
        for line in results_text.strip().split("\n"):
            pdf.multi_cell(0, 10, txt=line.strip())
            pdf.ln(1)

        # ensure the output directory exists
        output_path = os.path.abspath(pdf_output_path)
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        pdf.output(output_path)
        logging.info(f"PDF file created successfully at: {output_path}")
        return output_path

    except Exception as e:
        logging.error(f"Error during PDF creation: {e}")
        return None
