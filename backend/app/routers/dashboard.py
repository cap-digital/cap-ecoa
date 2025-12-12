from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from collections import defaultdict
from ..database import get_supabase
from ..schemas.dashboard import (
    StatsResponse,
    TrendResponse,
    TrendPoint,
    SourceStats,
    DashboardResponse
)
from .auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=StatsResponse)
async def get_stats(current_user=Depends(get_current_user)):
    supabase = get_supabase()

    # Get user's active terms
    terms_result = supabase.table("ecoa_monitored_terms").select("term").eq(
        "user_id", current_user.id
    ).eq("is_active", True).execute()

    terms = [t["term"] for t in terms_result.data] if terms_result.data else []
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

    # Build filter for user's terms
    term_filters = ",".join([
        f"title.ilike.%{t}%,content.ilike.%{t}%" for t in terms
    ])

    # Total news matching user's terms
    total_result = supabase.table("ecoa_news").select(
        "id", count="exact"
    ).or_(term_filters).execute()

    total_news = total_result.count or 0

    # News today
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = supabase.table("ecoa_news").select(
        "id", count="exact"
    ).or_(term_filters).gte("published_at", today.isoformat()).execute()

    news_today = today_result.count or 0

    # Sentiment counts
    positive_result = supabase.table("ecoa_news").select(
        "id", count="exact"
    ).or_(term_filters).eq("sentiment", "positive").execute()

    negative_result = supabase.table("ecoa_news").select(
        "id", count="exact"
    ).or_(term_filters).eq("sentiment", "negative").execute()

    neutral_result = supabase.table("ecoa_news").select(
        "id", count="exact"
    ).or_(term_filters).eq("sentiment", "neutral").execute()

    return StatsResponse(
        total_news=total_news,
        news_today=news_today,
        positive_mentions=positive_result.count or 0,
        negative_mentions=negative_result.count or 0,
        neutral_mentions=neutral_result.count or 0,
        active_terms=active_terms
    )


@router.get("/trends", response_model=list[TrendResponse])
async def get_trends(days: int = 7, current_user=Depends(get_current_user)):
    supabase = get_supabase()

    # Get user's active terms
    terms_result = supabase.table("ecoa_monitored_terms").select("term").eq(
        "user_id", current_user.id
    ).eq("is_active", True).execute()

    terms = [t["term"] for t in terms_result.data] if terms_result.data else []

    if not terms:
        return []

    start_date = datetime.now() - timedelta(days=days)
    trends = []

    for term in terms[:5]:  # Limit to top 5 terms
        # Get news for this term in the date range
        result = supabase.table("ecoa_news").select(
            "published_at, sentiment_score"
        ).or_(
            f"title.ilike.%{term}%,content.ilike.%{term}%"
        ).gte("published_at", start_date.isoformat()).execute()

        # Group by date
        daily_data = defaultdict(lambda: {"count": 0, "sentiment_sum": 0})

        for news in result.data or []:
            if news.get("published_at"):
                date_str = news["published_at"][:10]  # YYYY-MM-DD
                daily_data[date_str]["count"] += 1
                daily_data[date_str]["sentiment_sum"] += news.get("sentiment_score") or 0

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
async def get_source_stats(current_user=Depends(get_current_user)):
    supabase = get_supabase()

    # Get user's active terms
    terms_result = supabase.table("ecoa_monitored_terms").select("term").eq(
        "user_id", current_user.id
    ).eq("is_active", True).execute()

    terms = [t["term"] for t in terms_result.data] if terms_result.data else []

    if not terms:
        return []

    term_filters = ",".join([
        f"title.ilike.%{t}%,content.ilike.%{t}%" for t in terms
    ])

    # Get all news sources distribution
    result = supabase.table("ecoa_news").select("source").or_(term_filters).execute()

    # Count by source
    source_counts = defaultdict(int)
    total = 0

    for news in result.data or []:
        source_counts[news["source"]] += 1
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
async def get_dashboard(current_user=Depends(get_current_user)):
    supabase = get_supabase()

    # Get all dashboard data
    stats = await get_stats(current_user)
    trends = await get_trends(7, current_user)
    sources = await get_source_stats(current_user)

    # Get recent news
    terms_result = supabase.table("ecoa_monitored_terms").select("term").eq(
        "user_id", current_user.id
    ).eq("is_active", True).execute()

    terms = [t["term"] for t in terms_result.data] if terms_result.data else []
    recent_news = []

    if terms:
        term_filters = ",".join([
            f"title.ilike.%{t}%,content.ilike.%{t}%" for t in terms
        ])

        recent_result = supabase.table("ecoa_news").select(
            "id, title, source, sentiment, published_at, image_url"
        ).or_(term_filters).order("published_at", desc=True).limit(5).execute()

        recent_news = recent_result.data or []

    return DashboardResponse(
        stats=stats,
        trends=trends,
        sources=sources,
        recent_news=recent_news
    )
