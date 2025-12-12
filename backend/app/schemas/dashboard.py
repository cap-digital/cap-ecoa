from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime


class StatsResponse(BaseModel):
    total_news: int
    news_today: int
    positive_mentions: int
    negative_mentions: int
    neutral_mentions: int
    active_terms: int


class TrendPoint(BaseModel):
    date: str
    count: int
    sentiment_avg: float


class TrendResponse(BaseModel):
    term: str
    data: List[TrendPoint]


class SourceStats(BaseModel):
    source: str
    count: int
    percentage: float


class DashboardResponse(BaseModel):
    stats: StatsResponse
    trends: List[TrendResponse]
    sources: List[SourceStats]
    recent_news: List[dict]
