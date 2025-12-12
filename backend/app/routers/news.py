from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, timedelta
from ..database import get_supabase
from ..schemas.news import (
    NewsResponse,
    NewsListResponse,
    NewsSource,
    SentimentType
)
from .auth import get_current_user

router = APIRouter(prefix="/news", tags=["News"])


@router.get("", response_model=NewsListResponse)
async def list_news(
    term: Optional[str] = Query(None, description="Filtrar por termo"),
    source: Optional[NewsSource] = Query(None, description="Filtrar por fonte"),
    sentiment: Optional[SentimentType] = Query(None, description="Filtrar por sentimento"),
    start_date: Optional[datetime] = Query(None, description="Data inicial"),
    end_date: Optional[datetime] = Query(None, description="Data final"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user=Depends(get_current_user)
):
    supabase = get_supabase()

    # Get user's monitored terms
    user_terms = supabase.table("ecoa_monitored_terms").select("term").eq(
        "user_id", current_user.id
    ).eq("is_active", True).execute()

    terms = [t["term"] for t in user_terms.data] if user_terms.data else []

    if not terms:
        return NewsListResponse(
            items=[],
            total=0,
            page=page,
            per_page=per_page,
            total_pages=0
        )

    # Build query
    query = supabase.table("ecoa_news").select("*", count="exact")

    # Filter by source
    if source:
        query = query.eq("source", source.value)

    # Filter by sentiment
    if sentiment:
        query = query.eq("sentiment", sentiment.value)

    # Filter by date range
    if start_date:
        query = query.gte("published_at", start_date.isoformat())
    if end_date:
        query = query.lte("published_at", end_date.isoformat())

    # Filter by term in title or content
    if term:
        query = query.or_(f"title.ilike.%{term}%,content.ilike.%{term}%")
    else:
        # Filter by any of user's monitored terms
        term_filters = ",".join([
            f"title.ilike.%{t}%,content.ilike.%{t}%" for t in terms
        ])
        query = query.or_(term_filters)

    # Pagination
    offset = (page - 1) * per_page
    query = query.order("published_at", desc=True).range(offset, offset + per_page - 1)

    result = query.execute()

    total = result.count or 0
    total_pages = (total + per_page - 1) // per_page

    items = []
    for news in result.data or []:
        # Find which terms match this news
        matched_terms = []
        title_lower = (news.get("title") or "").lower()
        content_lower = (news.get("content") or "").lower()

        for t in terms:
            if t.lower() in title_lower or t.lower() in content_lower:
                matched_terms.append(t)

        items.append(NewsResponse(
            id=news["id"],
            title=news["title"],
            summary=news.get("summary"),
            content=news.get("content"),
            url=news["url"],
            image_url=news.get("image_url"),
            author=news.get("author"),
            source=news["source"],
            published_at=news.get("published_at"),
            sentiment=news.get("sentiment"),
            sentiment_score=news.get("sentiment_score"),
            scraped_at=news["scraped_at"],
            matched_terms=matched_terms
        ))

    return NewsListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(news_id: str, current_user=Depends(get_current_user)):
    supabase = get_supabase()

    result = supabase.table("ecoa_news").select("*").eq("id", news_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Notícia não encontrada")

    news = result.data

    # Get user's terms to show matches
    user_terms = supabase.table("ecoa_monitored_terms").select("term").eq(
        "user_id", current_user.id
    ).execute()

    terms = [t["term"] for t in user_terms.data] if user_terms.data else []
    matched_terms = []

    title_lower = (news.get("title") or "").lower()
    content_lower = (news.get("content") or "").lower()

    for t in terms:
        if t.lower() in title_lower or t.lower() in content_lower:
            matched_terms.append(t)

    return NewsResponse(
        id=news["id"],
        title=news["title"],
        summary=news.get("summary"),
        content=news.get("content"),
        url=news["url"],
        image_url=news.get("image_url"),
        author=news.get("author"),
        source=news["source"],
        published_at=news.get("published_at"),
        sentiment=news.get("sentiment"),
        sentiment_score=news.get("sentiment_score"),
        scraped_at=news["scraped_at"],
        matched_terms=matched_terms
    )


@router.get("/sources/list")
async def list_sources(current_user=Depends(get_current_user)):
    return {
        "sources": [
            {"id": "g1", "name": "G1", "url": "https://g1.globo.com"},
            {"id": "cnn", "name": "CNN Brasil", "url": "https://www.cnnbrasil.com.br"},
            {"id": "twitter", "name": "Twitter/X", "url": "https://twitter.com"},
            {"id": "threads", "name": "Threads", "url": "https://threads.net"},
        ]
    }
