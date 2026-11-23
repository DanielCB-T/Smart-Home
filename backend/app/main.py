"""Punto de entrada de la API de SmartHome.

Ejecutar en desarrollo:  uvicorn app.main:app --reload --port 3001
Documentación interactiva: http://localhost:3001/docs
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router
from app.config import origenes_cors
from app.db import inicializar


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI):
    inicializar()
    yield


app = FastAPI(
    title="SmartHome API",
    version=__version__,
    description=(
        "Interpreta instrucciones escritas (léxico, sintáctico, semántico), "
        "las ejecuta sobre dispositivos simulados y guarda el historial."
    ),
    lifespan=ciclo_de_vida,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes_cors(),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
