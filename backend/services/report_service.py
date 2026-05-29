from datetime import date, timedelta

from sqlalchemy.orm import Session

from models.client import Client, ClientStatus
from models.metric import Metric
from models.post import Post, PostStatus


def _kpi_row(label: str, value: str) -> str:
    return f"""
    <tr>
      <td style="padding:8px 12px;color:#6b7280;font-size:13px;">{label}</td>
      <td style="padding:8px 12px;font-weight:600;color:#111827;font-size:13px;">{value}</td>
    </tr>"""


def _fmt(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def generar_reporte_html(session: Session, semanas_atras: int = 1) -> str:
    """Genera HTML del reporte semanal de métricas para todos los clientes activos."""
    since = date.today() - timedelta(weeks=semanas_atras)
    clientes = session.query(Client).filter(Client.status != ClientStatus.INACTIVA).all()

    secciones = []
    for cliente in clientes:
        metrics = session.query(Metric).filter(
            Metric.client_id == cliente.id,
            Metric.date >= since,
        ).order_by(Metric.date.desc()).all()

        posts_pub = session.query(Post).filter(
            Post.client_id == cliente.id,
            Post.status == PostStatus.PUBLICADO,
            Post.scheduled_at >= since,
        ).count()

        if not metrics:
            continue

        latest = metrics[0]
        reach_total = sum(m.reach for m in metrics)
        impr_total = sum(m.impressions for m in metrics)
        eng_prom = round(sum(m.engagement_rate for m in metrics) / len(metrics), 2)

        filas = (
            _kpi_row("Seguidores", _fmt(latest.followers_count))
            + _kpi_row("Alcance (semana)", _fmt(reach_total))
            + _kpi_row("Impresiones (semana)", _fmt(impr_total))
            + _kpi_row("Engagement promedio", f"{eng_prom}%")
            + _kpi_row("Visitas de perfil", _fmt(sum(m.profile_views for m in metrics)))
            + _kpi_row("Posts publicados", str(posts_pub))
        )

        secciones.append(f"""
        <div style="margin-bottom:32px;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
          <div style="background:#111827;padding:14px 20px;">
            <h2 style="margin:0;color:#fff;font-size:16px;">@{cliente.instagram_username}</h2>
            <p style="margin:4px 0 0;color:#9ca3af;font-size:12px;">{cliente.name}</p>
          </div>
          <table style="width:100%;border-collapse:collapse;background:#fff;">
            {filas}
          </table>
        </div>""")

    if not secciones:
        secciones.append(
            "<p style='color:#6b7280;'>No hay métricas disponibles para este período.</p>"
        )

    periodo = f"{since.strftime('%d/%m/%Y')} — {date.today().strftime('%d/%m/%Y')}"
    cuerpo = "\n".join(secciones)

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f9fafb;margin:0;padding:32px;">
  <div style="max-width:600px;margin:0 auto;">
    <div style="background:#111827;border-radius:12px 12px 0 0;padding:24px;">
      <h1 style="margin:0;color:#fff;font-size:22px;">Diavolo Instagram Manager</h1>
      <p style="margin:6px 0 0;color:#9ca3af;font-size:13px;">Reporte semanal · {periodo}</p>
    </div>
    <div style="background:#f9fafb;padding:24px;">
      {cuerpo}
    </div>
    <div style="text-align:center;padding:20px;color:#9ca3af;font-size:11px;">
      Diavolo Agency · Reporte generado automáticamente
    </div>
  </div>
</body>
</html>"""
