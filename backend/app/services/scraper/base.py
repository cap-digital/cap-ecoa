from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Base class for all news scrapers"""

    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self.timeout = 30.0

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Return the source identifier (e.g., 'g1', 'cnn')"""
        pass

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL for the news source"""
        pass

    @abstractmethod
    async def get_article_urls(self, search_term: str) -> List[str]:
        """Get list of article URLs for a search term"""
        pass

    @abstractmethod
    async def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a single article and return its data"""
        pass

    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL"""
        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML string into BeautifulSoup object"""
        return BeautifulSoup(html, "lxml")

    async def scrape(self, search_terms: List[str]) -> List[Dict]:
        """
        Main scraping method.
        Searches for articles matching the given terms.
        """
        all_articles = []
        seen_urls = set()

        for term in search_terms:
            try:
                urls = await self.get_article_urls(term)
                logger.info(f"Found {len(urls)} URLs for term '{term}' on {self.source_name}")

                for url in urls[:10]:  # Limit to 10 articles per term
                    if url in seen_urls:
                        continue

                    seen_urls.add(url)
                    article = await self.parse_article(url)

                    if article:
                        article["source"] = self.source_name
                        article["scraped_at"] = datetime.utcnow().isoformat()
                        all_articles.append(article)

            except Exception as e:
                logger.error(f"Error scraping {self.source_name} for term '{term}': {e}")

        return all_articles

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        # Remove extra whitespace
        text = " ".join(text.split())
        return text.strip()
