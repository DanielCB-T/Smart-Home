"""Configuración leída del entorno. Se consulta en cada uso para que las pruebas puedan cambiarla."""

import os
from pathlib import Path

RAIZ_BACKEND = Path(__file__).resolve().parents[1]
CARPETA_DB = RAIZ_BACKEND / "db"


def ruta_base_datos() -> Path:
    valor = os.environ.get("SMART_HOME_DB")
    return Path(valor).resolve() if valor else (RAIZ_BACKEND / "data" / "smarthome.sqlite").resolve()


def origenes_cors() -> list[str]:
    valor = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origen.strip() for origen in valor.split(",") if origen.strip()]
