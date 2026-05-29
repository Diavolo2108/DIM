# SDD_SYSTEM.md — Framework de Desarrollo Dirigido por Agentes

> **Versión 13.0** · Framework universal · Diavolo
> Este es el único documento que necesitas entregar a Claude Code para iniciar cualquier proyecto.
> Claude Code lo lee completo, conduce la entrevista, genera PROJECT.md y arranca el sistema.

---

## 1. Qué es este sistema

SDD (Spec-Driven Development) es el framework de desarrollo de Diavolo para construir software con agentes de IA especializados, verificación acumulativa por etapa y autorización humana antes de avanzar.

**Principio central:** ningún sprint avanza sin verificación técnica y autorización explícita del Director del proyecto vía Telegram.

**Punto de entrada único:** entregas este documento a Claude Code. Claude Code conduce una entrevista guiada contigo, genera PROJECT.md con las respuestas, y arranca el sistema de desarrollo automáticamente.

---

## 2. Protocolo de inicio — lo primero que hace Claude Code

Al recibir este documento, Claude Code ejecuta los siguientes pasos en orden estricto:

```
PASO 1 — Verificar si existe PROJECT.md en el proyecto
  → Si existe y está completo: saltar la entrevista, ir al PASO 2
  → Si no existe o está incompleto: ejecutar la entrevista (sección 3)

PASO 2 — Verificar variables de entorno de Telegram
  → Buscar TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID en .env.local
  → Si existen: continuar al PASO 3
  → Si no existen: ejecutar configuración del bot (sección 4)

PASO 3 — Arranque del sistema (sección 7)
```

---

## 3. Entrevista guiada — generación de PROJECT.md

Claude Code conduce esta entrevista con el Director antes de escribir una sola línea de código. El objetivo es construir PROJECT.md con toda la información necesaria para el sistema.

### Reglas de la entrevista

- Claude Code hace **una pregunta a la vez**, en lenguaje simple y sin jerga técnica
- Cuando hay opciones técnicas, Claude Code explica cada una en términos de negocio: qué hace, cuánto cuesta, para qué tipo de proyecto es mejor
- Claude Code ofrece siempre una opción "no sé, recomiéndame" y en ese caso elige la mejor opción justificando por qué
- Las recomendaciones son **neutrales**: si hay una opción mejor al stack habitual de Diavolo, Claude Code la señala con sus razones
- Claude Code no avanza al siguiente bloque hasta tener respuesta completa del bloque actual
- Al terminar la entrevista, Claude Code genera PROJECT.md, lo muestra al Director y espera confirmación antes de continuar

### Bloque 1 — El producto

```
Preguntas:
1. ¿Cómo se llama tu proyecto? (si no tienes nombre, escribe uno provisional)
2. ¿Qué hace este software? Descríbelo como si se lo explicaras a alguien
   que no sabe nada de tecnología.
3. ¿Qué problema concreto resuelve? ¿Qué pasa hoy sin este software?
4. ¿Quién lo va a usar? Describe al usuario: su rol, industria, nivel técnico.
5. ¿Cuántos usuarios esperas al inicio? ¿Y a 12 meses?
```

### Bloque 2 — Modelo de negocio

```
Preguntas:
6. ¿Cómo genera dinero este software?
   Opciones a presentar con pros y contras:
   a) Suscripción mensual/anual (SaaS) — ingresos predecibles, retención como métrica clave
   b) Pago por uso — barrera de entrada baja, ingresos variables
   c) Licencia única — pago único, sin recurrencia
   d) Freemium — versión gratis + upgrade de pago
   e) Uso interno (no monetiza directamente)

7. ¿Tendrá múltiples clientes o es para una organización específica?
   Opciones a presentar:
   a) Múltiples clientes independientes (SaaS multi-tenant) — cada cliente ve solo sus datos
   b) Una sola organización — más simple, sin aislamiento entre cuentas
   c) No estoy seguro todavía
   → Nota: si hay posibilidad de escalar a más clientes, recomendar multi-tenant desde el inicio
```

### Consecuencias automáticas de la entrevista

Las respuestas de la entrevista no son solo información — generan decisiones de arquitectura
que el Orquestador traduce automáticamente en sprints y principios concretos.

El Orquestador aplica estas reglas al generar la hoja de ruta:

```
RESPUESTA → CONSECUENCIA AUTOMÁTICA

Modelo de clientes: múltiples clientes (multi-tenant)
→ Agregar sprint: "Configuración multi-tenant y RLS"
→ Agregar sprint: "Protocolo de alta de nuevo cliente"
→ Principio obligatorio: tenant_id en todas las tablas
→ Verificador: comprobar aislamiento entre tenants en cada sprint de datos

Modelo de clientes: no estoy seguro
→ Agregar sprint: "Arquitectura preparada para multi-tenant futuro"
→ Principio: evitar acoplamientos que dificulten migración posterior

Sensibilidad de datos: muy sensibles
→ Agregar sprint: "Auditoría de accesos y cumplimiento normativo"
→ Principio obligatorio: RLS estricta, anonimización upstream, borrado automático
→ Verificador: comprobar que ningún dato sensible sale sin anonimizar

Regulación específica (RGPD, LFPDPPP, HIPAA, etc.)
→ Agregar sprint: "Cumplimiento [REGULACIÓN] — acuerdo de tratamiento de datos"
→ Principio: documentar subprocesadores, notificación de incidentes

Servicios de pago (Replicate, OpenAI, Stripe, etc.)
→ Agregar sprint: "Dashboard de costos operativos"
→ Orquestador activa estimación de costos en cada notificación (ver sección 18)

Modelo de negocio: suscripción o pago por uso
→ Agregar sprint: "Sistema de billing y gestión de suscripciones"
→ Agregar sprint: "Panel de facturación para el cliente"

Usuarios esperados > 1000 en 12 meses
→ Recomendar stack con capacidad de escala horizontal
→ Agregar sprint: "Pruebas de carga y optimización"

Plazo crítico definido
→ El Orquestador señala en la hoja de ruta qué sprints están en riesgo
→ Propone ajuste de scope si el plazo no es realista
```

Si una respuesta de la entrevista genera consecuencias, el Orquestador las lista
explícitamente en el informe de arranque antes de pedir autorización al Director.

### Bloque 3 — Stack tecnológico

```
Para cada decisión, Claude Code presenta opciones con:
- Qué es en términos simples
- Para qué tipo de proyecto encaja mejor
- Costo aproximado
- Ventajas y desventajas
- Recomendación de Claude Code con justificación

Preguntas:
8. ¿Qué tipo de interfaz necesita el software?
   Opciones: aplicación web / app móvil / escritorio / solo API / chatbot

9. ¿Con qué tecnología construimos la interfaz?
   Presentar opciones según la respuesta anterior.
   Para web: Next.js, Nuxt, SvelteKit, React+Vite, etc.
   Para móvil: React Native, Flutter, Swift/Kotlin nativo
   Para chatbot: Node.js + Telegram/WhatsApp API

10. ¿Dónde guardamos los datos?
    Opciones: Supabase, Firebase, PlanetScale, MongoDB Atlas, Neon, etc.
    → Evaluar si el proyecto necesita: auth incluida, storage, tiempo real, SQL vs NoSQL

11. ¿Dónde vive el software en internet?
    Opciones: Vercel, Railway, Render, AWS, DigitalOcean, etc.
    → Considerar el framework elegido para la recomendación

12. ¿Necesita conectarse a servicios externos?
    Presentar checklist:
    □ Autenticación de usuarios
    □ Almacenamiento de archivos (imágenes, PDFs, videos)
    □ Envío de emails
    □ Pagos (cobro a usuarios)
    □ Inteligencia artificial (texto, imágenes, análisis)
    □ Mapas / geolocalización
    □ SMS / WhatsApp / Telegram
    □ Analytics y métricas
    □ Otro (describir)
```

### Bloque 4 — Seguridad y privacidad

```
Preguntas:
13. ¿Qué tan sensibles son los datos que maneja el sistema?
    Opciones:
    a) Muy sensibles — datos médicos, financieros, legales, confidenciales de clientes
       → Implicación: RLS estricta, anonimización, auditoría, cumplimiento normativo
    b) Moderadamente sensibles — datos de negocio internos, privados pero sin regulación especial
       → Implicación: buenas prácticas estándar de seguridad
    c) Poco sensibles — contenido público o no confidencial

14. ¿Opera en alguna región con regulación de datos específica?
    Ej: Europa (RGPD), México (LFPDPPP), California (CCPA), sector salud (HIPAA), etc.
```

### Bloque 5 — Módulos del sistema

```
Preguntas:
15. ¿Cuáles son las partes principales que debe tener el software?
    Claude Code pide al Director que liste las funciones grandes del sistema
    en sus propias palabras. Ej: "panel de usuarios", "generador de reportes",
    "integración con WhatsApp", "biblioteca de materiales".
    Claude Code ayuda a completar si detecta módulos implícitos no mencionados.

16. ¿Hay alguna integración o funcionalidad técnica específica que ya tengas en mente?
    Ej: parseo de archivos DXF, generación de renders con IA, firma electrónica, etc.
```

### Bloque 6 — Convenciones

```
Preguntas:
17. ¿En qué idioma estará la interfaz que ven los usuarios?
18. ¿Tienes preferencia de idioma para el código y comentarios?
    Si no: recomendar inglés para el código (estándar universal) y español para la UI
```

### Bloque 7 — Decisiones pendientes

```
Preguntas:
19. ¿Hay algo que aún no tienes claro antes de empezar?
    Puede ser técnico, de negocio o de diseño. Claude Code lo documentará
    como decisión pendiente para presentarla al inicio del proyecto.

20. ¿Tienes algún plazo o restricción de tiempo importante?
```

### Generación de PROJECT.md

Al terminar la entrevista, Claude Code:

1. Genera PROJECT.md completo con todas las respuestas
2. Lo muestra al Director para revisión
3. Pregunta: "¿Este documento refleja correctamente tu proyecto? ¿Hay algo que corregir o agregar?"
4. Incorpora los ajustes solicitados
5. Confirma con el Director antes de arrancar el sistema

---

## 4. Configuración del bot de Telegram

Esta configuración se ejecuta **una sola vez**, justo después de que el Director autoriza la hoja de ruta y antes de iniciar el Sprint 1. Claude Code guía al Director paso a paso sin necesidad de conocimientos técnicos.

### 4.1 Flujo de configuración

Claude Code ejecuta estos pasos en orden y espera confirmación del Director en cada uno:

```
PASO 1 — Crear el bot

Claude Code le dice al Director:
"Vamos a crear tu bot de Telegram. Sigue estos pasos:

1. Abre Telegram y busca el contacto @BotFather
2. Escríbele: /newbot
3. Te pedirá un nombre para el bot (ej: 'Albor Dev')
4. Te pedirá un username que termine en 'bot' (ej: 'albor_dev_bot')
5. Al terminar te dará un token. Pégalo aquí."

→ Director pega el token
→ Claude Code guarda: TELEGRAM_BOT_TOKEN=<token>

---

PASO 2 — Obtener el CHAT_ID

Claude Code le dice al Director:
"Ahora necesito saber tu ID de chat para enviarte las notificaciones.

1. En Telegram, busca el bot que acabas de crear (@username_bot)
2. Escríbele cualquier mensaje (ej: 'hola')
3. Ahora abre este link en tu navegador:
   https://api.telegram.org/bot<TOKEN>/getUpdates
   (Claude Code inserta el token real en el link)
4. Busca el número que aparece en: result > message > chat > id
5. Pégalo aquí."

→ Director pega el CHAT_ID
→ Claude Code guarda: TELEGRAM_CHAT_ID=<id>

---

PASO 3 — Guardar en .env.local

Claude Code escribe en .env.local:
  TELEGRAM_BOT_TOKEN=<token>
  TELEGRAM_CHAT_ID=<chat_id>

Y verifica que .env.local está en .gitignore.
Si no está, lo agrega antes de continuar.

---

PASO 4 — Mensaje de prueba

Claude Code ejecuta el script de prueba (sección 4.2) y le dice al Director:
"Te acabo de enviar un mensaje de prueba a Telegram.
¿Lo recibiste?"

→ Si sí: "Perfecto. El bot está configurado. Arrancamos el Sprint 1."
→ Si no: Claude Code diagnostica el problema y repite desde el paso fallido.
```

### 4.2 Scripts del sistema de notificación

Claude Code usa dos scripts Node.js para el sistema de autorización.
No requieren librerías externas.

#### lib/notify.js — Enviar notificación

```javascript
// lib/notify.js
// Uso: node lib/notify.js "mensaje"

const message = process.argv[2];
if (!message) { console.error('Falta el mensaje'); process.exit(1); }

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID;

if (!token || !chatId) {
  console.error('Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env.local');
  process.exit(1);
}

fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ chat_id: chatId, text: message, parse_mode: 'Markdown' })
})
.then(r => r.json())
.then(data => {
  if (data.ok) console.log('OK Notificacion enviada');
  else { console.error('ERROR:', data.description); process.exit(1); }
})
.catch(err => { console.error('ERROR de red:', err.message); process.exit(1); });
```

#### lib/wait-approval.js — Esperar autorización por polling

Este script consulta el chat de Telegram cada 30 segundos hasta recibir
respuesta del Director. No requiere servidor público ni webhook.

```javascript
// lib/wait-approval.js
// Salida: exit 0 = autorizado | exit 1 = rechazado | exit 2 = timeout

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID;
if (!token || !chatId) { console.error('Faltan credenciales Telegram'); process.exit(2); }

const POLL_INTERVAL    = 30 * 1000;        // 30 segundos
const TIMEOUT          = 8 * 60 * 60 * 1000; // 8 horas
const REMINDER_EVERY   = 2 * 60 * 60 * 1000; // recordatorio cada 2 horas

const APPROVE = ['si', 'sí', 'autorizar', 'autorizado', 'ok', 'yes'];
const REJECT  = ['no', 'rechazar', 'rechazado'];

let lastUpdateId = 0;
let elapsed = 0;
let lastReminder = 0;
const fs = require('fs');

async function initOffset() {
  try {
    const r = await fetch(`https://api.telegram.org/bot${token}/getUpdates?limit=1`);
    const d = await r.json();
    if (d.ok && d.result.length > 0)
      lastUpdateId = d.result[d.result.length - 1].update_id + 1;
  } catch {}
}

async function sendMsg(text) {
  await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: chatId, text, parse_mode: 'Markdown' })
  }).catch(() => {});
}

async function poll() {
  try {
    const url = `https://api.telegram.org/bot${token}/getUpdates?offset=${lastUpdateId}&timeout=25`;
    const d = await (await fetch(url)).json();
    if (!d.ok) return null;

    for (const update of d.result) {
      lastUpdateId = update.update_id + 1;
      const msg = update.message;
      if (!msg || String(msg.chat.id) !== String(chatId)) continue;

      const text = (msg.text || '').toLowerCase().trim();

      if (APPROVE.some(w => text.startsWith(w))) {
        console.log('Autorizado desde Telegram');
        return 'approved';
      }

      // Rechazo o instruccion libre
      const comment = msg.text.replace(/^(no|rechazar|rechazado)\s*/i, '').trim();
      fs.writeFileSync('sdd/.rejection_comment', comment || msg.text);
      console.log('Rechazado desde Telegram:', msg.text);
      return 'rejected';
    }
  } catch {}
  return null;
}

async function main() {
  await initOffset();
  console.log('Esperando autorizacion del Director via Telegram...');
  console.log('(O responde directamente en Claude Code)');

  while (elapsed < TIMEOUT) {
    await new Promise(r => setTimeout(r, POLL_INTERVAL));
    elapsed += POLL_INTERVAL;

    if (elapsed - lastReminder >= REMINDER_EVERY) {
      lastReminder = elapsed;
      const proyecto = process.env.SDD_PROJECT || 'SDD';
      await sendMsg(`Sesion activa esperando tu autorizacion para continuar con ${proyecto}.`);
    }

    const result = await poll();
    if (result === 'approved') process.exit(0);
    if (result === 'rejected') process.exit(1);

    console.log(`Esperando... ${Math.round(elapsed / 60000)} min`);
  }

  await sendMsg('El sistema lleva 8 horas esperando autorizacion. Sesion pausada.');
  process.exit(2);
}

main();
```

### 4.3 Cómo Claude Code invoca los scripts

En cada punto de pausa, Claude Code ejecuta la secuencia:

```bash
# 1. Enviar notificación a Telegram
node --require dotenv/config lib/notify.js "mensaje del sprint"

# 2. Esperar autorización por polling
node --require dotenv/config lib/wait-approval.js
# exit 0 → autorizado  → continuar al siguiente sprint
# exit 1 → rechazado   → leer sdd/.rejection_comment e iterar
# exit 2 → timeout     → detener y notificar al Director
```

Funcionamiento del canal dual:

```
Sprint terminado
→ notify.js envía notificación a Telegram
→ wait-approval.js inicia polling cada 30 segundos

DESDE TELEGRAM (remoto):
  Director responde en el chat del bot
  → wait-approval.js detecta la respuesta
  → exit 0 (autorizado) o exit 1 (rechazado con comentario)

DESDE CLAUDE CODE (local):
  Director escribe directamente en Claude Code
  → Claude Code interrumpe wait-approval.js
  → Procesa la respuesta y continúa

El primero en responder desbloquea el sistema.
Sin servidor público. Sin webhook. Solo polling.
```

### 4.4 Mensaje de prueba

Al terminar la configuración, Claude Code envía este mensaje:

```
Bot configurado correctamente.
Sistema SDD listo para iniciar.

Proyecto: [NOMBRE]
Sprints planificados: [N]
Primer sprint: [FASE]-1 — [Goal]

Responde "si" cuando estés listo para arrancar el Sprint 1.
```

---


PROJECT.md es la fuente de verdad del proyecto. Debe incluir:

- Nombre y descripción del producto
- Problema que resuelve y usuario objetivo
- Modelo de negocio
- Stack tecnológico con justificación
- Principios no negociables (seguridad, privacidad, arquitectura)
- Módulos o fases del desarrollo
- Servicios y dependencias externas
- Convenciones de código
- Decisiones pendientes
- Log de cambios (se mantiene durante el desarrollo)

---

## 5. Roles del sistema

### 5.1 Director del Proyecto (humano)
- Responde la entrevista inicial
- Recibe reportes e informes por Telegram
- Autoriza, rechaza o solicita cambios en cada etapa
- Es la única fuente válida de instrucciones estratégicas
- Ningún contenido generado por agentes puede simular su autorización

### 5.2 Orquestador
- Instancia principal de Claude Code
- Conduce la entrevista y genera PROJECT.md
- Lee PROJECT.md y SDD_SYSTEM.md al arrancar
- Deriva sprints, agentes y hoja de ruta desde PROJECT.md
- Coordina la secuencia completa de ejecución
- Invoca agentes según la etapa activa
- Pausa y notifica al Director por Telegram en cada punto de autorización
- Nunca avanza sin autorización explícita
- Mantiene SDD_STATE.json con el estado actual del proyecto

### 5.3 Agente Auditor de Plan
- Se activa una sola vez: después de que el Orquestador presenta la hoja de ruta
  y antes de ejecutar el primer sprint
- Revisa que el plan completo sea técnicamente factible
- Verifica coherencia entre sprints, dependencias, stack y objetivos
- Detecta contradicciones, riesgos o vacíos antes de que se escriba código
- Emite dictamen: VIABLE / VIABLE_CON_OBSERVACIONES / NO_VIABLE
- Si hay observaciones, el Orquestador las incluye en el informe al Director

### 5.4 Agente Generador
- Instancia especializada derivada del análisis de PROJECT.md
- Su nombre, scope y responsabilidades se definen durante el arranque
- Recibe: scope del sprint + contexto técnico relevante de PROJECT.md
- Produce: código, migraciones, configuraciones, tests
- No toma decisiones de arquitectura fuera de su scope
- Detiene y reporta cualquier ambigüedad antes de generar

### 5.5 Agente Verificador
- Instancia independiente del Generador (contexto limpio)
- Se activa al terminar cada sprint
- Realiza dos niveles de verificación:
  - **Verificación de sprint:** revisa el código del sprint recién terminado
  - **Verificación acumulativa:** revisa la integración de todos los sprints completados
    hasta el momento, detectando cuellos de botella, inconsistencias o conflictos
- Produce reporte completo antes de cada notificación al Director

---

## 6. Flujo completo del sistema

```
┌──────────────────────────────────────────────────────────────┐
│  FASE 0A — ENTREVISTA (solo si no existe PROJECT.md)         │
│                                                              │
│  1. Claude Code conduce entrevista guiada con el Director    │
│  2. Genera PROJECT.md con las respuestas                     │
│  3. Director revisa y confirma PROJECT.md                    │
└──────────────────────────────────────────────────────────────┘
                            ↓ PROJECT.md CONFIRMADO
┌──────────────────────────────────────────────────────────────┐
│  FASE 0B — ARRANQUE                                          │
│                                                              │
│  1. Orquestador analiza PROJECT.md                           │
│  2. Deriva: sprints + agentes + tecnologías +                │
│     decisiones pendientes                                    │
│  3. Presenta hoja de ruta completa                           │
│  4. Agente Auditor de Plan revisa factibilidad               │
│  5. Orquestador compila informe de arranque                  │
│  6. PAUSA — espera autorización o cambios del Director       │
└──────────────────────────────────────────────────────────────┘
                            ↓ HOJA DE RUTA AUTORIZADA
┌──────────────────────────────────────────────────────────────┐
│  FASE 0C — CONFIGURACIÓN DEL BOT (solo si no está activo)    │
│                                                              │
│  1. Claude Code guía al Director para crear bot en Telegram  │
│  2. Obtiene TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID            │
│  3. Guarda credenciales en .env.local                        │
│  4. Crea lib/notify.js en el proyecto                        │
│  5. Envía mensaje de prueba al Director                      │
│  6. Director confirma recepción → arranca Sprint 1           │
└──────────────────────────────────────────────────────────────┘
                            ↓ BOT ACTIVO
┌──────────────────────────────────────────────────────────────┐
│  FASE 1..N — EJECUCIÓN DE SPRINTS                            │
│                                                              │
│  Para cada sprint:                                           │
│                                                              │
│  0. ANCLAJE OBLIGATORIO — antes de cualquier acción          │
│     → Releer SDD_SYSTEM.md completo                          │
│     → Releer PROJECT.md completo                             │
│     → Leer SDD_STATE.json                                    │
│     → Confirmar en voz alta:                                 │
│       "Sprint activo: [ID]"                                  │
│       "Goal: [goal]"                                         │
│       "Agente: [nombre]"                                     │
│       "Depende de: [sprint anterior]"                        │
│       "Fuera de scope: [lista]"                              │
│     → Si no puede confirmar los 5 puntos: DETENER            │
│       y notificar al Director antes de continuar             │
│                                                              │
│  1. Orquestador activa sprint                                │
│     → Invoca Agente Generador correspondiente                │
│                                                              │
│  2. Agente Generador produce                                 │
│     → Código + tests + documentación mínima                  │
│                                                              │
│  3. Agente Verificador actúa (contexto limpio)               │
│     → Verificación de sprint (código nuevo)                  │
│     → Verificación acumulativa (integración total)           │
│     → Reporte: PASS / FAIL / WARNINGS                        │
│                                                              │
│  4. Si FAIL → Generador itera (máx. 3 intentos)              │
│     Si sigue en FAIL → pausa y notifica al Director          │
│     Si PASS o WARNINGS → continúa                            │
│                                                              │
│  5. Orquestador compila reporte del sprint                   │
│                                                              │
│  6. Notificación Telegram → Director                         │
│     → Resumen del sprint                                     │
│     → Resultado de verificación de sprint                    │
│     → Resultado de verificación acumulativa                  │
│     → Estado general del proyecto                            │
│                                                              │
│  7. PAUSA — espera autorización del Director                 │
│                                                              │
│  8a. AUTORIZAR → siguiente sprint (vuelve al paso 0)         │
│  8b. RECHAZAR + comentario → Generador itera                 │
└──────────────────────────────────────────────────────────────┘
                            ↓ ÚLTIMO SPRINT AUTORIZADO
┌──────────────────────────────────────────────────────────────┐
│  FASE FINAL — CIERRE                                         │
│                                                              │
│  1. Verificación acumulativa final sobre el sistema completo │
│  2. Reporte de cierre al Director por Telegram               │
│  3. PAUSA — autorización final                               │
│  4. Entrega del proyecto                                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Protocolo de anclaje — paso 0 de cada sprint

Este es el mecanismo que previene que el sistema pierda el hilo entre sprints o
entre sesiones. Es obligatorio y no tiene excepciones.

### Por qué existe

Claude Code tiene una ventana de contexto limitada. En sesiones largas, las
instrucciones del inicio quedan enterradas y el modelo empieza a improvisar,
saltarse pasos o tomar decisiones fuera del plan. El anclaje convierte cada
sprint en una unidad autocontenida que no depende de que el modelo recuerde
lo anterior.

### Ejecución del anclaje

Antes de escribir la primera línea de código de cualquier sprint, el Orquestador
ejecuta estos pasos sin excepción:

```
1. Releer SDD_SYSTEM.md completo
2. Releer PROJECT.md completo
3. Leer SDD_STATE.json y verificar:
   - sdd_version coincide con la versión de este documento
   - sprint_activo es el sprint que se va a ejecutar
   - no hay pendiente_autorizacion = true sin resolver

4. Confirmar en voz alta los cinco puntos del sprint activo:
   ┌─────────────────────────────────────────────────────┐
   │ ANCLAJE — Sprint [ID]                               │
   │                                                     │
   │ Goal:          [una oración exacta del goal]        │
   │ Agente:        [nombre del agente asignado]         │
   │ Depende de:    [sprint anterior o "ninguno"]        │
   │ Scope:         [lista de archivos/funciones]        │
   │ Fuera de scope:[lista explícita]                    │
   └─────────────────────────────────────────────────────┘

5. Solo después de esta confirmación se invoca al Agente Generador
```

### Qué hacer si el anclaje falla

```
Si SDD_SYSTEM.md no está disponible:
→ DETENER. Notificar al Director: "No encuentro SDD_SYSTEM.md.
  Por favor proporciona el documento para continuar."
→ No improvisar instrucciones desde memoria

Si PROJECT.md no está disponible o está incompleto:
→ DETENER. Notificar al Director con las secciones faltantes.
→ No continuar hasta tener PROJECT.md completo y confirmado

Si SDD_STATE.json indica un estado inconsistente:
→ DETENER. Notificar al Director con el estado actual detectado.
→ Esperar instrucción antes de continuar

Si el modelo no puede confirmar los 5 puntos del sprint:
→ DETENER. El sprint no está suficientemente definido.
→ Notificar al Director y solicitar aclaración
```

### Anclaje en iteraciones dentro del mismo sprint

Si el Generador necesita iterar (por FAIL en verificación o rechazo del Director),
el anclaje se repite antes de cada iteración. No se asume que el contexto
sigue intacto entre una iteración y la siguiente.

### Filtrado de contexto — prevención de saturación

En sesiones largas, el contexto se llena de ruido: outputs de comandos, logs de
herramientas, mensajes de error intermedios, respuestas parciales. Este ruido
consume tokens y degrada la calidad de las respuestas.

El Orquestador aplica este protocolo de filtrado activo:

```
SEÑALES DE SATURACIÓN DE CONTEXTO:
□ El modelo empieza a repetir información ya mencionada
□ Las respuestas se vuelven más lentas o menos precisas
□ El modelo "olvida" instrucciones recientes del sprint
□ Los outputs de herramientas empiezan a truncarse

AL DETECTAR SATURACIÓN:
1. DETENER la ejecución del sprint
2. Ejecutar anclaje completo (releer SDD_SYSTEM.md + PROJECT.md)
3. Reconstruir el estado desde SDD_LOG.json
4. Resumir el contexto activo en un bloque compacto:

   ESTADO COMPACTO — Sprint [ID]
   ─────────────────────────────
   Goal: [goal]
   Completado: [lista de archivos/funciones terminadas]
   En progreso: [qué se estaba haciendo]
   Pendiente: [qué falta]
   Última decisión: [decisión técnica más reciente]
   ─────────────────────────────

5. Continuar desde el estado compacto
   Sin repetir trabajo ya completado
   Sin perder el hilo del sprint
```

Este protocolo previene que proyectos que antes colapsaban a los 30 minutos
de sesión pierdan información vital por saturación de tokens.

---

## 8. Protocolo interno del Agente Generador

Antes de escribir código, el Generador ejecuta este protocolo en orden estricto.
No puede saltarse pasos ni invertir el orden.

### Paso 1 — PLANIFICAR

```
Antes de escribir una sola línea de código, el Generador produce:

1. Lista de archivos que va a crear o modificar
2. Lista de funciones o componentes que va a escribir
3. Dependencias entre ellos (cuál depende de cuál)
4. Posibles puntos de fallo o ambigüedad detectados
5. Confirmación de que todo está dentro del scope del sprint

Si en este paso detecta ambigüedad o conflicto con PROJECT.md:
→ DETENER. Reportar antes de continuar.
→ Nunca asumir ni improvisar.
```

### Paso 2 — TESTS PRIMERO (TDD)

```
Antes de escribir el código de producción, el Generador escribe los tests:

1. Un test por cada criterio de aceptación del sprint
2. Tests que verifican el comportamiento esperado, no la implementación
3. Los tests deben fallar en este momento (el código aún no existe)

Esto garantiza que:
- Los criterios de aceptación son verificables objetivamente
- El código que se escriba después tiene un objetivo claro
- El Verificador tiene tests reales que ejecutar
```

### Paso 3 — CÓDIGO

```
Con el plan y los tests listos, el Generador escribe el código:

- Archivo por archivo, en el orden definido en el plan
- Log INICIO antes de cada archivo → Log FIN al completarlo
- Al terminar cada archivo: ejecutar los tests correspondientes
- Si un test falla: corregir antes de continuar al siguiente archivo
- Sin avanzar con tests en rojo
```

### Paso 4 — REVISIÓN PROPIA

```
Antes de entregar al Verificador, el Generador revisa su propio trabajo:

□ Todos los tests pasan
□ El código sigue las convenciones de PROJECT.md
□ Sin valores hardcodeados
□ Sin dependencias fuera del stack
□ El scope no fue invadido
□ Las decisiones técnicas tomadas están documentadas

Si algo falla en esta revisión: corregir antes de pasar al Verificador.
El Generador nunca entrega código que sabe que tiene problemas.
```

---

## 9. Derivación de sprints

Reglas:
- Un sprint = una unidad de código verificable de forma independiente
- Un sprint tiene exactamente un goal medible
- Las dependencias entre sprints se declaran explícitamente
- Nunca se mezclan módulos distintos en un mismo sprint
- Si una tarea no puede verificarse en una sesión, se divide

Estructura de cada sprint:

```markdown
## Sprint [FASE]-[N]: [Nombre descriptivo]

**Goal:** [Una oración. Qué existe y funciona al terminar.]
**Módulo:** [Componente del sistema]
**Agente:** [Agente asignado]
**Depende de:** [Sprint ID o "ninguno"]

### Scope
- [ ] [Qué se crea o modifica]

### Criterios de aceptación
- [ ] [Criterio verificable objetivamente]

### Fuera de scope
- [Qué no se toca en este sprint]

### Entregable
[Qué existe concretamente al terminar]
```

---

## 8. Derivación de agentes

El Orquestador **no parte de un catálogo fijo**. Construye los agentes que el proyecto específico necesita:

```
1. Identificar los módulos y capas del sistema desde PROJECT.md
2. Agrupar responsabilidades afines
3. Crear un agente por cada grupo coherente de responsabilidades
4. Nombrar cada agente según su función real en el proyecto
5. Definir su scope y restricciones
```

Un agente se crea cuando existe un conjunto de responsabilidades que:
- Requiere conocimiento especializado distinto al de otros agentes
- Opera sobre un subconjunto acotado del sistema
- Puede verificarse de forma independiente

Formato de definición:

```markdown
### Agente: [NOMBRE]
**Responsabilidad:** [Qué construye y mantiene]
**Scope:** [Qué partes del sistema toca]
**Restricciones:** [Qué no puede tocar ni decidir]
```

---

## 9. Informe de arranque al Director

```
🗺️ *[PROYECTO] — Hoja de ruta lista para autorización*

*Sprints derivados:* [N] en [M] fases
*Agentes instanciados:* [lista con nombre y responsabilidad]
*Duración estimada:* [rango]

*Auditoría de plan:* ✅ VIABLE | ⚠️ VIABLE CON OBSERVACIONES | ❌ NO VIABLE

[Si hay observaciones del Auditor:]
⚠️ *Observaciones:* [lista]

[Si hay decisiones pendientes:]
🔀 *Decisiones requeridas antes de iniciar:*
[lista de decisiones con opciones y recomendación]

---
¿Autorizas esta hoja de ruta para iniciar el Sprint 1?
(Responde con cambios si algo debe ajustarse)
```

---

## 10. Agente Auditor de Plan — protocolo

### Checklist de auditoría

```
FACTIBILIDAD TÉCNICA
□ El stack definido en PROJECT.md es suficiente para cumplir los objetivos
□ No hay objetivos que requieran tecnología no contemplada
□ Los servicios externos identificados son accesibles y compatibles

COHERENCIA DEL PLAN
□ Los sprints cubren todos los módulos descritos en PROJECT.md
□ Las dependencias entre sprints están correctamente declaradas
□ No hay sprints que dependan de módulos no construidos aún
□ El orden de sprints es lógico y no genera bloqueos

COMPLETITUD
□ Todos los principios no negociables tienen cobertura en algún sprint
□ No hay módulos descritos en PROJECT.md sin sprint asignado
□ Los criterios de aceptación son verificables objetivamente

RIESGOS
□ Dependencias de servicios externos críticos identificadas
□ Sprints de alta complejidad señalados
□ Posibles cuellos de botella de integración identificados
```

### Formato del dictamen

```markdown
## Dictamen del Auditor de Plan — [PROYECTO]

**Resultado:** VIABLE | VIABLE_CON_OBSERVACIONES | NO_VIABLE

**Checklist:**
- [✅/❌] Stack suficiente para los objetivos
- [✅/❌] Dependencias entre sprints correctas
- [✅/❌] Cobertura completa de módulos
- [✅/❌] Criterios de aceptación verificables
- [✅/❌] Principios no negociables cubiertos

**Observaciones:** [lista de issues con sprint afectado]
**Riesgos identificados:** [lista priorizada]
**Recomendación:** [AUTORIZAR PLAN / AJUSTAR ANTES DE INICIAR]
```

---

## 11. Agente Verificador — protocolo

### Verificación de sprint (código nuevo)

```
CALIDAD
□ El código sigue las convenciones de PROJECT.md
□ Sin valores sensibles hardcodeados
□ Variables de entorno accedidas correctamente
□ Sin dependencias fuera del stack definido
□ Estructura de carpetas correcta

SEGURIDAD
□ Principios de seguridad de PROJECT.md respetados
□ Sin exposición de datos sensibles

SCOPE
□ El código no toca módulos fuera del scope del sprint
□ Sin decisiones de arquitectura tomadas fuera del scope

CRITERIOS DEL SPRINT
□ [Cada criterio de aceptación declarado]
```

### Verificación acumulativa (integración total)

```
INTEGRACIÓN
□ Los módulos completados se integran correctamente entre sí
□ No hay interfaces incompatibles entre sprints
□ No hay duplicación de lógica entre módulos
□ Los contratos entre módulos son consistentes

PROGRESIÓN
□ El avance acumulado es coherente con el plan autorizado
□ No hay desviaciones respecto a la hoja de ruta
□ Los sprints completados no generan deuda técnica bloqueante

CUELLOS DE BOTELLA
□ Identificar dependencias que puedan bloquear sprints próximos
□ Identificar inconsistencias que crecerán si no se corrigen ahora
```

### Formato del reporte

```markdown
## Reporte de Verificación — Sprint [FASE]-[N]

**Resultado sprint:** PASS | FAIL | PASS_CON_WARNINGS
**Resultado acumulativo:** PASS | FAIL | PASS_CON_WARNINGS

### Verificación de sprint
**Archivos revisados:** [lista]
- [✅/❌] Convenciones respetadas
- [✅/❌] Sin valores sensibles hardcodeados
- [✅/❌] Sin dependencias fuera del stack
- [✅/❌] Scope no invadido
- [✅/❌] [Criterio de aceptación N]

**Issues de sprint:** [descripción con archivo y línea]

### Verificación acumulativa
**Sprints revisados:** [lista]
- [✅/❌] Integración entre módulos correcta
- [✅/❌] Interfaces consistentes
- [✅/❌] Sin deuda técnica bloqueante
- [✅/❌] Sin desviaciones del plan

**Cuellos de botella detectados:** [lista con sprint afectado]
**Issues acumulativos:** [inconsistencias entre módulos]

**Decisiones del Generador documentadas:** [lista]
**Recomendación:** APROBAR | ITERAR
```

---

## 12. Autorización del Director

El Director puede autorizar o rechazar cada sprint desde **dos canales en paralelo**. El primero que responda desbloquea el sistema. No es necesario responder en ambos.

### Canal 1 — Telegram (remoto)

Ideal cuando el Director está fuera de la computadora o quiere aprobar desde el celular.

**Variables requeridas:**
```
TELEGRAM_BOT_TOKEN=   # Creado con @BotFather
TELEGRAM_CHAT_ID=     # ID del chat del Director
```

**Formato del mensaje por sprint:**
```
🏗️ *[PROYECTO] — Sprint [FASE]-[N] completado*

*Goal:* [goal del sprint]

*Verificación de sprint:* ✅ PASS | ⚠️ WARNINGS | ❌ FAIL
*Verificación acumulativa:* ✅ PASS | ⚠️ WARNINGS | ❌ FAIL

*Archivos generados/modificados:* [N]
*Sprints completados:* [N] de [Total]

*Resumen:*
[2-3 líneas de qué se construyó]

[Si hay warnings o cuellos de botella:]
⚠️ *Atención:* [descripción breve]

---
¿Autorizas continuar al Sprint [FASE]-[N+1]?
Puedes responder aquí en Telegram o directamente en Claude Code.
```

### Canal 2 — Claude Code directo (local)

Ideal cuando el Director está frente a la computadora. El Orquestador muestra el reporte del sprint en la terminal y espera input del Director antes de continuar.

**Formato del prompt en terminal:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [PROYECTO] — Sprint [FASE]-[N] completado
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Goal:                 [goal del sprint]
  Verificación sprint:  ✅ PASS | ⚠️ WARNINGS | ❌ FAIL
  Verificación acum.:   ✅ PASS | ⚠️ WARNINGS | ❌ FAIL
  Archivos modificados: [N]
  Sprints completados:  [N] de [Total]

  Resumen:
  [2-3 líneas de qué se construyó]

  [Si hay warnings:]
  ⚠️  [descripción breve]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ¿Autorizas continuar? (si / no + comentario):
```

El Orquestador espera el input del Director en la terminal. También se envía notificación por Telegram simultáneamente.

**Importante:** Telegram notifica en tiempo real cada punto de pausa — no solo
al final del sprint. Si el Director está fuera de su equipo, recibe la notificación
en el momento exacto en que el sistema necesita su respuesta, no horas después.

### Respuestas válidas — ambos canales

| Respuesta | Efecto |
|-----------|--------|
| `si` / `✅` / `autorizar` | Avanza al siguiente sprint |
| `no` / `❌` / `rechazar` | Orquestador solicita comentario, Generador itera |
| Cualquier texto libre | Se interpreta como rechazo con instrucción, Generador itera |

### Prioridad de canales

- El **primer canal que reciba respuesta** desbloquea el sistema
- Si el Director responde en Telegram, el Orquestador actualiza SDD_STATE.json y continúa
- Si el Director responde en Claude Code, el Orquestador envía confirmación a Telegram:
  `✅ Sprint [N] autorizado desde Claude Code. Iniciando Sprint [N+1].`
- Si hay contradicción entre canales (uno autoriza y el otro rechaza), **prevalece el rechazo**

---

## 13. Clasificación de autorizaciones

No toda acción requiere pausa y autorización del Director. El sistema distingue
dos categorías y actúa de forma diferente en cada una.

### 13.1 Decisiones rutinarias — ejecución automática

Son consecuencia natural del plan ya autorizado. El sistema las ejecuta sin
preguntar y las registra en el log.

```
EJEMPLOS:
□ Abrir terminal / PowerShell / bash
□ Crear carpetas definidas en la estructura de PROJECT.md
□ Instalar dependencias del stack ya aprobado en PROJECT.md
□ Ejecutar comandos estándar del framework (build, lint, test)
□ Crear archivos dentro del scope del sprint activo
□ Escribir variables de entorno definidas en PROJECT.md
□ Ejecutar migraciones de base de datos del sprint activo
□ Reiniciar el servidor de desarrollo
□ Hacer commit con el formato definido en PROJECT.md
```

**Regla:** si la acción está dentro del scope del sprint activo Y usa
tecnología ya aprobada en PROJECT.md → ejecutar sin preguntar.

### 13.2 Decisiones estratégicas — pausa y notificación inmediata

Requieren que el Director estudie las opciones y decida conscientemente.
El sistema se detiene, notifica a Telegram **en ese momento** y espera.
No continúa hasta recibir respuesta.

```
EJEMPLOS:
□ Elegir entre dos modelos de IA (Flux vs SDXL, GPT-4 vs Claude, etc.)
□ Adoptar una librería fuera del stack definido en PROJECT.md
□ Cambiar de proveedor de un servicio (Supabase → Firebase, etc.)
□ Modificar la arquitectura o estructura de carpetas del proyecto
□ Tomar una decisión que afecta más de un sprint futuro
□ Resolver una ambigüedad que PROJECT.md no cubre
□ Detectar que el enfoque planificado no es viable técnicamente
□ Cualquier acción irreversible fuera del scope del sprint
```

**Regla:** si la decisión afecta el plan, el stack, la arquitectura o
sprints futuros → pausa inmediata y notificación a Telegram.

### 13.3 Formato de notificación de decisión estratégica

```
🔀 *[PROYECTO] — Decisión requerida*

*Sprint activo:* [FASE]-[N]
*Punto de pausa:* [descripción de dónde está el sistema]

*Decisión necesaria:*
[Descripción clara del problema o elección]

*Opciones disponibles:*

A) [Opción A]
   ✅ [ventaja]
   ⚠️ [desventaja]
   💰 Costo estimado: [X €/mes o gratis]

B) [Opción B]
   ✅ [ventaja]
   ⚠️ [desventaja]
   💰 Costo estimado: [X €/mes o gratis]

*Recomendación:* [Opción X — justificación en una línea]

El sistema está pausado esperando tu respuesta.
Responde con la letra de tu elección o con instrucciones.
```

### 13.4 Qué hace el sistema mientras espera

Cuando hay una decisión estratégica pendiente:

```
→ El sistema NO continúa con el sprint activo
→ El sistema SÍ puede continuar con tareas que no dependan
  de esa decisión (si las hay en el scope del sprint)
→ Si no hay nada que pueda hacer sin la decisión:
  registra en el log "BLOQUEADO esperando decisión [descripción]"
  y notifica a Telegram cada 2 horas si no hay respuesta:
  "⏳ [PROYECTO] — Sigue esperando tu decisión sobre [tema]"
→ Cuando el Director responde, el sistema confirma recepción
  y continúa inmediatamente
```

---

## 14. Manejo de fallos

### Fallo en verificación de sprint

1. Verificador emite reporte FAIL con issues específicos
2. Generador recibe el reporte y corrige
3. Verificador revisa de nuevo (incluyendo acumulativa)
4. Máximo 3 iteraciones automáticas
5. Si en 3 intentos sigue en FAIL: Orquestador pausa y notifica al Director

### Fallo en verificación acumulativa

1. Verificador identifica el cuello de botella o inconsistencia
2. Orquestador determina qué sprint(s) anterior(es) están afectados
3. Notifica al Director con diagnóstico preciso antes de proponer corrección
4. Director autoriza el enfoque de corrección
5. Se corrige el módulo afectado antes de continuar

### Rechazo del Director

1. Director responde con comentario en Telegram
2. Orquestador pasa el comentario al Generador como instrucción
3. Generador itera → Verificador valida → Nueva notificación

### Ambigüedad o conflicto detectado por un agente

1. El agente detiene su ejecución inmediatamente
2. Reporta con precisión qué decisión se necesita y por qué
3. Orquestador notifica al Director por Telegram
4. Director responde → agente continúa
5. El agente nunca resuelve un conflicto con PROJECT.md por su cuenta

---

## 15. Protocolo de rollback

### Clasificación del problema

```
TIPO A — Corrección local:
El problema está contenido en un módulo y no afecta interfaces con otros.
→ Se crea un sprint de corrección sobre el módulo afectado.
→ No se revierten sprints anteriores.

TIPO B — Conflicto de integración:
El problema afecta la interfaz entre dos o más módulos ya construidos.
→ Se identifican todos los sprints afectados.
→ Se notifica al Director con diagnóstico antes de actuar.
→ El Director autoriza el enfoque: corrección puntual o reversión de sprint.

TIPO C — Fallo estructural:
El problema invalida decisiones de arquitectura ya ejecutadas.
→ El sistema se detiene completamente.
→ Se notifica al Director con reporte detallado.
→ No se propone solución automática. El Director decide el camino.
```

### Sprint de corrección

```markdown
## Sprint [FASE]-[N]C: Corrección — [Módulo afectado]

**Tipo:** Corrección (no es sprint de feature)
**Problema:** [descripción del issue]
**Sprint(s) afectado(s):** [lista]
**Agente:** [agente del módulo afectado]

### Scope de corrección
- [ ] [Qué se corrige específicamente]

### Criterios de aceptación
- [ ] El issue original ya no existe
- [ ] La verificación acumulativa pasa sin warnings en este punto
```

### Notificación Telegram de rollback

```
🔴 *[PROYECTO] — Problema detectado en verificación acumulativa*

*Tipo:* A — Corrección local | B — Conflicto de integración | C — Fallo estructural
*Sprint(s) afectado(s):* [lista]
*Descripción:* [diagnóstico preciso]

[Tipo A / B:]
*Propuesta:* Sprint de corrección [ID]C sobre [módulo]
¿Autorizas este enfoque?

[Tipo C:]
*El sistema está detenido. Se requiere tu instrucción para continuar.*
```

---

## 16. Reanudación entre sesiones

Claude Code no tiene memoria entre sesiones. Cada vez que se inicia una sesión nueva — por cualquier motivo, incluyendo agotamiento de tokens — el Orquestador ejecuta este protocolo completo antes de cualquier otra acción.

### 15.1 Protocolo de inicio de sesión

```
PASO 1 — ANCLAJE (obligatorio, sin excepción)
  → Leer SDD_SYSTEM.md completo
  → Leer PROJECT.md completo
  → Sin estos dos documentos el sistema no puede continuar
    Notificar al Director y esperar que los proporcione

PASO 2 — ESTADO
  → Leer SDD_STATE.json
  → Si no existe: es arranque nuevo, ir al flujo de entrevista (sección 3)
  → Si existe: continuar al PASO 3

PASO 3 — LOG
  → Leer SDD_LOG.json completo
  → Reconstruir el estado real del proyecto desde las entradas del log
  → El log es la fuente de verdad del progreso — tiene prioridad
    sobre SDD_STATE.json si hay contradicción

PASO 4 — DIAGNÓSTICO
  Determinar el estado actual combinando STATE + LOG:

  ESTADO A: pendiente_autorizacion = true
  → El Director no ha respondido al último sprint
  → Reenviar notificación:
    "⏳ Sesión reanudada. Sprint [N] completado y verificado.
     Sigue pendiente tu autorización para continuar."
  → Esperar respuesta

  ESTADO B: sprint_estado = "en_curso" con entradas de log incompletas
  → La sesión anterior se cortó a mitad del sprint (tokens agotados u otro motivo)
  → Reconstruir desde el log qué se completó y qué no
  → Notificar al Director con diagnóstico preciso:
    "⚠️ La sesión anterior se cortó durante el Sprint [N].

     Estado reconstruido desde el log:
     ✅ [archivo/función] — completado
     🔄 [archivo/función] — iniciado, no completado
     ⏳ [archivo/función] — pendiente

     Criterios completados: [N] de [Total]
     Último punto registrado: [descripción exacta del log]

     ¿Continúo desde el último punto o reinicio el sprint completo?"
  → Esperar instrucción del Director antes de continuar

  ESTADO C: sprint_estado = "esperando_autorizacion"
  → Igual que ESTADO A

  ESTADO D: todos los sprints completados y autorizados
  → Notificar al Director:
    "✅ Sesión reanudada. Próximo sprint: [FASE]-[N] — [Goal]
     ¿Autoriza iniciar?"
  → Esperar autorización

PASO 5 — CONTINUAR
  → Solo después del diagnóstico y con instrucción del Director
  → Si es sprint nuevo: ejecutar anclaje de sprint (sección 7)
  → Si es continuación: retomar desde el último punto confirmado en el log
```

### 15.2 Sistema de log incremental — SDD_LOG.json

El log es la memoria persistente del sistema. Se escribe de forma incremental — cada acción genera su entrada **antes y después** de ejecutarse, no al final del sprint. Esto garantiza que un corte por agotamiento de tokens quede registrado por omisión.

**Regla de escritura:**
```
Antes de cada acción  → LOG: "INICIO: [descripción]"
Después de completarla → LOG: "FIN: [descripción]"

Si solo existe el INICIO sin el FIN correspondiente
→ esa acción quedó incompleta cuando se cortó la sesión
```

**Formato de cada entrada:**
```json
{
  "timestamp": "[ISO timestamp]",
  "sesion": "[ID de sesión incremental]",
  "sprint": "[FASE]-[N]",
  "tipo": "INICIO | FIN | DECISION | ERROR | AUTORIZACION",
  "accion": "[descripción de la acción]",
  "detalle": "[archivo, función, criterio o decisión afectada]"
}
```

**Ejemplo de log con corte por tokens:**
```json
[
  {"timestamp":"...","sesion":"3","sprint":"1-3","tipo":"INICIO","accion":"Crear archivo","detalle":"src/lib/dxf/parser.ts"},
  {"timestamp":"...","sesion":"3","sprint":"1-3","tipo":"FIN","accion":"Crear archivo","detalle":"src/lib/dxf/parser.ts"},
  {"timestamp":"...","sesion":"3","sprint":"1-3","tipo":"INICIO","accion":"Escribir función","detalle":"parseWalls en parser.ts"},
  {"timestamp":"...","sesion":"3","sprint":"1-3","tipo":"FIN","accion":"Escribir función","detalle":"parseWalls en parser.ts"},
  {"timestamp":"...","sesion":"3","sprint":"1-3","tipo":"INICIO","accion":"Escribir función","detalle":"parseOpenings en parser.ts"}
  ← sesión cortada aquí. No existe el FIN de parseOpenings.
]
```

La nueva sesión lee el log, detecta que `parseOpenings` tiene INICIO pero no FIN, y sabe exactamente dónde retomar.

**Qué se loguea:**
```
□ INICIO y FIN de cada archivo creado o modificado
□ INICIO y FIN de cada función o componente escrito
□ Cada decisión técnica tomada por el Generador (tipo DECISION)
□ Cada resultado de verificación (tipo FIN con resultado PASS/FAIL)
□ Cada autorización del Director (tipo AUTORIZACION)
□ Cada error detectado (tipo ERROR)
```

**Dónde vive:**
```
sdd/
├── SDD_STATE.json    ← estado actual del proyecto
└── SDD_LOG.json      ← historial completo de acciones
```

Ambos archivos van en `.gitignore`. Son archivos operativos del sistema, no del proyecto.

### SDD_STATE.json

```json
{
  "sdd_version": "13.0",
  "proyecto": "[NOMBRE]",
  "agentes_derivados": [],
  "sprints_totales": 0,
  "sprint_activo": null,
  "sprint_estado": "pendiente | en_curso | verificacion | esperando_autorizacion | completado",
  "sesion_actual": 0,
  "sprints_completados": [],
  "decisiones_pendientes": [],
  "ultimo_autorizado_por": null,
  "ultima_autorizacion": null,
  "iteraciones_sprint_activo": 0,
  "pendiente_autorizacion": false,
  "cuellos_de_botella_activos": [],
  "costo_estimado_total": 0,
  "costo_acumulado": 0,
  "ultima_actualizacion": "[ISO timestamp]"
}
```

---

## 17. Log de cambios al PROJECT.md

Durante el desarrollo, las decisiones autorizadas por el Director pueden modificar el plan original. El Orquestador mantiene PROJECT.md siempre actualizado.

### Cuándo se actualiza

- El Director autoriza una decisión técnica no contemplada en el plan original
- El Director rechaza un enfoque y aprueba uno alternativo
- Un agente detecta que una decisión del plan no es viable y el Director aprueba el cambio
- Se completa una fase y se confirman decisiones que antes eran tentativas

### Protocolo de actualización

```
1. Orquestador detecta que una decisión modifica el plan
2. Notifica al Director:
   "📝 La decisión tomada en Sprint [N] modifica el plan original:
    [descripción del cambio]
    ¿Confirmas que actualice PROJECT.md?"
3. Director confirma
4. Orquestador actualiza PROJECT.md y agrega entrada al log
```

### Formato del log en PROJECT.md

```markdown
## Cambios al plan

| Fecha | Sprint | Cambio | Motivo | Autorizado por |
|-------|--------|--------|--------|----------------|
| [fecha] | [sprint ID] | [qué cambió] | [por qué] | Director |
```

**Regla de integridad:** PROJECT.md siempre refleja el estado actual del plan. El log es el registro histórico. Todo agente que lea PROJECT.md está leyendo la versión vigente y autorizada.

---

## 18. Estimación de costos operativos

El Orquestador registra y reporta el costo estimado de servicios de pago en cada sprint
cuando el proyecto usa al menos un servicio con costo por uso.

### Qué se rastrea

```
Servicios rastreables típicos:
- Replicate (inferencia IA) — costo por predicción
- OpenAI / Anthropic API — costo por tokens
- Stripe / MercadoPago — comisión por transacción
- Twilio — costo por SMS / WhatsApp
- SendGrid / Resend — costo por email sobre free tier
- Mapbox / Google Maps — costo por request sobre free tier
- AWS / GCP / Azure — costo por uso de recursos
```

### Cómo el Orquestador estima el costo

```
1. Al arrancar, el Orquestador identifica los servicios de pago del proyecto
   desde PROJECT.md y sus tarifas aproximadas

2. Al terminar cada sprint, estima el consumo generado:
   - Llamadas a APIs externas realizadas durante el sprint
   - Inferencias de IA ejecutadas en pruebas
   - Recursos de nube aprovisionados

3. Registra en SDD_STATE.json:
   - costo_estimado_total: proyección del proyecto completo
   - costo_acumulado: suma de sprints completados

4. Incluye el resumen en la notificación Telegram y en el prompt de Claude Code
```

### Alertas de costo

Si el costo acumulado supera el 80% del presupuesto estimado antes de terminar
todos los sprints, el Orquestador notifica al Director con alerta especial:

```
⚠️ *[PROYECTO] — Alerta de presupuesto*

El costo acumulado (~[X] €) ha superado el 80% del estimado total (~[X] €.
Quedan [N] sprints por ejecutar.

Opciones:
a) Continuar con el plan actual
b) Revisar sprints restantes para reducir llamadas a servicios externos
c) Ajustar el presupuesto estimado

¿Cómo prefieres proceder?
```

### Nota importante

Las estimaciones son aproximadas. El Orquestador no tiene acceso en tiempo real
a los dashboards de facturación de los servicios. Para costos exactos, consultar
el panel de cada servicio directamente.

---

## 19. Biblioteca de skills reutilizables

Cada proyecto genera conocimiento que puede aprovecharse en proyectos futuros.
El Orquestador mantiene una biblioteca de skills — patrones, soluciones y
configuraciones probadas — que se acumulan entre proyectos.

### 19.1 Qué es una skill

Una skill es un agente o patrón reutilizable que resolvió un problema específico
en un proyecto y puede aplicarse en proyectos futuros sin rediseñarlo desde cero.

```markdown
## Skill: [NOMBRE]

**Problema que resuelve:** [descripción]
**Proyecto origen:** [nombre del proyecto donde se creó]
**Sprint origen:** [ID del sprint]
**Stack compatible:** [tecnologías donde funciona]

### Implementación
[Descripción de cómo funciona y cómo se invoca]

### Criterios de aplicación
[Cuándo usar esta skill y cuándo no]

### Resultado esperado
[Qué produce cuando se aplica correctamente]
```

### 19.2 Cuándo se crea una skill

```
Al terminar un sprint, el Orquestador evalúa:
□ ¿Este agente o patrón resolvió algo no trivial?
□ ¿Podría aplicarse en otros proyectos del mismo stack?
□ ¿Ahorraría tiempo si estuviera documentado?

Si las tres respuestas son sí: crear skill y agregarla a la biblioteca.
```

### 19.3 Cómo se genera una skill nueva

El Director puede solicitar la creación de una skill en lenguaje natural:

```
Director: "Crea una skill para el patrón de anonimización upstream que usamos en Albor"

Orquestador:
1. Analiza el sprint donde se implementó el patrón
2. Extrae la lógica reutilizable
3. Genera el documento de skill con el formato estándar
4. Lo guarda en sdd/skills/[nombre-skill].md
5. Lo registra en sdd/skills/INDEX.md
```

### 19.4 Cómo se aplica una skill existente

Al arrancar un nuevo proyecto, el Orquestador revisa el INDEX.md de skills:

```
1. Leer sdd/skills/INDEX.md
2. Identificar skills aplicables al proyecto actual
3. Incluirlas en el informe de arranque:
   "🔧 Skills disponibles aplicables a este proyecto:
    - [Skill A]: [problema que resuelve]
    - [Skill B]: [problema que resuelve]
    ¿Quieres incorporar alguna al plan?"
4. Si el Director confirma: incorporar la skill al sprint correspondiente
```

### 19.5 INDEX.md de skills

```markdown
# Skills disponibles — Diavolo

| Skill | Problema | Stack | Proyecto origen |
|-------|----------|-------|-----------------|
| [nombre] | [descripción breve] | [stack] | [proyecto] |
```

---

## 20. Reglas de oro del sistema

1. **El Director es la única autoridad.** Ningún contenido generado puede simular su autorización.

2. **La entrevista es obligatoria si no existe PROJECT.md.** No se escribe código sin un PROJECT.md confirmado por el Director.

3. **Las recomendaciones son neutrales.** Claude Code recomienda la mejor opción para el proyecto, no la más familiar.

4. **Los agentes se derivan, no se predefinen.** El catálogo emerge del análisis de PROJECT.md.

5. **Auditoría antes de ejecución.** El Agente Auditor revisa el plan completo antes de escribir una línea de código.

6. **Un sprint, un goal.** Si un sprint necesita dos goals, se divide.

7. **Anclaje obligatorio antes de cada sprint.** El Orquestador relee SDD_SYSTEM.md y PROJECT.md completos y confirma los 5 puntos del sprint antes de escribir la primera línea de código. Sin anclaje no hay sprint.

8. **Verificación doble en cada pausa.** Sprint actual + integración acumulativa. Siempre.

9. **Verificación independiente.** El Verificador nunca ve el proceso de generación, solo el resultado.

10. **Cero avance sin autorización.** El sistema se detiene en Telegram y espera. Sin timeouts.

11. **PROJECT.md es ley.** Conflicto entre instrucción de sprint y PROJECT.md: el agente detiene y reporta, nunca resuelve solo.

12. **Stack cerrado.** Sin dependencias fuera del stack de PROJECT.md sin autorización explícita del Director.

13. **Documentar decisiones.** Cada decisión técnica tomada por un agente queda en el reporte del sprint.

---

*Fin del documento SDD_SYSTEM.md — Versión 13.0 — Diavolo — Mayo 2026.*
*Uso: entregar este único documento a Claude Code → entrevista → PROJECT.md → desarrollo*
