from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from ..database import get_db
from ..models import User, News, MonitoredTerm
from ..services.auth import get_current_user
from ..schemas.news import (
    NewsResponse,
    NewsListResponse,
    NewsSource,
    SentimentType
)

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get user's monitored terms
    user_terms = db.query(MonitoredTerm).filter(
        MonitoredTerm.user_id == current_user.id,
        MonitoredTerm.is_active == True
    ).all()

    terms = [t.term for t in user_terms]

    if not terms:
        return NewsListResponse(
            items=[],
            total=0,
            page=page,
            per_page=per_page,
            total_pages=0
        )

    # Build query
    query = db.query(News)

    # Filter by source
    if source:
        query = query.filter(News.source == source.value)

    # Filter by sentiment
    if sentiment:
        query = query.filter(News.sentiment == sentiment.value)

    # Filter by date range
    if start_date:
        query = query.filter(News.published_at >= start_date)
    if end_date:
        query = query.filter(News.published_at <= end_date)

    # Filter by term in title or content
    if term:
        query = query.filter(
            or_(
                News.title.ilike(f"%{term}%"),
                News.content.ilike(f"%{term}%")
            )
        )
    else:
        # Filter by any of user's monitored terms
        term_filters = []
        for t in terms:
            term_filters.append(News.title.ilike(f"%{t}%"))
            term_filters.append(News.content.ilike(f"%{t}%"))
        if term_filters:
            query = query.filter(or_(*term_filters))

    # Get total count
    total = query.count()

    # Pagination
    offset = (page - 1) * per_page
    news_list = query.order_by(News.published_at.desc()).offset(offset).limit(per_page).all()

    total_pages = (total + per_page - 1) // per_page

    items = []
    for news in news_list:
        # Find which terms match this news
        matched_terms = []
        title_lower = (news.title or "").lower()
        content_lower = (news.content or "").lower()

        for t in terms:
            if t.lower() in title_lower or t.lower() in content_lower:
                matched_terms.append(t)

        items.append(NewsResponse(
            id=news.id,
            title=news.title,
            summary=news.summary,
            content=news.content,
            url=news.url,
            image_url=news.image_url,
            author=news.author,
            source=news.source,
            published_at=news.published_at,
            sentiment=news.sentiment.value if news.sentiment else None,
            sentiment_score=news.sentiment_score,
            scraped_at=news.scraped_at,
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
async def get_news(
    news_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    news = db.query(News).filter(News.id == news_id).first()

    if not news:
        raise HTTPException(status_code=404, detail="Notícia não encontrada")

    # Get user's terms to show matches
    user_terms = db.query(MonitoredTerm).filter(
        MonitoredTerm.user_id == current_user.id
    ).all()

    terms = [t.term for t in user_terms]
    matched_terms = []

    title_lower = (news.title or "").lower()
    content_lower = (news.content or "").lower()

    for t in terms:
        if t.lower() in title_lower or t.lower() in content_lower:
            matched_terms.append(t)

    return NewsResponse(
        id=news.id,
        title=news.title,
        summary=news.summary,
        content=news.content,
        url=news.url,
        image_url=news.image_url,
        author=news.author,
        source=news.source,
        published_at=news.published_at,
        sentiment=news.sentiment.value if news.sentiment else None,
        sentiment_score=news.sentiment_score,
        scraped_at=news.scraped_at,
        matched_terms=matched_terms
    )


@router.get("/sources/list")
async def list_sources(current_user: User = Depends(get_current_user)):
    return {
        "sources": [
            {"id": "g1", "name": "G1", "url": "https://g1.globo.com"},
            {"id": "cnn", "name": "CNN Brasil", "url": "https://www.cnnbrasil.com.br"},
            {"id": "twitter", "name": "Twitter/X", "url": "https://twitter.com"},
            {"id": "threads", "name": "Threads", "url": "https://threads.net"},
        ]
    }
