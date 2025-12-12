from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models import User, News, MonitoredTerm, SentimentType
from ..services.auth import get_current_user
from ..schemas.dashboard import (
    StatsResponse,
    TrendResponse,
    TrendPoint,
    SourceStats,
    DashboardResponse
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_user_terms(db: Session, user_id: str, active_only: bool = True):
    """Get user's monitored terms"""
    query = db.query(MonitoredTerm).filter(MonitoredTerm.user_id == user_id)
    if active_only:
        query = query.filter(MonitoredTerm.is_active == True)
    return [t.term for t in query.all()]


def build_term_filter(terms: list):
    """Build SQLAlchemy filter for terms"""
    term_filters = []
    for t in terms:
        term_filters.append(News.title.ilike(f"%{t}%"))
        term_filters.append(News.content.ilike(f"%{t}%"))
    return or_(*term_filters) if term_filters else None


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    terms = get_user_terms(db, current_user.id)
    active_terms = len(terms)

    if not terms:
        return StatsResponse(
            total_news=0,
            news_today=0,
            positive_mentions=0,
            negative_mentions=0,
            neutral_mentions=0,
            active_terms=0
        )

    term_filter = build_term_filter(terms)

    # Total news matching user's terms
    total_news = db.query(News).filter(term_filter).count()

    # News today
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    news_today = db.query(News).filter(
        term_filter,
        News.published_at >= today
    ).count()

    # Sentiment counts
    positive_mentions = db.query(News).filter(
        term_filter,
        News.sentiment == SentimentType.POSITIVE
    ).count()

    negative_mentions = db.query(News).filter(
        term_filter,
        News.sentiment == SentimentType.NEGATIVE
    ).count()

    neutral_mentions = db.query(News).filter(
        term_filter,
        News.sentiment == SentimentType.NEUTRAL
    ).count()

    return StatsResponse(
        total_news=total_news,
        news_today=news_today,
        positive_mentions=positive_mentions,
        negative_mentions=negative_mentions,
        neutral_mentions=neutral_mentions,
        active_terms=active_terms
    )


@router.get("/trends", response_model=list[TrendResponse])
async def get_trends(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    terms = get_user_terms(db, current_user.id)

    if not terms:
        return []

    start_date = datetime.now() - timedelta(days=days)
    trends = []

    for term in terms[:5]:  # Limit to top 5 terms
        # Get news for this term in the date range
        term_filter = or_(
            News.title.ilike(f"%{term}%"),
            News.content.ilike(f"%{term}%")
        )

        news_list = db.query(News).filter(
            term_filter,
            News.published_at >= start_date
        ).all()

        # Group by date
        daily_data = defaultdict(lambda: {"count": 0, "sentiment_sum": 0})

        for news in news_list:
            if news.published_at:
                date_str = news.published_at.strftime("%Y-%m-%d")
                daily_data[date_str]["count"] += 1
                daily_data[date_str]["sentiment_sum"] += news.sentiment_score or 0

        # Build trend points
        data_points = []
        for date_str, values in sorted(daily_data.items()):
            avg_sentiment = values["sentiment_sum"] / values["count"] if values["count"] > 0 else 0
            data_points.append(TrendPoint(
                date=date_str,
                count=values["count"],
                sentiment_avg=round(avg_sentiment, 2)
            ))

        trends.append(TrendResponse(term=term, data=data_points))

    return trends


@router.get("/sources", response_model=list[SourceStats])
async def get_source_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    terms = get_user_terms(db, current_user.id)

    if not terms:
        return []

    term_filter = build_term_filter(terms)

    # Get all news matching terms
    news_list = db.query(News.source).filter(term_filter).all()

    # Count by source
    source_counts = defaultdict(int)
    total = 0

    for (source,) in news_list:
        source_counts[source] += 1
        total += 1

    # Calculate percentages
    stats = []
    for source, count in source_counts.items():
        stats.append(SourceStats(
            source=source,
            count=count,
            percentage=round((count / total * 100) if total > 0 else 0, 1)
        ))

    return sorted(stats, key=lambda x: x.count, reverse=True)


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get all dashboard data
    stats = await get_stats(current_user, db)
    trends = await get_trends(7, current_user, db)
    sources = await get_source_stats(current_user, db)

    # Get recent news
    terms = get_user_terms(db, current_user.id)
    recent_news = []

    if terms:
        term_filter = build_term_filter(terms)

        recent_list = db.query(News).filter(term_filter).order_by(
            News.published_at.desc()
        ).limit(5).all()

        recent_news = [
            {
                "id": n.id,
                "title": n.title,
                "source": n.source,
                "sentiment": n.sentiment.value if n.sentiment else None,
                "published_at": n.published_at.isoformat() if n.published_at else None,
                "image_url": n.image_url
            }
            for n in recent_list
        ]

    return DashboardResponse(
        stats=stats,
        trends=trends,
        sources=sources,
        recent_news=recent_news
    )
