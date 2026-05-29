from datetime import date, datetime
from pydantic import BaseModel


class MetricOut(BaseModel):
    id: str
    client_id: str
    date: date
    followers_count: int
    reach: int
    impressions: int
    engagement_rate: float
    profile_views: int
    website_clicks: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MetricSummary(BaseModel):
    followers_count: int
    reach_total: int
    impressions_total: int
    engagement_promedio: float
    profile_views_total: int
    website_clicks_total: int
    dias: int
