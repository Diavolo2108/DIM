import os

import httpx

RESEND_API = "https://api.resend.com/emails"


def enviar_reporte(to: str, subject: str, html: str) -> str:
    """Envía un email vía Resend. Devuelve el ID del mensaje."""
    api_key = os.environ.get("RESEND_API_KEY", "")
    if not api_key:
        raise RuntimeError("RESEND_API_KEY no configurada")

    from_email = os.environ.get("RESEND_FROM", "reportes@diavolo.agency")

    resp = httpx.post(
        RESEND_API,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"from": from_email, "to": [to], "subject": subject, "html": html},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("id", "")
