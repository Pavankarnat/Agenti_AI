"""
Web search tool for finding information across the internet.
Supports DuckDuckGo search via ddgs library.
"""

import logging
from typing import List
from duckduckgo_search import DDGS
from app.models.schemas import SearchResult, SearchResults

logger = logging.getLogger(__name__)


class WebSearchTool:
    """Tool for performing web searches."""

    def __init__(self, max_results: int = 5, timeout: int = 10):
        """
        Initialize the web search tool.

        Args:
            max_results: Maximum number of search results to return
            timeout: Request timeout in seconds
        """
        self.max_results = max_results
        self.timeout = timeout

    def search(self, query: str, max_results: int = None) -> SearchResults:
        """
        Perform a web search using DuckDuckGo.

        Args:
            query: The search query
            max_results: Override max_results for this search

        Returns:
            SearchResults object with search results
        """

        if max_results is None:
            max_results = self.max_results

        try:
            logger.info(f"Performing web search for: {query}")

            # Use context manager (recommended by ddgs)
            with DDGS(timeout=self.timeout) as ddgs:
                results = list(ddgs.text(query, max_results=max_results))

            search_results = []

            for result in results:
                search_result = SearchResult(
                    title=result.get("title") or result.get("name", ""),
                    url=result.get("href") or result.get("link", ""),
                    snippet=result.get("body") or result.get("description", ""),
                    source="DuckDuckGo"
                )

                # Ensure URL exists
                if search_result.url:
                    search_results.append(search_result)

            logger.info(f"Found {len(search_results)} results for query: {query}")

            return SearchResults(
                query=query,
                results=search_results,
                total_results=len(search_results)
            )

        except Exception as e:
            logger.error(f"Error performing web search for '{query}': {str(e)}")

            return SearchResults(
                query=query,
                results=[],
                total_results=0
            )

    def search_multiple(self, queries: List[str]) -> List[SearchResults]:
        """
        Perform multiple web searches.

        Args:
            queries: List of search queries

        Returns:
            List of SearchResults objects
        """

        results = []

        for query in queries:
            result = self.search(query)
            results.append(result)

        return results


# Global instance
web_search = WebSearchTool()


def search(query: str, max_results: int = 5) -> SearchResults:
    """
    Convenience function for web search.

    Args:
        query: The search query
        max_results: Maximum number of results to return

    Returns:
        SearchResults object
    """

    return web_search.search(query, max_results)


if __name__ == "__main__":

    # Example usage
    results = search("Latest AI advancements 2024")

    print(f"\nQuery: {results.query}")
    print(f"Total Results: {results.total_results}")

    for i, result in enumerate(results.results, 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Snippet: {result.snippet[:120]}...")