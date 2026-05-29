import os
import anthropic

PLANNING_SYSTEM_PROMPT = """Eres el asistente de planificación de campañas de Instagram de Diavolo, una agencia de marketing.

Tu rol es ayudar al equipo a planificar campañas completas de Instagram para sus clientes.

Cuando el equipo describa un cliente y sus objetivos, tú debes proponer:
1. Objetivo concreto y medible de la campaña
2. Duración recomendada (en semanas)
3. Frecuencia de publicación (posts por semana)
4. Formatos sugeridos (imágenes, carruseles, Reels)
5. Tono de comunicación
6. Horarios óptimos de publicación
7. Hashtags relevantes (máx. 20)
8. Calendario de posts con fechas, formato y tema de cada post

Sé específico, práctico y orientado a resultados. Habla siempre en español.
Cuando tengas toda la información necesaria para el plan, presenta el calendario completo en formato de tabla."""


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY no definida en variables de entorno")
    return anthropic.Anthropic(api_key=api_key)


def build_planning_messages(
    historial: list[dict],
    contexto_cliente: str | None = None,
) -> list[dict]:
    messages = list(historial)

    if contexto_cliente:
        if messages and messages[0]["role"] == "user":
            # Inyectar en el primer mensaje de usuario existente
            messages[0] = {
                "role": "user",
                "content": f"[Contexto del cliente: {contexto_cliente}]\n\n{messages[0]['content']}",
            }
        elif not messages:
            # Historial vacío: crear mensaje de contexto inicial
            messages = [{"role": "user", "content": f"[Contexto del cliente: {contexto_cliente}]"}]

    return messages


def planificar_campana(
    historial: list[dict],
    contexto_cliente: str | None = None,
) -> str:
    client = get_client()
    messages = build_planning_messages(historial, contexto_cliente)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=PLANNING_SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


COPY_SYSTEM_PROMPT = """Eres un experto en copywriting para Instagram de la agencia Diavolo.

Tu tarea es generar copies (captions) para publicaciones de Instagram basados en el contexto de la campaña.

Reglas:
- El copy debe ser auténtico, en primera persona del plural o del cliente según el tono
- Incluir emojis relevantes de forma natural (no en exceso)
- Al final del copy incluir los hashtags separados por espacio
- Longitud: 100-300 caracteres para el copy principal, sin contar hashtags
- Idioma: español, salvo que el contexto indique otro

Formato de respuesta OBLIGATORIO (sin texto adicional):
COPY: [el caption aquí]
HASHTAGS: [hashtag1] [hashtag2] [hashtag3]"""


def build_copy_prompt(
    campaign_context: str | None,
    instruccion: str,
    formato: str,
) -> str:
    ctx = f"Contexto de la campaña:\n{campaign_context}\n\n" if campaign_context else ""
    return f"{ctx}Formato del post: {formato}\n\nInstrucción: {instruccion}"


def generar_copy(
    instruccion: str,
    formato: str,
    campaign_context: str | None = None,
) -> tuple[str, list[str]]:
    """Genera copy e hashtags para un post. Devuelve (copy, hashtags)."""
    client = get_client()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=COPY_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_copy_prompt(campaign_context, instruccion, formato)}],
    )
    raw = response.content[0].text
    copy, hashtags = _parse_copy_response(raw)
    return copy, hashtags


def _parse_copy_response(raw: str) -> tuple[str, list[str]]:
    copy = ""
    hashtags: list[str] = []
    for line in raw.splitlines():
        if line.startswith("COPY:"):
            copy = line.removeprefix("COPY:").strip()
        elif line.startswith("HASHTAGS:"):
            raw_tags = line.removeprefix("HASHTAGS:").strip()
            hashtags = [t.lstrip("#").strip() for t in raw_tags.split() if t.startswith("#")]
    # Fallback si Claude no sigue el formato exacto
    if not copy:
        copy = raw.strip()
    return copy, hashtags
