from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import quote_plus
import logging
from .base import BaseScraper

logger = logging.getLogger(__name__)


class CNNScraper(BaseScraper):
    """Scraper for CNN Brasil news"""

    @property
    def source_name(self) -> str:
        return "cnn"

    @property
    def base_url(self) -> str:
        return "https://www.cnnbrasil.com.br"

    async def get_article_urls(self, search_term: str) -> List[str]:
        """Search CNN Brasil for articles containing the search term"""
        encoded_term = quote_plus(search_term)
        search_url = f"https://www.cnnbrasil.com.br/?s={encoded_term}&orderby=date"

        html = await self.fetch_page(search_url)
        if not html:
            return []

        soup = self.parse_html(html)
        urls = []

        # CNN Brasil search results
        results = soup.select("a.home__list__tag")
        for link in results:
            href = link.get("href", "")
            if href and "cnnbrasil.com.br" in href:
                if href not in urls:
                    urls.append(href)

        # Alternative selectors
        if not urls:
            results = soup.select("article a[href*='cnnbrasil.com.br']")
            for link in results:
                href = link.get("href", "")
                if href and href.startswith("http"):
                    if href not in urls:
                        urls.append(href)

        # Try another pattern
        if not urls:
            results = soup.select(".news-item a, .post-item a, h2 a, h3 a")
            for link in results:
                href = link.get("href", "")
                if href and "cnnbrasil.com.br" in href and "/noticia" in href:
                    if href not in urls:
                        urls.append(href)

        return urls[:15]

    async def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a CNN Brasil article page"""
        html = await self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)

        try:
            # Title
            title_elem = soup.select_one("h1.post__title") or soup.select_one("h1")
            title = self.clean_text(title_elem.get_text()) if title_elem else None

            if not title:
                return None

            # Summary
            summary_elem = soup.select_one(".post__excerpt") or soup.select_one("h2.post__excerpt")
            summary = self.clean_text(summary_elem.get_text()) if summary_elem else None

            # Content
            content_elem = soup.select_one(".post__content") or soup.select_one("article .content")
            content = ""
            if content_elem:
                paragraphs = content_elem.select("p")
                content = " ".join([self.clean_text(p.get_text()) for p in paragraphs])

            # Author
            author_elem = soup.select_one(".author__name") or soup.select_one(".post__author")
            author = self.clean_text(author_elem.get_text()) if author_elem else None

            # Published date
            date_elem = soup.select_one("time[datetime]") or soup.select_one(".post__data time")
            published_at = None
            if date_elem:
                datetime_str = date_elem.get("datetime")
                if datetime_str:
                    try:
                        published_at = datetime.fromisoformat(datetime_str.replace("Z", "+00:00")).isoformat()
                    except:
                        pass

            # Image
            image_elem = soup.select_one(".post__thumbnail img") or soup.select_one("figure img")
            image_url = image_elem.get("src") if image_elem else None

            return {
                "title": title,
                "summary": summary,
                "content": content[:5000] if content else None,
                "url": url,
                "image_url": image_url,
                "author": author,
                "published_at": published_at
            }

        except Exception as e:
            logger.error(f"Error parsing CNN article {url}: {e}")
            return None
