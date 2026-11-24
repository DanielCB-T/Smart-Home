"""Genera contratos/openapi.yaml a partir de la aplicación FastAPI.

Uso (desde la carpeta backend):  python scripts/exportar_openapi.py
"""

from pathlib import Path

import yaml

from app.main import app

DESTINO = Path(__file__).resolve().parents[2] / "contratos" / "openapi.yaml"


def generar() -> dict:
    return app.openapi()


if __name__ == "__main__":
    DESTINO.write_text(
        yaml.safe_dump(generar(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Contrato escrito en {DESTINO}")
