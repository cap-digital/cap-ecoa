import logging
from typing import List, Dict
from datetime import datetime
from ..database import get_supabase
from .sentiment import analyze_news_sentiment
from .scraper import G1Scraper, CNNScraper
from .scraper.twitter import TwitterScraper
from .scraper.threads import ThreadsScraper

logger = logging.getLogger(__name__)


class NewsProcessor:
    """Process and store scraped news articles"""

    def __init__(self):
        self.scrapers = {
            "g1": G1Scraper(),
            "cnn": CNNScraper(),
            "twitter": TwitterScraper(),
            "threads": ThreadsScraper(),
        }

    async def get_all_monitored_terms(self) -> List[str]:
        """Get all unique monitored terms from all users"""
        supabase = get_supabase()

        result = supabase.table("ecoa_monitored_terms").select("term").eq(
            "is_active", True
        ).execute()

        terms = list(set([t["term"] for t in result.data])) if result.data else []
        return terms

    async def scrape_all_sources(self, terms: List[str] = None) -> List[Dict]:
        """Scrape all news sources for the given terms"""
        if terms is None:
            terms = await self.get_all_monitored_terms()

        if not terms:
            logger.info("No monitored terms found. Skipping scraping.")
            return []

        logger.info(f"Scraping for {len(terms)} terms: {terms}")

        all_articles = []

        # Scrape each source
        for source_name, scraper in self.scrapers.items():
            try:
                logger.info(f"Scraping {source_name}...")
                articles = await scraper.scrape(terms)
                all_articles.extend(articles)
                logger.info(f"Found {len(articles)} articles from {source_name}")
            except Exception as e:
                logger.error(f"Error scraping {source_name}: {e}")

        return all_articles

    async def process_and_store(self, articles: List[Dict]) -> int:
        """Process articles (sentiment analysis) and store in database"""
        supabase = get_supabase()
        stored_count = 0

        for article in articles:
            try:
                # Check if article already exists (by URL)
                existing = supabase.table("ecoa_news").select("id").eq(
                    "url", article["url"]
                ).execute()

                if existing.data:
                    logger.debug(f"Article already exists: {article['url']}")
                    continue

                # Analyze sentiment
                sentiment, sentiment_score = analyze_news_sentiment(
                    article.get("title", ""),
                    article.get("content")
                )

                # Prepare data for insertion
                news_data = {
                    "title": article["title"],
                    "summary": article.get("summary"),
                    "content": article.get("content"),
                    "url": article["url"],
                    "image_url": article.get("image_url"),
                    "author": article.get("author"),
                    "source": article["source"],
                    "published_at": article.get("published_at"),
                    "scraped_at": article.get("scraped_at", datetime.utcnow().isoformat()),
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                }

                # Insert into database
                result = supabase.table("ecoa_news").insert(news_data).execute()

                if result.data:
                    stored_count += 1
                    news_id = result.data[0]["id"]

                    # Create term matches
                    await self.create_term_matches(news_id, article)

            except Exception as e:
                logger.error(f"Error processing article {article.get('url')}: {e}")

        logger.info(f"Stored {stored_count} new articles")
        return stored_count

    async def create_term_matches(self, news_id: str, article: Dict):
        """Create matches between news and monitored terms"""
        supabase = get_supabase()

        # Get all monitored terms
        terms_result = supabase.table("ecoa_monitored_terms").select("id, term").eq(
            "is_active", True
        ).execute()

        if not terms_result.data:
            return

        title_lower = (article.get("title") or "").lower()
        content_lower = (article.get("content") or "").lower()

        for term_data in terms_result.data:
            term = term_data["term"].lower()
            term_id = term_data["id"]

            # Count occurrences
            count = title_lower.count(term) + content_lower.count(term)

            if count > 0:
                try:
                    supabase.table("ecoa_news_term_matches").insert({
                        "news_id": news_id,
                        "term_id": term_id,
                        "match_count": count
                    }).execute()
                except Exception as e:
                    logger.error(f"Error creating term match: {e}")

    async def run_scraping_job(self) -> Dict:
        """Run a complete scraping job"""
        start_time = datetime.utcnow()

        # Scrape all sources
        articles = await self.scrape_all_sources()

        # Process and store
        stored_count = await self.process_and_store(articles)

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        return {
            "status": "completed",
            "articles_found": len(articles),
            "articles_stored": stored_count,
            "duration_seconds": duration,
            "timestamp": end_time.isoformat()
        }


# Global processor instance
news_processor = NewsProcessor()
