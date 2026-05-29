from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.clients import router as clients_router
from routers.campaigns import router as campaigns_router
from routers.assets import router as assets_router
from routers.posts import router as posts_router
from routers.messages import router as messages_router
from routers.auto_replies import router as auto_replies_router
from routers.metrics import router as metrics_router
from routers.webhooks import router as webhooks_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — iniciar scheduler de publicación
    from database import engine
    from services.scheduler import start_scheduler
    start_scheduler(engine)
    yield
    # Shutdown
    from services.scheduler import scheduler
    if scheduler.running:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title="Diavolo Instagram Manager API",
    version="0.1.0",
    lifespan=lifespan,
)

import os as _os

_CORS_ORIGINS = [o.strip() for o in _os.environ.get(
    "CORS_ORIGINS", "http://localhost:3000"
).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(clients_router)
app.include_router(campaigns_router)
app.include_router(assets_router)
app.include_router(posts_router)
app.include_router(messages_router)
app.include_router(auto_replies_router)
app.include_router(metrics_router)
app.include_router(webhooks_router)


@app.get("/health")
def health():
    return {"status": "ok", "proyecto": "Diavolo Instagram Manager"}
