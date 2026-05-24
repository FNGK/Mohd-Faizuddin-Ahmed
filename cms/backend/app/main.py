from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import REPO_ROOT, get_settings
from app.routers import auth, contact, content, dashboard, i18n, media, publish, roles, users, webhooks
from app.routers import settings as settings_router
from app.seed import run_seed

ADMIN_DIR = REPO_ROOT / "cms" / "admin"
CMS_UPLOADS_MOUNT = True


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_seed()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SEO With Faiz CMS",
        version="1.0.0",
        docs_url="/api/docs" if not settings.is_production else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    prefix = "/api/v1"
    app.include_router(auth.router, prefix=prefix)
    app.include_router(users.router, prefix=prefix)
    app.include_router(content.router, prefix=prefix)
    app.include_router(media.router, prefix=prefix)
    app.include_router(contact.router, prefix=prefix)
    app.include_router(dashboard.router, prefix=prefix)
    app.include_router(settings_router.router, prefix=prefix)
    app.include_router(publish.router, prefix=prefix)
    app.include_router(webhooks.router, prefix=prefix)
    app.include_router(i18n.router, prefix=prefix)
    app.include_router(roles.router, prefix=prefix)

    def _health_payload():
        return {"status": "ok", "cms": True}

    @app.get("/api/health")
    def health():
        return _health_payload()

    @app.get("/api/v1/health")
    def health_v1():
        return _health_payload()

    if ADMIN_DIR.is_dir():
        app.mount(
            "/admin",
            StaticFiles(directory=str(ADMIN_DIR), html=True),
            name="admin",
        )

    app.mount("/", StaticFiles(directory=str(REPO_ROOT), html=True), name="site")
    return app


app = create_app()
