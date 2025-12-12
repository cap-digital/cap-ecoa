import asyncio
from celery import Celery
from ..config import settings

# Celery configuration
celery_app = Celery(
    "ecoa_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    beat_schedule={
        "scrape-news-every-30-minutes": {
            "task": "app.tasks.scraping.scrape_news_task",
            "schedule": settings.SCRAPE_INTERVAL_MINUTES * 60,  # Convert to seconds
        },
    },
)


@celery_app.task(name="app.tasks.scraping.scrape_news_task")
def scrape_news_task():
    """Celery task to run the news scraping job"""
    from ..services.news_processor import news_processor

    # Run async function in sync context
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(news_processor.run_scraping_job())

    return result


@celery_app.task(name="app.tasks.scraping.scrape_term_task")
def scrape_term_task(term: str):
    """Celery task to scrape news for a specific term"""
    from ..services.news_processor import news_processor

    loop = asyncio.get_event_loop()
    articles = loop.run_until_complete(news_processor.scrape_all_sources([term]))
    stored = loop.run_until_complete(news_processor.process_and_store(articles))

    return {
        "term": term,
        "articles_found": len(articles),
        "articles_stored": stored
    }
