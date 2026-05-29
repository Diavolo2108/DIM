# PROJECT.md — Diavolo Instagram Manager

> Fuente de verdad del proyecto. Generado el 2026-05-28 desde Diavolo-Instagram-Manager.md.

---

## 1. El producto

**Nombre:** Diavolo Instagram Manager

**Descripción:** Software de gestión de Instagram para la agencia Diavolo. Permite administrar múltiples cuentas de clientes desde un solo panel: planificación de campañas con IA, generación de contenido, publicación automática, gestión de DMs/comentarios y métricas.

**Problema que resuelve:** Sin este software, el equipo de Diavolo gestiona cada cuenta de Instagram de cliente de forma manual y desconectada — sin automatización de publicaciones, sin inbox centralizado, sin métricas unificadas ni generación de contenido asistida por IA.

**Usuario objetivo:** Equipo interno de Diavolo (agencia). Los clientes no tienen acceso al dashboard; reciben documentos de aprobación de campaña por fuera.

**Escala esperada:** Uso interno, 1 organización, volumen bajo-medio.

---

## 2. Modelo de negocio

**Tipo:** Uso interno — no monetiza directamente.

**Modelo de clientes:** Una sola organización (equipo Diavolo), que a su vez gestiona múltiples cuentas de Instagram de sus clientes.

> No es SaaS multi-tenant. No hay aislamiento entre cuentas de diferentes "tenants" — todo el equipo Diavolo accede a todos los clientes de Instagram.

---

## 3. Stack tecnológico

| Capa | Tecnología | Justificación |
|---|---|---|
| Frontend | Next.js 14 (App Router) | SSR, deploy en Vercel, soporte óptimo en Claude Code |
| UI | Tailwind CSS + shadcn/ui | Componentes listos, diseño limpio y rápido |
| Estado global | Zustand + React Query | Ligero, eficiente, manejo de caché de servidor |
| Backend | FastAPI (Python) | Ligero, ideal para APIs REST y tareas asíncronas |
| ORM | SQLAlchemy + Alembic | Migraciones controladas, robusto |
| Scheduler | APScheduler (Python) | Publicaciones automáticas, integrado en FastAPI |
| Auth | NextAuth.js + JWT | Sesiones seguras, compatible con Next.js |
| Base de datos | PostgreSQL vía Supabase | Plan gratuito, auth incluida |
| Caché | Redis vía Upstash | Plan gratuito, ideal para cola de jobs |
| Assets | Cloudflare R2 | Gratuito hasta 10 GB, S3-compatible |
| Hosting frontend | Vercel | Plan gratuito, integración nativa con Next.js |
| Hosting backend | Railway o Render | Plan gratuito con límites aceptables para MVP |
| IA | Claude API (claude-sonnet-4-6) | Planificación de campañas, copies, autorrespuestas |
| Correo | Resend | Gratuito hasta 3.000 emails/mes |

### Costos estimados mensuales

| Servicio | Costo |
|---|---|
| Meta Graph API | Gratuito |
| Claude API | ~$5–10 USD |
| Supabase | Gratuito |
| Cloudflare R2 | Gratuito (< 10 GB) |
| Vercel | Gratuito |
| Railway/Render | Gratuito (con límites) |
| Resend | Gratuito |
| **Total estimado** | **< $10 USD/mes** |

---

## 4. Principios no negociables

1. **Credenciales nunca hardcodeadas** — siempre variables de entorno.
2. **Tokens de clientes de Instagram siempre encriptados** — usar `encryption_service.py`, nunca texto plano en BD.
3. **Toda lógica es por cliente** — nunca mezclar datos entre cuentas de Instagram distintas.
4. **Tests obligatorios** — Pytest para backend, Playwright para E2E.
5. **Assets siempre en R2** — nunca almacenar archivos en el servidor local.
6. **Pedir confirmación antes de modificar modelos de BD existentes**.

---

## 5. Módulos del sistema

### Módulo 1 — Panel de administración
Lista de clientes con estado (EN CAMPAÑA / EN PAUSA / INACTIVA). CRUD de cuentas. Credenciales encriptadas por cliente.

### Módulo 2 — Planificación de campañas
Chatbot con Claude API. Genera `contexto.md` y `aprobacion-cliente.md`. Historial de campañas.

### Módulo 3 — Generación de contenido
Claude genera copies, captions y hashtags. Upload de assets (drag & drop → Cloudflare R2). Vista de calendario por cliente.

### Módulo 4 — Calendario
Vista mensual por cliente. Estado de cada post: programado / publicado / fallido. Edición rápida de horarios.

### Módulo 5 — Publicación automática
Scheduler sin intervención manual. Assets desde R2. Cola con reintentos. Soporte: imágenes, carruseles, Reels.

### Módulo 6 — Inbox unificado
DMs y comentarios de todos los clientes en una sola bandeja. Filtro por cuenta. Respuestas sugeridas por Claude. Autorrespuestas configurables.

### Módulo 7 — Dashboard de métricas
KPIs por cliente: alcance, impresiones, engagement, seguidores. Resultados por campaña. Reportes semanales por correo (Resend).

---

## 6. Servicios y dependencias externas

| Servicio | Uso | Restricciones importantes |
|---|---|---|
| Meta Graph API | Publicar, leer DMs, métricas | Rate limit 200 llamadas/hora por cuenta; tokens caducan cada 60 días; no se puede iniciar conversación en DMs; ventana de 24h para responder; Stories no publicables vía API |
| Claude API | Planificación, copies, autorrespuestas | Costo por tokens |
| Supabase | PostgreSQL | Free tier: 500 MB BD, 1 GB storage |
| Cloudflare R2 | Assets | Gratuito hasta 10 GB |
| Upstash | Redis | Free tier: 10.000 comandos/día |
| Resend | Correo | Gratuito hasta 3.000/mes |

### Meta App configurada

| Elemento | Valor |
|---|---|
| Business Manager ID | 1027543546404665 |
| Cuenta Instagram inicial | @diavolo_lab (ID: 17841437345819102) |
| App ID | 974196185219039 |
| Modo actual | Desarrollo |

### Permisos Meta configurados
- `instagram_business_basic`
- `instagram_manage_comments`
- `instagram_business_manage_messages`
- `instagram_content_publish`
- Estadísticas

---

## 7. Variables de entorno

```env
# Meta / Instagram (globales)
META_APP_ID=974196185219039
META_APP_SECRET=<ver panel Meta developers>
META_WEBHOOK_VERIFY_TOKEN=<token personalizado>

# Claude API
ANTHROPIC_API_KEY=<console.anthropic.com>

# Base de datos
DATABASE_URL=<postgresql://... Supabase>
REDIS_URL=<redis://... Upstash>

# Almacenamiento
CLOUDFLARE_R2_BUCKET=<nombre bucket>
CLOUDFLARE_R2_ACCESS_KEY=<key>
CLOUDFLARE_R2_SECRET_KEY=<secret>
CLOUDFLARE_R2_ENDPOINT=<endpoint R2>

# Correo
RESEND_API_KEY=<resend.com>

# Seguridad
ENCRYPTION_KEY=<clave AES para encriptar tokens de clientes>

# Telegram (SDD — notificaciones de desarrollo)
TELEGRAM_BOT_TOKEN=<BotFather>
TELEGRAM_CHAT_ID=<ID del chat>
```

---

## 8. Convenciones de código

- **Idioma de la UI:** Español
- **Código:** Inglés (variables, funciones, archivos)
- **Comentarios:** Español
- **Tests backend:** Pytest
- **Tests E2E:** Playwright
- **Formato de commits:** `[sprint-id] descripción breve en español`
- **Estructura de carpetas:** según sección de arquitectura de Diavolo-Instagram-Manager.md

---

## 9. Estructura del proyecto

```
diavolo-instagram-manager/
├── PROJECT.md
├── .env.local                     ← nunca subir a git
├── .gitignore
├── sdd/
│   ├── SDD_STATE.json
│   └── SDD_LOG.json
├── lib/
│   └── notify.js                  ← bot Telegram SDD
├── frontend/                      ← Next.js 14
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── clientes/
│   │   │   ├── campanas/
│   │   │   ├── contenido/
│   │   │   ├── calendario/
│   │   │   ├── inbox/
│   │   │   └── metricas/
│   └── components/
├── backend/                       ← FastAPI
│   ├── main.py
│   ├── routers/
│   │   ├── clients.py
│   │   ├── campaigns.py
│   │   ├── posts.py
│   │   ├── assets.py
│   │   ├── messages.py
│   │   └── metrics.py
│   ├── models/
│   └── services/
│       ├── claude_service.py
│       ├── meta_service.py
│       ├── r2_service.py
│       ├── encryption_service.py
│       └── scheduler.py
└── clientes/                      ← carpetas por cliente
    └── @diavolo_lab/
```

---

## 10. Decisiones pendientes

| # | Decisión | Estado |
|---|---|---|
| 1 | Railway vs Render para backend | Pendiente — decidir al llegar a deploy |
| 2 | APScheduler vs BullMQ+Redis para scheduler | APScheduler preferido (Python nativo), BullMQ si se necesita más robustez |
| 3 | Webhooks Meta — URL pública del servidor | Pendiente hasta que haya backend desplegado |

---

## 11. Log de cambios al plan

| Fecha | Sprint | Cambio | Motivo | Autorizado por |
|-------|--------|--------|--------|----------------|
| 2026-05-28 | — | Creación inicial de PROJECT.md desde Diavolo-Instagram-Manager.md | Arranque del sistema SDD | Director |
