"""Generador de Representación Intermedia (IR) según contrato S1-03 / S2-12."""

from __future__ import annotations

from typing import Any

from app.language.ast_nodes import (
    Condicion,
    Condicional,
    Consultar,
    Control,
    EnviarCorreo,
    Establecer,
    Estado,
    Instruccion,
    Listar,
    Notificar,
    Numero,
    Programa,
)
from .construir_instruccion import ESTADO_DESTINO_POR_OPERACION


class GeneradorIR:
    """Traduce un AST validado semánticamente a instrucciones IR."""

    def __init__(self):
        self._contador_temp = 0
        self._contador_etiquetas = 0
        self._instrucciones: list[dict[str, Any]] = []
        self._etiqueta_pendiente: str | None = None

    def _nuevo_temp(self) -> str:
        self._contador_temp += 1
        return f"t{self._contador_temp}"

    def _nueva_etiqueta(self) -> str:
        self._contador_etiquetas += 1
        return f"L{self._contador_etiquetas}"

    def _emitir(self, instr: dict[str, Any]) -> None:
        if self._etiqueta_pendiente is not None:
            instr["etiqueta"] = self._etiqueta_pendiente
            self._etiqueta_pendiente = None
        self._instrucciones.append(instr)

    def generar(self, programa: Programa) -> dict[str, Any]:
        """Genera el programa IR completo con HALT al final."""
        self._contador_temp = 0
        self._contador_etiquetas = 0
        self._instrucciones = []
        self._etiqueta_pendiente = None

        for instruccion in programa.instrucciones:
            self._visitar_instruccion(instruccion)

        ultima_linea = (
            programa.instrucciones[-1].linea if programa.instrucciones else 1
        )
        self._emitir({"op": "HALT", "linea": ultima_linea})

        return {
            "version": "1.0",
            "instrucciones": self._instrucciones,
        }

    def _visitar_instruccion(self, nodo: Instruccion) -> None:
        if isinstance(nodo, Control):
            self._emitir(
                {
                    "op": "SET_STATE",
                    "dispositivo": nodo.dispositivo,
                    "valor": ESTADO_DESTINO_POR_OPERACION[nodo.operacion],
                    "linea": nodo.linea,
                }
            )
        elif isinstance(nodo, Establecer):
            self._emitir(
                {
                    "op": "SET_STATE",
                    "dispositivo": nodo.dispositivo,
                    "valor": nodo.valor,
                    "linea": nodo.linea,
                }
            )
        elif isinstance(nodo, Consultar):
            dest = self._nuevo_temp()
            self._emitir(
                {
                    "op": "GET_STATE",
                    "dispositivo": nodo.dispositivo,
                    "destino": dest,
                    "mostrar": True,
                    "linea": nodo.linea,
                }
            )
        elif isinstance(nodo, Listar):
            self._emitir({"op": "LIST_DEVICES", "linea": nodo.linea})
        elif isinstance(nodo, Notificar):
            self._emitir(
                {
                    "op": "NOTIFY",
                    "mensaje": nodo.mensaje,
                    "linea": nodo.linea,
                }
            )
        elif isinstance(nodo, EnviarCorreo):
            self._emitir(
                {
                    "op": "SEND_EMAIL",
                    "destinatario": nodo.destinatario,
                    "mensaje": nodo.mensaje,
                    "linea": nodo.linea,
                }
            )
        elif isinstance(nodo, Condicional):
            self._visitar_condicional(nodo)

    def _visitar_condicional(self, nodo: Condicional) -> None:
        cond: Condicion = nodo.condicion
        temp_lectura = self._nuevo_temp()
        self._emitir(
            {
                "op": "GET_STATE",
                "dispositivo": cond.izquierda,
                "destino": temp_lectura,
                "linea": cond.linea,
            }
        )

        valor_derecha = (
            cond.derecha.valor
            if isinstance(cond.derecha, (Numero, Estado))
            else cond.derecha
        )
        temp_cmp = self._nuevo_temp()
        self._emitir(
            {
                "op": "COMPARE",
                "izquierda": {"temp": temp_lectura},
                "operador": cond.operador,
                "derecha": {"valor": valor_derecha},
                "destino": temp_cmp,
                "linea": cond.linea,
            }
        )

        etiqueta_fin = self._nueva_etiqueta()
        self._emitir(
            {
                "op": "JUMP_IF_FALSE",
                "condicion": temp_cmp,
                "salto_a": etiqueta_fin,
                "linea": nodo.linea,
            }
        )

        self._visitar_instruccion(nodo.accion)
        self._etiqueta_pendiente = etiqueta_fin


def generar_ir(programa: Programa) -> dict[str, Any]:
    """Función auxiliar para generar el IR de un Programa."""
    return GeneradorIR().generar(programa)