"""Esqueleto de la máquina virtual (tarjeta S1-18).

La VM recibe instrucciones del IR (ver contratos/ir.md) y las ejecuta en seis pasos:

    1. Identificar la operación.
    2. Obtener el dispositivo.
    3. Validar el estado solicitado.
    4. Actualizar el estado del dispositivo.
    5. Guardar el resultado.
    6. Notificar a la interfaz.

En S1-18 solo se implementa el paso 1 y la validación de operaciones del IR.
Los pasos 2 a 6 quedan definidos y lanzan NotImplementedError hasta S2-17.
"""

from __future__ import annotations

from typing import Any

PASOS: tuple[str, ...] = (
    "identificar_operacion",
    "obtener_dispositivo",
    "validar_estado",
    "actualizar_estado",
    "guardar_resultado",
    "notificar_interfaz",
)

OPERACIONES_IR: frozenset[str] = frozenset({
    "SET_STATE", "GET_STATE", "COMPARE", "JUMP_IF_FALSE",
    "NOTIFY", "SEND_EMAIL", "LIST_DEVICES", "HALT",
})


class OperacionDesconocida(ValueError):
    """La instrucción del IR no pertenece al conjunto del contrato."""


class MaquinaVirtual:
    def ejecutar(self, instruccion: dict[str, Any]) -> dict[str, Any]:
        """Ejecuta los seis pasos en orden y devuelve el contexto acumulado."""
        contexto: dict[str, Any] = {"instruccion": instruccion}
        for paso in PASOS:
            contexto = getattr(self, paso)(contexto)
        return contexto

    def identificar_operacion(self, contexto: dict[str, Any]) -> dict[str, Any]:
        operacion = contexto["instruccion"].get("op")
        if operacion not in OPERACIONES_IR:
            raise OperacionDesconocida(f"Operación fuera del contrato del IR: {operacion!r}")
        contexto["operacion"] = operacion
        return contexto

    def obtener_dispositivo(self, contexto: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Pendiente: S2-17 (VM completa).")

    def validar_estado(self, contexto: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Pendiente: S2-17 (VM completa).")

    def actualizar_estado(self, contexto: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Pendiente: S2-17 (VM completa).")

    def guardar_resultado(self, contexto: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Pendiente: S2-17 (VM completa).")

    def notificar_interfaz(self, contexto: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Pendiente: S2-17 (VM completa).")
