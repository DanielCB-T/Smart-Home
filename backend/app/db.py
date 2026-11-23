"""Acceso a SQLite: conexión, migraciones, semillas y consultas de estado e historial."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from .config import CARPETA_DB, ruta_base_datos

CARPETA_MIGRACIONES = CARPETA_DB / "migrations"
CARPETA_SEMILLAS = CARPETA_DB / "seeders"

# Estado legible de cada tipo: (valor cuando está activo, valor cuando está inactivo).
ESTADOS = {
    "luz": ("ENCENDIDO", "APAGADO"),
    "ventilador": ("ENCENDIDO", "APAGADO"),
    "puerta": ("ABIERTA", "CERRADA"),
    "alarma": ("ACTIVADA", "DESACTIVADA"),
}


def ahora() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def abrir(ruta: Optional[Path] = None) -> Iterator[sqlite3.Connection]:
    ruta = Path(ruta) if ruta else ruta_base_datos()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta, timeout=5)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


def inicializar(ruta: Optional[Path] = None) -> None:
    """Aplica las migraciones pendientes y después las semillas (idempotentes)."""
    with abrir(ruta) as conexion:
        conexion.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        aplicadas = {fila["name"] for fila in conexion.execute("SELECT name FROM schema_migrations")}
        for archivo in sorted(CARPETA_MIGRACIONES.glob("*.sql")):
            if archivo.name in aplicadas:
                continue
            conexion.executescript(archivo.read_text(encoding="utf-8"))
            conexion.execute(
                "INSERT INTO schema_migrations(name, applied_at) VALUES (?, ?)",
                (archivo.name, ahora()),
            )
        for archivo in sorted(CARPETA_SEMILLAS.glob("*.sql")):
            conexion.executescript(archivo.read_text(encoding="utf-8"))


def _dispositivo(fila: sqlite3.Row) -> dict:
    activo = bool(fila["enabled"])
    valor_activo, valor_inactivo = ESTADOS[fila["type"]]
    base = {
        "id": fila["id"],
        "name": fila["name"],
        "type": fila["type"],
        "estado": valor_activo if activo else valor_inactivo,
    }
    if fila["type"] == "puerta":
        base["open"] = activo
    else:
        base["on"] = activo
    return base


def _registro(fila: sqlite3.Row) -> dict:
    return {
        "id": fila["id"],
        "timestamp": fila["timestamp"],
        "command": fila["command"],
        "message": fila["message"],
        "success": bool(fila["success"]),
        "skipped": bool(fila["skipped"]),
    }


def leer_dispositivos(conexion: sqlite3.Connection) -> list[dict]:
    filas = conexion.execute("SELECT id, name, type, enabled FROM devices ORDER BY rowid").fetchall()
    return [_dispositivo(fila) for fila in filas]


def leer_temperatura(conexion: sqlite3.Connection) -> float:
    fila = conexion.execute("SELECT value FROM settings WHERE key = 'temperature'").fetchone()
    return float(fila["value"]) if fila else 28.0


def leer_historial(conexion: sqlite3.Connection, limite: int = 100) -> list[dict]:
    filas = conexion.execute(
        "SELECT * FROM history ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()
    return [_registro(fila) for fila in filas]


def registrar(conexion: sqlite3.Connection, comando: str, mensaje: str, exito: bool, omitida: bool = False) -> dict:
    marca = ahora()
    cursor = conexion.execute(
        "INSERT INTO history(timestamp, command, message, success, skipped) VALUES (?, ?, ?, ?, ?)",
        (marca, comando, mensaje, int(exito), int(omitida)),
    )
    return {
        "id": cursor.lastrowid,
        "timestamp": marca,
        "command": comando,
        "message": mensaje,
        "success": exito,
        "skipped": omitida,
    }


def estado_completo(ruta: Optional[Path] = None) -> dict:
    with abrir(ruta) as conexion:
        return {
            "devices": leer_dispositivos(conexion),
            "temperature": leer_temperatura(conexion),
            "history": leer_historial(conexion),
        }
