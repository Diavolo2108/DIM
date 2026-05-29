import httpx

META_API_BASE = "https://graph.facebook.com/v20.0"


def _build_caption_with_hashtags(caption: str | None, hashtags: list | None) -> str:
    text = caption or ""
    if hashtags:
        tags = " ".join(f"#{h.lstrip('#')}" for h in hashtags)
        text = f"{text}\n\n{tags}" if text else tags
    return text.strip()


def create_image_container(account_id: str, token: str, image_url: str, caption: str) -> str:
    """Crea un contenedor de imagen en Meta. Devuelve el creation_id."""
    resp = httpx.post(
        f"{META_API_BASE}/{account_id}/media",
        params={"access_token": token},
        json={"image_url": image_url, "caption": caption},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def create_carousel_item(account_id: str, token: str, image_url: str) -> str:
    """Crea un ítem de carrusel. Devuelve el creation_id del ítem."""
    resp = httpx.post(
        f"{META_API_BASE}/{account_id}/media",
        params={"access_token": token},
        json={"image_url": image_url, "is_carousel_item": True},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def create_carousel_container(account_id: str, token: str, child_ids: list[str], caption: str) -> str:
    """Crea un contenedor de carrusel con los IDs de los ítems."""
    resp = httpx.post(
        f"{META_API_BASE}/{account_id}/media",
        params={"access_token": token},
        json={
            "media_type": "CAROUSEL",
            "children": ",".join(child_ids),
            "caption": caption,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def create_reel_container(account_id: str, token: str, video_url: str, caption: str) -> str:
    """Crea un contenedor de Reel."""
    resp = httpx.post(
        f"{META_API_BASE}/{account_id}/media",
        params={"access_token": token},
        json={"media_type": "REELS", "video_url": video_url, "caption": caption},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def get_account_profile(account_id: str, token: str) -> dict:
    """Obtiene followers_count y media_count del perfil."""
    resp = httpx.get(
        f"{META_API_BASE}/{account_id}",
        params={"access_token": token, "fields": "followers_count,media_count"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def get_account_insights(account_id: str, token: str, since: str, until: str) -> dict:
    """Obtiene insights diarios: impressions, reach, profile_views, website_clicks."""
    resp = httpx.get(
        f"{META_API_BASE}/{account_id}/insights",
        params={
            "access_token": token,
            "metric": "impressions,reach,profile_views,website_clicks",
            "period": "day",
            "since": since,
            "until": until,
        },
        timeout=30,
    )
    resp.raise_for_status()
    result: dict[str, int] = {}
    for item in resp.json().get("data", []):
        values = item.get("values", [])
        total = sum(v.get("value", 0) for v in values)
        result[item["name"]] = total
    return result


def refresh_long_lived_token(current_token: str, app_id: str, app_secret: str) -> tuple[str, int]:
    """Renueva un long-lived token de Meta. Devuelve (nuevo_token, expires_in_segundos)."""
    resp = httpx.get(
        f"{META_API_BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": current_token,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["access_token"], data.get("expires_in", 5184000)


def get_instagram_conversations(account_id: str, token: str) -> list[dict]:
    """Obtiene hilos de DMs del inbox de Instagram Business."""
    resp = httpx.get(
        f"{META_API_BASE}/{account_id}/conversations",
        params={
            "access_token": token,
            "platform": "instagram",
            "fields": "id,messages{id,message,from,created_time}",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def send_dm_reply(account_id: str, token: str, recipient_id: str, message: str) -> str:
    """Responde a un DM de Instagram dentro de la ventana de 24h."""
    resp = httpx.post(
        f"{META_API_BASE}/{account_id}/messages",
        params={"access_token": token},
        json={
            "recipient": {"id": recipient_id},
            "message": {"text": message},
            "messaging_type": "RESPONSE",
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("message_id", "")


def get_media_comments(media_id: str, token: str) -> list[dict]:
    """Obtiene comentarios de un post de Instagram."""
    resp = httpx.get(
        f"{META_API_BASE}/{media_id}/comments",
        params={"access_token": token, "fields": "id,text,from,timestamp"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("data", [])


def reply_to_comment(comment_id: str, token: str, message: str) -> str:
    """Responde a un comentario de Instagram."""
    resp = httpx.post(
        f"{META_API_BASE}/{comment_id}/replies",
        params={"access_token": token},
        json={"message": message},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("id", "")


def publish_container(account_id: str, token: str, container_id: str) -> str:
    """Publica el contenedor. Devuelve el media_id del post publicado."""
    resp = httpx.post(
        f"{META_API_BASE}/{account_id}/media_publish",
        params={"access_token": token},
        json={"creation_id": container_id},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["id"]
