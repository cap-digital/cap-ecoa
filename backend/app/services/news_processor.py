import logging
import hashlib
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import News, MonitoredTerm, NewsTermMatch, SentimentType
from .sentiment import analyze_news_sentiment
from .scraper import G1Scraper, CNNScraper
from .scraper.twitter import TwitterScraper
from .scraper.threads import ThreadsScraper

logger = logging.getLogger(__name__)


def get_url_hash(url: str) -> str:
    """Generate SHA256 hash of URL for unique constraint"""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()


class NewsProcessor:
    """Process and store scraped news articles"""

    def __init__(self):
        self.scrapers = {
            "g1": G1Scraper(),
            "cnn": CNNScraper(),
            "twitter": TwitterScraper(),
            "threads": ThreadsScraper(),
        }

    def get_db(self) -> Session:
        """Get a database session"""
        return SessionLocal()

    async def get_all_monitored_terms(self) -> List[str]:
        """Get all unique monitored terms from all users"""
        db = self.get_db()
        try:
            terms = db.query(MonitoredTerm.term).filter(
                MonitoredTerm.is_active == True
            ).distinct().all()
            return [t[0] for t in terms]
        finally:
            db.close()

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
        db = self.get_db()
        stored_count = 0

        try:
            for article in articles:
                try:
                    # Generate URL hash
                    url_hash = get_url_hash(article["url"])

                    # Check if article already exists (by URL hash)
                    existing = db.query(News).filter(News.url_hash == url_hash).first()

                    if existing:
                        logger.debug(f"Article already exists: {article['url']}")
                        continue

                    # Analyze sentiment
                    sentiment_str, sentiment_score = analyze_news_sentiment(
                        article.get("title", ""),
                        article.get("content")
                    )

                    # Convert sentiment string to enum
                    sentiment = None
                    if sentiment_str == "positive":
                        sentiment = SentimentType.POSITIVE
                    elif sentiment_str == "negative":
                        sentiment = SentimentType.NEGATIVE
                    elif sentiment_str == "neutral":
                        sentiment = SentimentType.NEUTRAL

                    # Parse published_at if it's a string
                    published_at = article.get("published_at")
                    if isinstance(published_at, str):
                        try:
                            published_at = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                        except:
                            published_at = None

                    # Create news entry
                    news = News(
                        title=article["title"],
                        summary=article.get("summary"),
                        content=article.get("content"),
                        url=article["url"],
                        url_hash=url_hash,
                        image_url=article.get("image_url"),
                        author=article.get("author"),
                        source=article["source"],
                        published_at=published_at,
                        scraped_at=datetime.utcnow(),
                        sentiment=sentiment,
                        sentiment_score=sentiment_score,
                    )

                    db.add(news)
                    db.commit()
                    db.refresh(news)

                    stored_count += 1

                    # Create term matches
                    await self.create_term_matches(db, news.id, article)

                except Exception as e:
                    db.rollback()
                    logger.error(f"Error processing article {article.get('url')}: {e}")

            logger.info(f"Stored {stored_count} new articles")
            return stored_count
        finally:
            db.close()

    async def create_term_matches(self, db: Session, news_id: str, article: Dict):
        """Create matches between news and monitored terms"""
        # Get all active monitored terms
        terms = db.query(MonitoredTerm).filter(MonitoredTerm.is_active == True).all()

        if not terms:
            return

        title_lower = (article.get("title") or "").lower()
        content_lower = (article.get("content") or "").lower()

        for term_data in terms:
            term = term_data.term.lower()
            term_id = term_data.id

            # Count occurrences
            count = title_lower.count(term) + content_lower.count(term)

            if count > 0:
                try:
                    # Check if match already exists
                    existing = db.query(NewsTermMatch).filter(
                        NewsTermMatch.news_id == news_id,
                        NewsTermMatch.term_id == term_id
                    ).first()

                    if not existing:
                        match = NewsTermMatch(
                            news_id=news_id,
                            term_id=term_id,
                            match_count=count
                        )
                        db.add(match)
                        db.commit()
                except Exception as e:
                    db.rollback()
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
