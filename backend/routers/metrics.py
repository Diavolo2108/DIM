from datetime import date, datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import get_db
from models.client import Client
from models.metric import Metric
from models.user import User
from routers.auth import _get_current_user
from schemas.metric import MetricOut, MetricSummary
from services.encryption_service import decrypt
from services.meta_service import get_account_insights, get_account_profile

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricSummary)
def resumen_metricas(
    client_id: str,
    days: int = 7,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    since = date.today() - timedelta(days=days)
    rows = db.query(Metric).filter(
        Metric.client_id == client_id,
        Metric.date >= since,
    ).all()

    if not rows:
        latest = db.query(Metric).filter_by(client_id=client_id).order_by(Metric.date.desc()).first()
        followers = latest.followers_count if latest else 0
        return MetricSummary(
            followers_count=followers,
            reach_total=0, impressions_total=0,
            engagement_promedio=0.0, profile_views_total=0,
            website_clicks_total=0, dias=0,
        )

    return MetricSummary(
        followers_count=rows[-1].followers_count,
        reach_total=sum(r.reach for r in rows),
        impressions_total=sum(r.impressions for r in rows),
        engagement_promedio=round(sum(r.engagement_rate for r in rows) / len(rows), 2),
        profile_views_total=sum(r.profile_views for r in rows),
        website_clicks_total=sum(r.website_clicks for r in rows),
        dias=len(rows),
    )


@router.get("/", response_model=list[MetricOut])
def listar_metricas(
    client_id: str | None = None,
    since: date | None = None,
    until: date | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    q = db.query(Metric)
    if client_id:
        q = q.filter(Metric.client_id == client_id)
    if since:
        q = q.filter(Metric.date >= since)
    if until:
        q = q.filter(Metric.date <= until)
    return q.order_by(Metric.date.desc()).all()


@router.post("/sync", response_model=MetricOut)
def sync_metricas(
    client_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(_get_current_user),
):
    client = db.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    token = decrypt(client.access_token_encrypted)
    account_id = client.instagram_account_id
    today = date.today()

    try:
        profile = get_account_profile(account_id, token)
        since_ts = str(int(datetime(today.year, today.month, today.day, tzinfo=timezone.utc).timestamp()))
        until_ts = str(int((datetime(today.year, today.month, today.day, tzinfo=timezone.utc) + timedelta(days=1)).timestamp()))
        insights = get_account_insights(account_id, token, since_ts, until_ts)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

    existing = db.query(Metric).filter_by(client_id=client_id, date=today).first()
    if existing:
        m = existing
    else:
        m = Metric(client_id=client_id, date=today)
        db.add(m)

    m.followers_count = profile.get("followers_count", 0)
    m.impressions = insights.get("impressions", 0)
    m.reach = insights.get("reach", 0)
    m.profile_views = insights.get("profile_views", 0)
    m.website_clicks = insights.get("website_clicks", 0)
    m.engagement_rate = round(
        (m.impressions / m.followers_count * 100) if m.followers_count else 0.0, 2
    )

    db.commit()
    db.refresh(m)
    return m
