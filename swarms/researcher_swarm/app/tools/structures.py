from pydantic import BaseModel
from typing import List


class SearchResult(BaseModel):
    """Data model for each search result."""

    title: str
    link: str
    snippet: str


class GoogleSearchResults(BaseModel):
    """Structured output for Google Search Agent."""

    objective: str
    results: List[SearchResult]


class MapURLResult(BaseModel):
    """Structured output for Map URL Agent."""

    objective: str
    results: List[str]


class ScrapedContent(BaseModel):
    """Structured output for Website Scraper Agent."""

    objective: str
    results: str
