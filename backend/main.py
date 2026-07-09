# -*- coding: utf-8 -*-
"""FastAPI 应用入口 — 路由注册、CORS、启动建表"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine, Base
from models.user import User  # noqa: F401
from models.trip import Trip  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用启动时自动建表"""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="LightJourney API",
    description="AI 驱动的旅行行程管理系统",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS 中间件 ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── 路由注册 ────────────────────────────────────────────
from routers.auth import router as auth_router
from routers.trips import router as trips_router
from routers.ai import router as ai_router

app.include_router(auth_router, prefix="/api/auth", tags=["鉴权"])
app.include_router(trips_router, tags=["行程"])
app.include_router(ai_router, tags=["AI"])


# ─── 健康检查 ────────────────────────────────────────────
@app.get("/")
def health_check():
    return {"status": "ok", "version": "1.0.0"}
