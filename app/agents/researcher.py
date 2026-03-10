"""
Researcher Agent - Executes searches and extracts content from URLs.
"""
import logging
from typing import List
from app.models.schemas import SearchResults, ExtractedURL, AgentState
from app.tools.web_search import web_search
from app.tools.url_scraper import url_scraper
from app.config import MAX_URL_EXTRACTIONS

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """Agent responsible for conducting research through searches and content extraction."""

    def __init__(self, max_url_extractions: int = MAX_URL_EXTRACTIONS):
        """
        Initialize the Researcher Agent.
        
        Args:
            max_url_extractions: Maximum number of URLs to extract content from
        """
        self.max_url_extractions = max_url_extractions
        self.web_search = web_search
        self.url_scraper = url_scraper

    def execute_searches(self, search_queries: List[str]) -> SearchResults:
        """
        Execute multiple search queries and aggregate results.
        
        Args:
            search_queries: List of search queries to execute
            
        Returns:
            Aggregated SearchResults
        """
        logger.info(f"Executing {len(search_queries)} search queries")
        
        all_results = []
        
        for query in search_queries:
            try:
                results = self.web_search.search(query)
                all_results.extend(results.results)
                logger.info(f"Search '{query}' returned {len(results.results)} results")
            except Exception as e:
                logger.error(f"Error executing search for '{query}': {str(e)}")
        
        # Remove duplicates based on URL
        unique_results = {}
        for result in all_results:
            if result.url not in unique_results:
                unique_results[result.url] = result
        
        final_results = SearchResults(
            query=" | ".join(search_queries),
            results=list(unique_results.values()),
            total_results=len(unique_results)
        )
        
        logger.info(f"Total unique results collected: {final_results.total_results}")
        return final_results

    def extract_content(self, search_results: SearchResults) -> List[ExtractedURL]:
        """
        Extract content from the top URL results.
        
        Args:
            search_results: SearchResults from web search
            
        Returns:
            List of ExtractedURL objects
        """
        urls_to_extract = search_results.results[:self.max_url_extractions]
        logger.info(f"Extracting content from {len(urls_to_extract)} URLs")
        
        extracted_content = []
        
        for search_result in urls_to_extract:
            try:
                logger.info(f"Extracting content from: {search_result.url}")
                extracted = self.url_scraper.scrape(search_result.url)
                
                if extracted.extraction_status == "success":
                    logger.info(f"Successfully extracted {extracted.word_count} words from {search_result.url}")
                    extracted_content.append(extracted)
                else:
                    logger.warning(f"Failed to extract from {search_result.url}: {extracted.error_message}")
                    
            except Exception as e:
                logger.error(f"Error extracting content from {search_result.url}: {str(e)}")
        
        logger.info(f"Extracted content from {len(extracted_content)} URLs successfully")
        return extracted_content

    def conduct_research(self, search_queries: List[str]) -> tuple[SearchResults, List[ExtractedURL]]:
        """
        Conduct complete research: search and extract content.
        
        Args:
            search_queries: List of search queries
            
        Returns:
            Tuple of (SearchResults, List of ExtractedURL)
        """
        logger.info("Starting research conduct")
        
        # Execute searches
        search_results = self.execute_searches(search_queries)
        
        # Extract content from top results
        extracted_content = self.extract_content(search_results)
        
        logger.info("Research conduct completed")
        return search_results, extracted_content


# Global instance
researcher = ResearcherAgent()


def conduct_research(search_queries: List[str]) -> tuple[SearchResults, List[ExtractedURL]]:
    """
    Convenience function to conduct research.
    
    Args:
        search_queries: List of search queries
        
    Returns:
        Tuple of (SearchResults, List of ExtractedURL)
    """
    return researcher.conduct_research(search_queries)


if __name__ == "__main__":
    # Example usage
    queries = [
        "AI memory systems 2024",
        "Agentic memory architecture",
        "Large language model memory optimization"
    ]
    
    search_results, extracted = conduct_research(queries)
    
    print(f"Search Results: {search_results.total_results}")
    for i, result in enumerate(search_results.results[:3], 1):
        print(f"\n{i}. {result.title}")
        print(f"   URL: {result.url}")
    
    print(f"\n\nExtracted Content from {len(extracted)} URLs:")
    for ext in extracted:
        print(f"✓ {ext.url} ({ext.word_count} words)")
