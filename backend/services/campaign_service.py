import json
import os
import unicodedata
from datetime import datetime
from pathlib import Path

from services.claude_service import get_client

# Ruta base para los archivos de clientes — configurable via env
CLIENTES_BASE = Path(
    os.environ.get("CLIENTES_BASE_PATH", str(Path(__file__).parent.parent.parent / "clientes"))
)

_EXTRACCION_PROMPT = """Del siguiente historial de planificación de campaña de Instagram, extrae los datos en JSON con exactamente estos campos:
{
  "objetivo": "descripción del objetivo principal",
  "duracion_semanas": número entero estimado,
  "frecuencia": "X posts por semana",
  "tono": "descripción del tono de comunicación",
  "hashtags": ["hashtag1", "hashtag2"],
  "horarios_sugeridos": "descripción de horarios óptimos",
  "posts_propuestos": [
    {"semana": 1, "formato": "IMAGE|CAROUSEL|REEL", "tema": "tema del post"}
  ]
}

Responde SOLO con el JSON válido, sin texto adicional ni bloques de código."""


def _extraer_datos_plan(historial: list[dict]) -> dict:
    client = get_client()
    conversation_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in historial
    )
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"{_EXTRACCION_PROMPT}\n\nHISTORIAL:\n{conversation_text}"}],
    )
    try:
        return json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError):
        return {
            "objetivo": "Ver historial de campaña",
            "duracion_semanas": 4,
            "frecuencia": "3 posts por semana",
            "tono": "profesional",
            "hashtags": [],
            "horarios_sugeridos": "—",
            "posts_propuestos": [],
        }


def crear_estructura_carpeta(instagram_username: str, campaign_name: str) -> Path:
    mes = datetime.now().strftime("%Y-%m")
    normalizado = unicodedata.normalize("NFKD", campaign_name).encode("ascii", "ignore").decode("ascii")
    slug = "".join(c if c.isalnum() or c == "-" else "-" for c in normalizado.lower().replace(" ", "-"))[:40].strip("-")
    carpeta = CLIENTES_BASE / f"@{instagram_username}" / f"{mes}_{slug}"
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "assets").mkdir(exist_ok=True)
    return carpeta


def _generar_contexto_md(campaign_name: str, datos: dict) -> str:
    hashtags_str = " ".join(f"#{h.lstrip('#')}" for h in datos.get("hashtags", []))
    posts = datos.get("posts_propuestos", [])
    filas = "\n".join(
        f"| Semana {p.get('semana', i + 1)} | {p.get('formato', 'IMAGE')} | {p.get('tema', '—')} |"
        for i, p in enumerate(posts)
    ) or "| — | — | — |"

    return f"""# Campaña: {campaign_name}

## Objetivo
{datos.get('objetivo', '—')}

## Duración estimada
{datos.get('duracion_semanas', 4)} semanas

## Frecuencia de publicación
{datos.get('frecuencia', '—')}

## Tono y mensajes clave
{datos.get('tono', '—')}

## Horarios sugeridos
{datos.get('horarios_sugeridos', '—')}

## Hashtags
{hashtags_str or '_(pendiente)_'}

## Posts programados
| Semana | Formato | Tema |
|--------|---------|------|
{filas}

## Resultados al cierre
_(completar al finalizar la campaña)_
"""


def _generar_aprobacion_md(instagram_username: str, campaign_name: str, datos: dict) -> str:
    posts = datos.get("posts_propuestos", [])
    filas = "\n".join(
        f"| Semana {p.get('semana', i + 1)} | — | {p.get('formato', 'IMAGE')} | _(pendiente)_ | — | — |"
        for i, p in enumerate(posts)
    ) or "| — | — | — | — | — | — |"

    return f"""# Plan de campaña: @{instagram_username}

## Objetivo de la campaña
{datos.get('objetivo', '—')}

## Frecuencia y duración
{datos.get('frecuencia', '—')} durante {datos.get('duracion_semanas', 4)} semanas

## Tono de comunicación
{datos.get('tono', '—')}

## Calendario de publicaciones
| Semana | Fecha | Formato | Copy | Hashtags | Vista previa |
|--------|-------|---------|------|----------|--------------|
{filas}

## Siguiente paso
Revisar este plan y responder con tu aprobación o los ajustes que necesites.

---
_Generado automáticamente por Diavolo Instagram Manager_
"""


def guardar_documentos(
    instagram_username: str,
    campaign_name: str,
    historial: list[dict],
    usar_claude: bool = True,
) -> tuple[str, str, dict]:
    """Genera y guarda contexto.md y aprobacion-cliente.md. Devuelve (ruta_ctx, ruta_aprob, datos)."""
    datos = _extraer_datos_plan(historial) if (usar_claude and historial) else {
        "objetivo": campaign_name, "duracion_semanas": 4,
        "frecuencia": "3 posts por semana", "tono": "profesional",
        "hashtags": [], "horarios_sugeridos": "—", "posts_propuestos": [],
    }

    carpeta = crear_estructura_carpeta(instagram_username, campaign_name)
    contexto_path = carpeta / "contexto.md"
    aprobacion_path = carpeta / "aprobacion-cliente.md"

    contexto_path.write_text(_generar_contexto_md(campaign_name, datos), encoding="utf-8")
    aprobacion_path.write_text(_generar_aprobacion_md(instagram_username, campaign_name, datos), encoding="utf-8")

    return str(contexto_path), str(aprobacion_path), datos
