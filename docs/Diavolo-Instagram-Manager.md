# Diavolo Instagram Manager

Documento maestro del proyecto. Contiene el contexto completo del sistema, arquitectura, configuración de Meta, flujos y hoja de ruta. Usar como referencia en cada sesión de Claude Code.

---

## Qué es este proyecto

Software de gestión de Instagram para la agencia **Diavolo**. Permite administrar múltiples cuentas de clientes desde un solo panel: planificación de campañas con IA, generación de contenido, publicación automática, gestión de DMs/comentarios y métricas.

**Uso:** Interno de la agencia. El equipo de Diavolo administra todas las cuentas. Los clientes no tienen acceso al dashboard — reciben documentos de aprobación de campaña por fuera.

**Costo objetivo:** menos de $10 USD/mes.

---

## ✅ Setup de Meta — COMPLETADO

### Configuración realizada (Mayo 2026)

| Elemento | Detalle | Estado |
|---|---|---|
| Business Manager | Diavolo (ID: 1027543546404665) | ✅ Activo |
| Cuenta de Instagram | @diavolo_lab (ID: 17841437345819102) | ✅ Vinculada |
| Meta App | Diavolo Social Manager | ✅ Creada |
| App ID | 974196185219039 | ✅ |
| Caso de uso | Administrar mensajes y contenido en Instagram | ✅ |
| Token de acceso | Generado para @diavolo_lab | ✅ Guardar de forma segura |

### Permisos configurados

- ✅ `instagram_business_basic` — Ver perfil y contenido multimedia
- ✅ `instagram_manage_comments` — Acceder y administrar comentarios
- ✅ `instagram_business_manage_messages` — Acceder y administrar mensajes directos
- ✅ `instagram_content_publish` — Acceder al contenido y publicarlo
- ✅ Estadísticas — Acceder y administrar estadísticas

### Modo actual: Desarrollo
La app funciona en modo desarrollo con @diavolo_lab sin restricciones. Para usuarios externos se requiere revisión de Meta (1–3 semanas), que se solicitará cuando el software esté listo.

### Webhooks — Pendiente
Se configurará cuando el backend esté desplegado. Requiere una URL pública del servidor.

### Contexto: cuenta anterior de Meta
- La cuenta anterior (Diavolo Studio) tiene bloqueo permanente de WhatsApp Business
- Se creó un Business Manager nuevo y limpio con `hola@diavolo.me`
- La cuenta anterior puede dejarse inactiva sin eliminarla

---

## Panel de administración — Multi-cuenta

El sistema soporta múltiples clientes, cada uno con su propia cuenta de Instagram y credenciales independientes.

### ¿Cómo se agrega un cliente?
El administrador (equipo Diavolo) agrega manualmente las credenciales de cada cliente desde el panel de admin:
- Nombre del cliente
- Usuario de Instagram
- Instagram Account ID
- Token de acceso de Meta
- App Secret (si aplica)

Las credenciales se almacenan **encriptadas** en la base de datos. Nunca en texto plano.

### Estados de cuenta
Cada cliente puede tener uno de estos estados visible en el panel:
- 🟢 **EN CAMPAÑA** — tiene una campaña activa en curso
- 🟡 **EN PAUSA** — cuenta configurada pero sin campaña activa
- 🔴 **INACTIVA** — cuenta desconectada o con token vencido

---

## Sistema de carpetas por cliente

Cada cliente tiene su propia estructura de carpetas con sus campañas y assets:

```
clientes/
├── @diavolo_lab/          [EN CAMPAÑA]
│   ├── 2026-05_aumentar-seguidores/
│   │   ├── contexto.md
│   │   ├── aprobacion-cliente.md
│   │   └── assets/
│   │       ├── post-01.jpg
│   │       └── post-02.mp4
│   └── 2026-06_nuevo-servicio/
│       ├── contexto.md
│       ├── aprobacion-cliente.md
│       └── assets/
├── @cliente_02/           [EN PAUSA]
│   └── ...
├── @cliente_03/           [EN CAMPAÑA]
│   └── ...
```

### contexto.md — Documento interno de la campaña
```markdown
# Campaña: [nombre]
## Objetivo
## Duración y fechas
## Frecuencia de publicación
## Tono y mensajes clave
## Posts programados (fecha, formato, copy, hashtags, asset)
## Resultados al cierre
```

### aprobacion-cliente.md — Documento para el cliente
Generado automáticamente por el sistema. Incluye todo lo que el cliente necesita ver y aprobar antes de que se ejecute la campaña:
```markdown
# Plan de campaña: [nombre del cliente]
## Objetivo de la campaña
## Calendario de publicaciones
| Fecha | Hora | Formato | Copy | Hashtags | Vista previa |
## Siguiente paso: aprobar o solicitar cambios
```

Los assets viven en **Cloudflare R2** para publicación automática sin que el equipo esté conectado.

---

## Flujo principal del sistema

### 1. Planificación de campaña
```
Usuario selecciona cliente en el panel
    ↓
Abre módulo de planificación
    ↓
Chatbot con Claude pregunta por objetivos
(aumentar seguidores, promocionar servicio, engagement, etc.)
    ↓
Claude sugiere campaña completa:
duración, frecuencia, formatos, tono, horarios, hashtags
    ↓
Usuario aprueba o ajusta
    ↓
Sistema crea carpeta del cliente con contexto.md
y genera aprobacion-cliente.md para compartir
```

### 2. Producción de contenido
```
Claude genera copies, captions y hashtags (basado en contexto.md)
    ↓
Equipo diseña assets manualmente (Canva, Photoshop, etc.)
    ↓
Diseñador sube assets al dashboard (drag & drop)
    ↓
Assets se almacenan en Cloudflare R2
    ↓
Posts quedan listos en el calendario del cliente con asset + copy
```

### 3. Publicación automática
```
Scheduler detecta post programado
    ↓
Descarga asset desde Cloudflare R2
    ↓
Publica en Instagram del cliente vía Meta Graph API
    ↓
Nadie necesita estar conectado
    ↓
Webhook confirma éxito o error
    ↓
Métricas se almacenan en PostgreSQL
```

### 4. Autorrespuesta de DMs
```
Usuario manda DM en Instagram del cliente
    ↓
Meta dispara Webhook al backend
    ↓
Claude API genera respuesta contextual
    ↓
Backend responde vía Meta Graph API
    ↓
Restricción: solo dentro de ventana de 24 horas
```

---

## Módulos del sistema

### Módulo 1 — Panel de administración
- Lista de todos los clientes con estado (EN CAMPAÑA / EN PAUSA / INACTIVA)
- Agregar, editar y desactivar cuentas manualmente
- Credenciales encriptadas por cliente (token, account ID, app secret)
- Acceso rápido al calendario y campañas de cada cliente

### Módulo 2 — Planificación de campañas
- Chatbot con Claude API dentro del dashboard
- Define objetivo, duración, frecuencia, tono y hashtags
- Genera contexto.md automáticamente
- Genera aprobacion-cliente.md para compartir con el cliente
- Historial de campañas anteriores con resultados

### Módulo 3 — Generación de contenido
- Claude genera copies, captions y hashtags basados en el contexto.md
- Upload de assets desde el dashboard (drag & drop → Cloudflare R2)
- Vista de calendario por cliente con posts programados
- Aprobación interna antes de publicar

### Módulo 4 — Calendario
- Vista mensual por cliente (no global)
- Muestra día, hora, formato y estado de cada post
- Indicador visual de estado: programado, publicado, fallido
- Edición rápida de horarios desde el calendario

### Módulo 5 — Publicación automática
- Scheduler publica sin intervención manual
- Assets descargados desde Cloudflare R2 en el momento de publicación
- Cola con reintentos en caso de fallo
- Soporte: imágenes, carruseles, Reels

### Módulo 6 — Inbox unificado
- DMs y comentarios de todos los clientes en una sola bandeja
- Filtro por cuenta de cliente
- Respuestas sugeridas por Claude API
- Autorrespuestas configurables por cliente
- Historial de conversaciones por usuario

### Módulo 7 — Dashboard de métricas
- Vista por cliente
- KPIs: alcance, impresiones, engagement, seguidores
- Resultados por campaña
- Reportes semanales automáticos por correo (Resend)
- Comparativas por período

---

## Arquitectura técnica

### Stack técnico

| Capa | Tecnología | Por qué |
|---|---|---|
| Frontend | Next.js 14 (App Router) | SSR, deploy en Vercel, excelente soporte en Claude Code |
| UI | Tailwind CSS + shadcn/ui | Componentes listos, diseño limpio |
| Estado global | Zustand + React Query | Ligero y eficiente |
| Backend | FastAPI (Python) | Ligero, rápido, ideal para APIs REST y tareas asíncronas |
| ORM | SQLAlchemy + Alembic | Migraciones controladas |
| Scheduler | APScheduler → BullMQ + Redis | Publicaciones automáticas en horario |
| Auth | NextAuth.js + JWT | Sesiones seguras |
| Base de datos | PostgreSQL vía Supabase | Plan gratuito |
| Caché | Redis vía Upstash | Plan gratuito |
| Assets | Cloudflare R2 | Gratuito hasta 10 GB |
| Hosting frontend | Vercel | Plan gratuito |
| Hosting backend | Railway o Render | Plan gratuito |
| IA | Claude API (claude-sonnet) | Planificación, copies, autorrespuestas |
| Correo | Resend | Gratuito hasta 3,000/mes |

### Costos estimados

| Servicio | Uso | Costo |
|---|---|---|
| Meta Graph API | Publicar, leer DMs, métricas | Gratuito |
| Claude API | Planificación, copies, autorrespuestas | ~$5–10/mes |
| Supabase | Base de datos PostgreSQL | Gratuito |
| Cloudflare R2 | Assets de campañas | Gratuito hasta 10 GB |
| Vercel | Hosting frontend | Gratuito |
| Render / Railway | Hosting backend | Gratuito (con límites) |
| Resend | Reportes por correo | Gratuito hasta 3,000/mes |

> **Costo total estimado: menos de $10 USD/mes**

---

## Modelo de datos

```
clients          → cuentas de clientes con credenciales encriptadas y estado
campaigns        → campañas por cliente con contexto, objetivo y estado
posts            → posts programados y publicados (linked a campaign y client)
assets           → archivos en R2 (URL, tipo, campaña asociada)
messages         → DMs y comentarios del inbox por cliente
auto_replies     → reglas de respuesta automática por cliente
metrics          → métricas diarias por cuenta de cliente
scheduled_jobs   → cola de tareas pendientes
```

---

## Restricciones importantes de Meta API

- Solo responder DMs dentro de ventana de **24 horas** desde el último mensaje
- **No se puede iniciar conversación** — solo responder mensajes entrantes
- Rate limit: **200 llamadas por hora** por cuenta
- Webhooks requieren URL pública del servidor — configurar en deploy
- Reels: formato MP4, máximo 15 minutos
- Stories: **no se pueden publicar** vía API
- Tokens de Meta caducan cada **60 días** — implementar rotación automática

---

## Variables de entorno

```env
# Meta / Instagram (por cliente — almacenadas en BD encriptadas)
META_APP_ID=974196185219039
META_APP_SECRET=<ver panel de Meta developers>
META_WEBHOOK_VERIFY_TOKEN=<token personalizado>

# Claude API
ANTHROPIC_API_KEY=<obtener en console.anthropic.com>

# Base de datos
DATABASE_URL=<URL de Supabase — formato postgresql://...>
REDIS_URL=<URL de Upstash — formato redis://...>

# Almacenamiento
CLOUDFLARE_R2_BUCKET=<nombre del bucket>
CLOUDFLARE_R2_ACCESS_KEY=<key>
CLOUDFLARE_R2_SECRET_KEY=<secret>
CLOUDFLARE_R2_ENDPOINT=<endpoint de R2>

# Correo
RESEND_API_KEY=<obtener en resend.com>

# Seguridad
ENCRYPTION_KEY=<clave para encriptar tokens de clientes>
```

---

## Estructura del proyecto

```
diavolo-instagram-manager/
├── Diavolo-Instagram-Manager.md  ← este archivo (contexto maestro)
├── TODO.md                        ← tareas pendientes actualizadas
├── frontend/                      ← Next.js 14
│   ├── app/
│   │   ├── dashboard/
│   │   │   ├── clientes/          ← panel multi-cuenta
│   │   │   ├── campanas/          ← planificación y chatbot
│   │   │   ├── contenido/         ← generación y upload
│   │   │   ├── calendario/        ← programación por cliente
│   │   │   ├── inbox/             ← DMs y comentarios
│   │   │   └── metricas/          ← KPIs y reportes
│   ├── components/
│   └── ...
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
│   ├── services/
│   │   ├── claude_service.py      ← integración Claude API
│   │   ├── meta_service.py        ← integración Meta Graph API
│   │   ├── r2_service.py          ← almacenamiento Cloudflare R2
│   │   ├── encryption_service.py  ← encriptación de tokens
│   │   └── scheduler.py           ← publicación automática
│   └── ...
└── .env                           ← nunca subir a git
```

---

## Hoja de ruta del MVP

### Etapa 1: Fundación
- [x] Meta App y permisos configurados ← COMPLETADO
- [x] Token de acceso generado ← COMPLETADO
- [ ] Repositorio y estructura de proyecto
- [ ] Auth OAuth con Meta
- [ ] Supabase + modelo de datos inicial
- [ ] Panel de administración multi-cuenta
- [ ] Endpoint básico para publicar un post

### Etapa 2: Core del sistema
- [ ] Chatbot de planificación de campañas con Claude API
- [ ] Generación automática de contexto.md y aprobacion-cliente.md
- [ ] Sistema de carpetas por cliente
- [ ] Upload de assets a Cloudflare R2
- [ ] Generación de copies, captions y hashtags por campaña

### Etapa 3: Automatización
- [ ] Calendario por cliente
- [ ] Scheduler de publicación automática
- [ ] Inbox de DMs y comentarios con filtro por cliente
- [ ] Autorrespuestas con IA por cliente
- [ ] Webhooks con URL del servidor
- [ ] Rotación automática de tokens de Meta

### Etapa 4: Pulido y deploy
- [ ] Dashboard de métricas por cliente y campaña
- [ ] Reportes automáticos por correo
- [ ] Deploy Vercel + Railway
- [ ] Pruebas E2E y corrección de errores
- [ ] Documentación de uso interno

---

## Reglas para Claude Code

1. **Nunca hardcodear credenciales** — siempre usar variables de entorno
2. **Tokens de clientes siempre encriptados** — usar encryption_service.py
3. **Toda lógica es por cliente** — nunca mezclar datos entre cuentas
4. **Generar tests** junto con cada función nueva (Pytest backend, Playwright E2E)
5. **Actualizar TODO.md** al terminar cada tarea
6. **Pedir confirmación** antes de modificar modelos de base de datos existentes
7. **Un módulo a la vez** — no mezclar lógica de módulos distintos
8. **Comentar en español** — el equipo es hispanohablante
9. **Assets siempre en R2** — nunca almacenar archivos en el servidor local

---

## Criterios de éxito del MVP

- [ ] Agregar un cliente nuevo con sus credenciales en menos de 5 minutos
- [ ] Planificar una campaña completa desde el chatbot en menos de 10 minutos
- [ ] Generar y exportar el documento de aprobación para el cliente automáticamente
- [ ] Subir un asset y que quede listo para publicación automática
- [ ] Publicar un post programado sin intervención manual
- [ ] Ver el calendario de publicaciones por cliente
- [ ] Responder un DM desde el inbox unificado
- [ ] Costo mensual inferior a $10 USD

---

*Diavolo Instagram Manager — Documento maestro del proyecto*
*Versión 2.0 — Mayo 2026*
