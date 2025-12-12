from typing import List, Dict, Optional
from datetime import datetime
import logging
from .base import BaseScraper

logger = logging.getLogger(__name__)


class TwitterScraper(BaseScraper):
    """
    Scraper for Twitter/X content.

    Note: Twitter requires API access for proper scraping.
    This implementation uses web scraping as a fallback,
    but for production use, Twitter API v2 (via Tweepy) is recommended.
    """

    @property
    def source_name(self) -> str:
        return "twitter"

    @property
    def base_url(self) -> str:
        return "https://twitter.com"

    async def get_article_urls(self, search_term: str) -> List[str]:
        """
        Get Twitter search results.

        Note: Twitter heavily restricts web scraping.
        For production, use Twitter API v2 with Tweepy.
        """
        # Twitter search URL (may require login)
        # For production, implement with Tweepy:
        #
        # import tweepy
        # client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        # tweets = client.search_recent_tweets(
        #     query=search_term,
        #     max_results=100,
        #     tweet_fields=['created_at', 'author_id', 'text']
        # )

        logger.warning(
            "Twitter scraping requires API access. "
            "Please configure TWITTER_BEARER_TOKEN for production use."
        )
        return []

    async def parse_article(self, url: str) -> Optional[Dict]:
        """Parse a Twitter post/thread"""
        # Twitter requires API access for reliable parsing
        return None

    async def search_with_api(self, search_term: str, bearer_token: str) -> List[Dict]:
        """
        Search Twitter using the official API v2.
        Requires Twitter API Bearer Token.
        """
        try:
            import tweepy

            client = tweepy.Client(bearer_token=bearer_token)

            tweets = client.search_recent_tweets(
                query=f"{search_term} lang:pt -is:retweet",
                max_results=50,
                tweet_fields=['created_at', 'author_id', 'text', 'public_metrics'],
                expansions=['author_id'],
                user_fields=['username', 'name']
            )

            if not tweets.data:
                return []

            # Create user lookup
            users = {user.id: user for user in tweets.includes.get('users', [])}

            results = []
            for tweet in tweets.data:
                author = users.get(tweet.author_id)
                author_name = author.name if author else "Unknown"
                author_username = author.username if author else "unknown"

                results.append({
                    "title": tweet.text[:100] + "..." if len(tweet.text) > 100 else tweet.text,
                    "summary": None,
                    "content": tweet.text,
                    "url": f"https://twitter.com/{author_username}/status/{tweet.id}",
                    "image_url": None,
                    "author": f"@{author_username} ({author_name})",
                    "published_at": tweet.created_at.isoformat() if tweet.created_at else None,
                    "source": "twitter",
                    "scraped_at": datetime.utcnow().isoformat(),
                    "metrics": {
                        "likes": tweet.public_metrics.get('like_count', 0) if tweet.public_metrics else 0,
                        "retweets": tweet.public_metrics.get('retweet_count', 0) if tweet.public_metrics else 0,
                        "replies": tweet.public_metrics.get('reply_count', 0) if tweet.public_metrics else 0,
                    }
                })

            return results

        except ImportError:
            logger.error("Tweepy not installed. Install with: pip install tweepy")
            return []
        except Exception as e:
            logger.error(f"Error searching Twitter: {e}")
            return []
