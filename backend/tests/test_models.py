import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from models.base import Base
from models.client import Client, ClientStatus
from models.campaign import Campaign, CampaignStatus
from models.post import Post, PostFormat, PostStatus
from models.asset import Asset
from models.message import Message, MessageType
from models.auto_reply import AutoReply
from models.metric import Metric
from models.scheduled_job import ScheduledJob, JobStatus

TABLES_ESPERADAS = {
    "clients", "campaigns", "posts", "assets",
    "messages", "auto_replies", "metrics", "scheduled_jobs",
}


@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s


def test_todas_las_tablas_existen(engine):
    tablas = set(inspect(engine).get_table_names())
    assert TABLES_ESPERADAS.issubset(tablas)


def test_client_insert_y_recuperar(session):
    client = Client(
        name="Diavolo Lab",
        instagram_username="diavolo_lab",
        instagram_account_id="17841437345819102",
        access_token_encrypted="token_encriptado",
        status=ClientStatus.EN_PAUSA,
    )
    session.add(client)
    session.commit()
    recuperado = session.get(Client, client.id)
    assert recuperado.instagram_username == "diavolo_lab"
    assert recuperado.status == ClientStatus.EN_PAUSA


def test_campaign_vinculada_a_client(session):
    client = Client(
        name="Cliente Test",
        instagram_username="cliente_test",
        instagram_account_id="123",
        access_token_encrypted="tok",
        status=ClientStatus.EN_PAUSA,
    )
    session.add(client)
    session.flush()

    campaign = Campaign(
        client_id=client.id,
        name="Aumentar seguidores",
        objetivo="Crecer 500 seguidores en 30 dias",
        status=CampaignStatus.PLANIFICACION,
    )
    session.add(campaign)
    session.commit()

    assert campaign.client_id == client.id


def test_post_vinculado_a_client_y_campaign(session):
    from datetime import datetime, timezone
    client = Client(
        name="C2",
        instagram_username="c2",
        instagram_account_id="999",
        access_token_encrypted="x",
        status=ClientStatus.EN_PAUSA,
    )
    session.add(client)
    session.flush()

    campaign = Campaign(
        client_id=client.id,
        name="Camp",
        objetivo="Obj",
        status=CampaignStatus.ACTIVA,
    )
    session.add(campaign)
    session.flush()

    post = Post(
        client_id=client.id,
        campaign_id=campaign.id,
        scheduled_at=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        format=PostFormat.IMAGE,
        status=PostStatus.PROGRAMADO,
    )
    session.add(post)
    session.commit()

    assert post.campaign_id == campaign.id


def test_asset_vinculado_a_post(session):
    from datetime import datetime, timezone
    client = Client(
        name="C3",
        instagram_username="c3",
        instagram_account_id="888",
        access_token_encrypted="y",
        status=ClientStatus.EN_PAUSA,
    )
    session.add(client)
    session.flush()

    asset = Asset(
        client_id=client.id,
        r2_key="clientes/c3/post-01.jpg",
        r2_url="https://r2.example.com/post-01.jpg",
        filename="post-01.jpg",
        content_type="image/jpeg",
        size_bytes=204800,
    )
    session.add(asset)
    session.commit()

    assert asset.r2_key == "clientes/c3/post-01.jpg"


def test_message_insert(session):
    from datetime import datetime, timezone
    client = Client(
        name="C4",
        instagram_username="c4",
        instagram_account_id="777",
        access_token_encrypted="z",
        status=ClientStatus.EN_PAUSA,
    )
    session.add(client)
    session.flush()

    msg = Message(
        client_id=client.id,
        instagram_thread_id="thread_001",
        instagram_message_id="msg_001",
        sender_id="user_999",
        content="Hola, me interesa el producto",
        type=MessageType.DM,
        is_from_page=False,
        replied=False,
    )
    session.add(msg)
    session.commit()

    assert msg.type == MessageType.DM
    assert msg.replied is False


def test_scheduled_job_estados(session):
    job = ScheduledJob(
        job_type="publish_post",
        reference_id="00000000-0000-0000-0000-000000000001",
        status=JobStatus.PENDIENTE,
        retry_count=0,
    )
    session.add(job)
    session.commit()

    assert job.status == JobStatus.PENDIENTE
