from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import quote_plus
import re
import logging
from .base import BaseScraper

logger = logging.getLogger(__name__)


class G1Scraper(BaseScraper):
    """Scraper for G1 (Globo) news"""

    @property
    def source_name(self) -> str:
        return "g1"

    @property
    def base_url(self) -> str:
        return "https://g1.globo.com"

    async def get_article_urls(self, search_term: str) -> List[str]:
        """Search G1 for articles containing the search term"""
        encoded_term = quote_plus(search_term)
        search_url = f"https://g1.globo.com/busca/?q={encoded_term}&order=recent"

        html = await self.fetch_page(search_url)
        if not html:
            return []

        soup = self.parse_html(html)
        urls = []

        # G1 search results structure
        results = soup.select(".widget--info__text-container a")

        for link in results:
            href = link.get("href", "")
            if href and "g1.globo.com" in href and "/noticia/" in href:
                if href not in urls:
                    urls.append(href)

        # Also try alternative selectors
        if not urls:
            results = soup.select("a[href*='/noticia/']")
            for link in results:
                href = link.get("href", "")
                if href and href.startswith("http"):
                    if href not in urls:
                        urls.append(href)

        return urls[:15]

    async def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a G1 article page"""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Title
            title_elem = soup.select_one("h1.content-head__title") or soup.select_one("h1")
            title = self.clean_text(title_elem.get_text()) if title_elem else None

            if not title:
                return None

            # Summary/Subtitle
            summary_elem = soup.select_one(".content-head__subtitle") or soup.select_one("h2.content-head__subtitle")
            summary = self.clean_text(summary_elem.get_text()) if summary_elem else None

            # Content
            content_elem = soup.select_one(".mc-article-body") or soup.select_one("article")
            content = ""
            if content_elem:
                paragraphs = content_elem.select("p")
                content = " ".join([self.clean_text(p.get_text()) for p in paragraphs])

            # Author
            author_elem = soup.select_one(".content-publication-data__from") or soup.select_one("address")
            author = self.clean_text(author_elem.get_text()) if author_elem else None
            if author:
                author = author.replace("Por", "").strip()

            # Published date
            date_elem = soup.select_one("time[datetime]")
            published_at = None
            if date_elem:
                datetime_str = date_elem.get("datetime")
                if datetime_str:
                    try:
                        published_at = datetime.fromisoformat(datetime_str.replace("Z", "+00:00")).isoformat()
                    except:
                        pass

            # Image
            image_elem = soup.select_one(".content-media__image img") or soup.select_one("figure img")
            image_url = image_elem.get("src") if image_elem else None

            return {
                "title": title,
                "summary": summary,
                "content": content[:5000] if content else None,  # Limit content size
                "url": url,
                "image_url": image_url,
                "author": author,
                "published_at": published_at
            }

        except Exception as e:
            logger.error(f"Error parsing G1 article {url}: {e}")
            return None
