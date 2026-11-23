"""Ejecuta las instrucciones semánticas sobre la base de datos.

Solo ejecuta SET_STATE (control de dispositivos) y CONDITIONAL. Las demás
instrucciones se analizan completamente, pero su ejecución queda pendiente
(tarjetas S2-09, S2-10 y S2-18).
"""

from __future__ import annotations

import sqlite3
from typing import Optional

from app.db import ESTADOS
from app.language.ast_nodes import Estado, Numero
from app.semantic import InstruccionSemantica

ACTIVOS = {"ENCENDIDO", "ACTIVADA", "ABIERTA"}
OPERADORES = {
    ">": lambda a, b: a > b,
    "<": lambda a, b: a < b,
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


class ErrorEjecucion(Exception):
    """Una instrucción válida que no puede ejecutarse en el estado actual."""


def _fila_dispositivo(conexion: sqlite3.Connection, nombre: str) -> sqlite3.Row:
    fila = conexion.execute(
        "SELECT id, name, type, enabled FROM devices WHERE lower(id) = lower(?)", (nombre,)
    ).fetchone()
    if fila is None:
        raise ErrorEjecucion(f'El dispositivo "{nombre}" no existe.')
    return fila


def _estado_actual(fila: sqlite3.Row) -> str:
    activo, inactivo = ESTADOS[fila["type"]]
    return activo if fila["enabled"] else inactivo


def _set_state(conexion: sqlite3.Connection, instruccion: InstruccionSemantica) -> str:
    fila = _fila_dispositivo(conexion, instruccion.dispositivo)
    destino_activo = instruccion.valor in ACTIVOS
    if bool(fila["enabled"]) == destino_activo:
        raise ErrorEjecucion(f'El dispositivo "{fila["id"]}" ya está {_estado_actual(fila)}.')
    conexion.execute("UPDATE devices SET enabled = ? WHERE id = ?", (int(destino_activo), fila["id"]))
    return f'{fila["name"]} cambió a {instruccion.valor}.'


def _evaluar_condicion(conexion: sqlite3.Connection, instruccion: InstruccionSemantica) -> bool:
    condicion = instruccion.condicion
    operador = OPERADORES[condicion.operador]

    if condicion.izquierda.lower() == "temperatura":
        if not isinstance(condicion.derecha, Numero):
            raise ErrorEjecucion("La temperatura solo se compara con un número.")
        fila = conexion.execute("SELECT value FROM settings WHERE key = 'temperature'").fetchone()
        temperatura = float(fila["value"]) if fila else 28.0
        return operador(temperatura, condicion.derecha.valor)

    fila = _fila_dispositivo(conexion, condicion.izquierda)
    if not isinstance(condicion.derecha, Estado):
        raise ErrorEjecucion(f'"{fila["id"]}" solo se compara con un estado.')
    return operador(_estado_actual(fila), condicion.derecha.valor)


def ejecutar(conexion: sqlite3.Connection, instruccion: InstruccionSemantica) -> tuple[str, bool]:
    """Ejecuta una instrucción. Devuelve (mensaje, omitida)."""
    if instruccion.tipo_accion == "SET_STATE":
        return _set_state(conexion, instruccion), False

    if instruccion.tipo_accion == "CONDITIONAL":
        if not _evaluar_condicion(conexion, instruccion):
            return "Condición falsa. No se ejecutó ninguna acción.", True
        mensaje, _ = ejecutar(conexion, instruccion.accion_condicional)
        return f"Condición verdadera. {mensaje}", False

    raise ErrorEjecucion(
        "La sintaxis es válida, pero esta instrucción aún no tiene ejecución implementada."
    )


def ejecutar_todas(
    conexion: sqlite3.Connection, instrucciones: list[InstruccionSemantica]
) -> tuple[Optional[str], bool]:
    """Ejecuta en orden. Se detiene en el primer error. Devuelve (mensaje, omitida)."""
    mensajes: list[str] = []
    omitida = True
    for instruccion in instrucciones:
        mensaje, omitida_actual = ejecutar(conexion, instruccion)
        mensajes.append(mensaje)
        omitida = omitida and omitida_actual
    return " ".join(mensajes), omitida
