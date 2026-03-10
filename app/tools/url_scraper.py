"""
URL scraper tool for extracting content from web pages.
"""
import logging
from typing import Optional
import requests
from bs4 import BeautifulSoup
from app.models.schemas import ExtractedURL
from datetime import datetime

logger = logging.getLogger(__name__)


class URLScraper:
    """Tool for scraping and extracting content from URLs."""

    def __init__(self, timeout: int = 10, max_content_length: int = 50000):
        """
        Initialize the URL scraper.
        
        Args:
            timeout: Request timeout in seconds
            max_content_length: Maximum content length to extract in characters
        """
        self.timeout = timeout
        self.max_content_length = max_content_length
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def scrape(self, url: str) -> ExtractedURL:
        """
        Scrape and extract content from a URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            ExtractedURL object with extracted content
        """
        try:
            logger.info(f"Scraping URL: {url}")
            
            # Fetch the page
            response = requests.get(
                url, 
                headers=self.headers, 
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else ""
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            content = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit content length
            if len(content) > self.max_content_length:
                content = content[:self.max_content_length]
            
            word_count = len(content.split())
            
            logger.info(f"Successfully scraped {url} ({word_count} words)")
            
            return ExtractedURL(
                url=url,
                title=title,
                content=content,
                word_count=word_count,
                extraction_date=datetime.now(),
                extraction_status="success"
            )
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to scrape {url}: {str(e)}")
            return ExtractedURL(
                url=url,
                extraction_status="failed",
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return ExtractedURL(
                url=url,
                extraction_status="failed",
                error_message=str(e)
            )

    def scrape_multiple(self, urls: list) -> list:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of ExtractedURL objects
        """
        results = []
        for url in urls:
            result = self.scrape(url)
            results.append(result)
        return results


# Global instance
url_scraper = URLScraper()


def scrape(url: str) -> ExtractedURL:
    """
    Convenience function for URL scraping.
    
    Args:
        url: The URL to scrape
        
    Returns:
        ExtractedURL object
    """
    return url_scraper.scrape(url)


if __name__ == "__main__":
    # Example usage
    url = "https://www.example.com"
    result = scrape(url)
    print(f"URL: {result.url}")
    print(f"Title: {result.title}")
    print(f"Status: {result.extraction_status}")
    print(f"Content preview: {result.content[:200]}...")
    print(f"Word count: {result.word_count}")
