"""Alta, edición y baja de dispositivos en la tabla de símbolos."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Optional

from app.db import abrir, estado_completo, registrar
from app.language.tokens import PALABRAS_RESERVADAS

TIPOS_VALIDOS = ("luz", "ventilador", "puerta", "alarma")
PATRON_IDENTIFICADOR = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,39}$")
IDENTIFICADORES_BLOQUEADOS = {"TEMPERATURA"}  # nombre reservado del sensor simulado


class ErrorDispositivo(Exception):
    def __init__(self, codigo: int, mensaje: str):
        super().__init__(mensaje)
        self.codigo = codigo
        self.mensaje = mensaje


def _validar(identificador: str, nombre: str, tipo: str) -> None:
    if not PATRON_IDENTIFICADOR.match(identificador):
        raise ErrorDispositivo(422, "El identificador debe empezar con letra o guion bajo y usar solo letras, números o guion bajo (máximo 40 caracteres).")
    clave = identificador.upper()
    if clave in PALABRAS_RESERVADAS or clave in IDENTIFICADORES_BLOQUEADOS:
        raise ErrorDispositivo(422, f'"{identificador}" es una palabra reservada del lenguaje y no puede usarse como identificador.')
    if not nombre.strip():
        raise ErrorDispositivo(422, "El nombre no puede estar vacío.")
    if tipo not in TIPOS_VALIDOS:
        raise ErrorDispositivo(422, f"Tipo no válido. Usa uno de: {', '.join(TIPOS_VALIDOS)}.")


def _existe_otro(conexion: sqlite3.Connection, identificador: str, excepto: Optional[str] = None) -> bool:
    if excepto is None:
        fila = conexion.execute("SELECT 1 FROM devices WHERE lower(id) = lower(?)", (identificador,)).fetchone()
    else:
        fila = conexion.execute(
            "SELECT 1 FROM devices WHERE lower(id) = lower(?) AND id != ?", (identificador, excepto)
        ).fetchone()
    return fila is not None


def _buscar(conexion: sqlite3.Connection, identificador: str) -> sqlite3.Row:
    fila = conexion.execute(
        "SELECT id, name, type, enabled FROM devices WHERE lower(id) = lower(?)", (identificador,)
    ).fetchone()
    if fila is None:
        raise ErrorDispositivo(404, f'El dispositivo "{identificador}" no existe.')
    return fila


def crear(identificador: str, nombre: str, tipo: str, ruta: Optional[Path] = None) -> dict:
    _validar(identificador, nombre, tipo)
    nombre = nombre.strip()
    with abrir(ruta) as conexion:
        if _existe_otro(conexion, identificador):
            raise ErrorDispositivo(409, f'Ya existe un dispositivo con el identificador "{identificador}".')
        conexion.execute(
            "INSERT INTO devices(id, name, type, enabled) VALUES (?, ?, ?, 0)",
            (identificador, nombre, tipo),
        )
        registrar(conexion, f"SYM_DECL {identificador}", f'Dispositivo "{nombre}" registrado como {tipo}.', True)
    return estado_completo(ruta)


def actualizar(actual: str, identificador: str, nombre: str, tipo: str, ruta: Optional[Path] = None) -> dict:
    _validar(identificador, nombre, tipo)
    nombre = nombre.strip()
    with abrir(ruta) as conexion:
        fila = _buscar(conexion, actual)
        if _existe_otro(conexion, identificador, excepto=fila["id"]):
            raise ErrorDispositivo(409, f'Ya existe un dispositivo con el identificador "{identificador}".')
        conexion.execute(
            "UPDATE devices SET id = ?, name = ?, type = ? WHERE id = ?",
            (identificador, nombre, tipo, fila["id"]),
        )
        cambio = f'"{fila["id"]}" → "{identificador}"' if fila["id"] != identificador else f'"{identificador}"'
        registrar(conexion, f"SYM_UPDATE {identificador}", f"Dispositivo {cambio} actualizado.", True)
    return estado_completo(ruta)


def eliminar(identificador: str, ruta: Optional[Path] = None) -> dict:
    with abrir(ruta) as conexion:
        fila = _buscar(conexion, identificador)
        conexion.execute("DELETE FROM devices WHERE id = ?", (fila["id"],))
        registrar(conexion, f"SYM_DELETE {fila['id']}", f'Dispositivo "{fila["name"]}" eliminado.', True)
    return estado_completo(ruta)
