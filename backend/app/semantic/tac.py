"""Convierte el IR en código de tres direcciones legible.

Ejemplo:
    t1 = temperatura
    t2 = t1 > 30
    if_false t2 goto L1
    ventilador1 = ENCENDIDO
    L1:
"""

from __future__ import annotations

from typing import Any


def _operando(valor: Any) -> str:
    if isinstance(valor, dict):
        if "temp" in valor:
            return str(valor["temp"])
        if "valor" in valor:
            return _literal(valor["valor"])
    return _literal(valor)


def _literal(valor: Any) -> str:
    if isinstance(valor, str):
        return f'"{valor}"' if " " in valor or valor == "" else valor
    return str(valor)


def _linea(instruccion: dict[str, Any]) -> str | None:
    op = instruccion["op"]
    if op == "SET_STATE":
        return f'{instruccion["dispositivo"]} = {_literal(instruccion["valor"])}'
    if op == "GET_STATE":
        return f'{instruccion["destino"]} = {instruccion["dispositivo"]}'
    if op == "COMPARE":
        return (
            f'{instruccion["destino"]} = {_operando(instruccion["izquierda"])} '
            f'{instruccion["operador"]} {_operando(instruccion["derecha"])}'
        )
    if op == "JUMP_IF_FALSE":
        return f'if_false {instruccion["condicion"]} goto {instruccion["salto_a"]}'
    if op == "NOTIFY":
        return f'notify "{instruccion["mensaje"]}"'
    if op == "SEND_EMAIL":
        return f'send_email "{instruccion["destinatario"]}", "{instruccion["mensaje"]}"'
    if op == "LIST_DEVICES":
        return "list_devices"
    if op == "HALT":
        return None  # El fin del programa no se muestra; solo su etiqueta, si la tiene.
    return f"{op.lower()} {instruccion}"


def formatear_tac(ir: dict[str, Any]) -> list[str]:
    lineas: list[str] = []
    for instruccion in ir.get("instrucciones", []):
        etiqueta = instruccion.get("etiqueta")
        if etiqueta:
            lineas.append(f"{etiqueta}:")
        linea = _linea(instruccion)
        if linea is not None:
            lineas.append(linea)
    return lineas
