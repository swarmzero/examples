import os
import requests


from dotenv import load_dotenv
load_dotenv()

langtrace_api_key = os.getenv("LANGTRACE_API_KEY", "")
if langtrace_api_key:
    from langtrace_python_sdk import langtrace
    langtrace.init(
        api_key=langtrace_api_key, 
        disable_instrumentations={ "only": ["sqlalchemy"] }
    )

from datetime import datetime, timedelta
from swarmzero import Agent
from newsapi import NewsApiClient
from typing import Optional, Dict, List, Literal


newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))
page_size = 10
page = 1



def fetch_latest_news_gdelt(query: str) -> Optional[str]:
    """
    Fetches the latest news articles based on the user query.

    :param query: The query to search for in the news articles.
    :return: A summary of the latest news articles, or None if an error occurs or the articles cannot be found.
    """
    url = f"https://api.gdeltproject.org/api/v2/doc/doc?query={query}&mode=artlist&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get("articles", [])
        if articles:
            summary = "\n\n".join([f"Title: {article.get('title')}\nLink: {article.get('url')}" for article in articles[:5]])
            return summary.strip()
        else:
            return "No articles found."
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def fetch_top_headlines(query: str, sources: Optional[str], category: Optional[str], language: str, country: Optional[str], page_size: int = 10, page: int = 1) -> List[Dict[str, str]]:
    """
    Fetches top headlines based on query parameters.
    
    Args:
        query: Search term.
        sources: Comma-separated string of source IDs (Optional).
        category: News category (e.g., 'business') (Optional).
        language: Language of the news (e.g., 'en').
        country: Country code (e.g., 'us') (Optional).
        page_size: Number of articles to return per page (default is 10).
        page: Page number to return (default is 1).

    Returns:
        List of dictionaries with title and url of top headlines.
    """
    # Ensure we don't mix sources with category or country
    if sources:
        top_headlines = newsapi.get_top_headlines(q=query,
                                                  sources=sources,
                                                  language=language,
                                                  page_size=page_size,
                                                  page=page)
    else:
        top_headlines = newsapi.get_top_headlines(q=query,
                                                  category=category,
                                                  language=language,
                                                  country=country,
                                                  page_size=page_size,
                                                  page=page)
    
    results = []
    if top_headlines['status'] == 'ok':
        for headline in top_headlines['articles']:  # Access the articles list
            results.append({
                "title": headline['title'],
                "url": headline['url']
            })
    
    return results
    
    if top_headlines['status'] == 'ok':
        for headline in top_headlines['articles']:  # Access the articles list
            results.append({
                "title": headline['title'],
                "url": headline['url']
            })
    return results  # Return results either way (empty list if no data)

def fetch_all_articles(query: str, sources: str, domains: str, to: str, language: str, sort_by: str) -> List[Dict[str, str]]:
    """
    Fetches all articles matching the search criteria.
    
    Args:
        query: Search term.
        sources: Comma-separated string of source IDs.
        domains: Comma-separated string of domains to restrict search.
        to: Ending date of articles (YYYY-MM-DD).
        language: Language of the news (e.g., 'en').
        sort_by: Criteria to sort results (e.g., 'relevancy').

    Returns:
        List of articles' titles and urls.
    """

    today = datetime.today()
    date_28_days_ago = today - timedelta(days=28)
    formatted_date = date_28_days_ago.strftime("%Y-%m-%d")

    all_articles = newsapi.get_everything(q=query,
                                          sources=sources,
                                          domains=domains,
                                          to=to,
                                          language=language,
                                          sort_by=sort_by,
                                          page_size=page_size,
                                          page=page,
                                          from_param=formatted_date)
    
    if all_articles['status'] == 'ok':
        summary = "\n\n".join([f"Title: {article['title']}\nLink: {article['url']}" for article in all_articles['articles']])
        return summary.strip()
        # for article in all_articles['articles']:
        #     results.append({
        #         "title": article['title'],
        #         "url": article['url']
        #     })
    return "Couldn't get the news"

def fetch_news_sources(category: Literal["business", "technology", "entertainment", "sports", "health", "science", "general"] = "general") -> List[str]:
    """
    Fetches all available news sources.

    Args:
        category: The category of news sources to fetch.

    Returns:
        List of available news sources.
    """
    results = []
    sources = newsapi.get_sources(category=category)
    
    if sources['status'] == 'ok':
        for source in sources['sources']:
            results.append(source['id'])
    else:
        results = ['google-news']  # Fallback option
    return results

if __name__ == "__main__":
    my_agent = Agent(
       name="news_agent",
       functions=[fetch_all_articles],
       config_path="./swarmzero_config.toml",
       instruction="Use appropriate tools to answer the questions related to the news.",
    )
    
    my_agent.run()
