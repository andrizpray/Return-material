from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import os, secrets

from app.config import get_settings
from app.database import engine, Base, SessionLocal
from app.models import User, hash_password

settings = get_settings()


def seed_admin():
    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
            )
            db.add(admin)
            db.commit()
            print("[AUTH] Default admin created — admin / admin123")
    finally:
        db.close()


async def auth_guard(request: Request, call_next):
    path = request.url.path
    if path.startswith("/static") or path.startswith("/uploads"):
        return await call_next(request)
    if path in ("/login", "/logout"):
        return await call_next(request)
    if not request.session.get("user_id"):
        return RedirectResponse("/login", status_code=303)
    return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    seed_admin()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# SessionMiddleware MUST be outermost (added last)
app.add_middleware(BaseHTTPMiddleware, dispatch=auth_guard)
app.add_middleware(SessionMiddleware, secret_key=secrets.token_hex(32))

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Auth routes
from app.routes import auth  # noqa: E402
app.include_router(auth.router)

# Protected routes
from app.routes import dashboard, returns, reports, export, berita_acara  # noqa: E402

app.include_router(dashboard.router)
app.include_router(returns.router, prefix="/returns", tags=["returns"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(export.router, prefix="/export", tags=["export"])
app.include_router(berita_acara.router, prefix="/berita-acara", tags=["berita_acara"])
