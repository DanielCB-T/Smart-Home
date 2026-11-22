"""Acción semántica construir_instruccion (Ticket S1-15)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from app.language.ast_nodes import (
    Condicion,
    Condicional,
    Consultar,
    Control,
    EnviarCorreo,
    Establecer,
    Instruccion,
    Listar,
    Notificar,
    Programa,
)
from .tabla_simbolos import TablaSimbolos
from .validador import AnalizadorSemantico

ESTADO_DESTINO_POR_OPERACION: dict[str, str] = {
    "ENCENDER": "ENCENDIDO",
    "APAGAR": "APAGADO",
    "ACTIVAR": "ACTIVADA",
    "DESACTIVAR": "DESACTIVADA",
    "ABRIR": "ABIERTA",
    "CERRAR": "CERRADA",
}


@dataclass(frozen=True)
class InstruccionSemantica:
    """Representación semántica enriquecida con metadatos de la tabla de símbolos."""

    tipo_accion: str
    linea: int
    dispositivo: str | None = None
    tipo_dispositivo: str | None = None
    valor: Union[str, int, float, None] = None
    destinatario: str | None = None
    mensaje: str | None = None
    condicion: Condicion | None = None
    accion_condicional: InstruccionSemantica | None = None


def construir_instruccion(
    nodo: Instruccion, tabla: TablaSimbolos
) -> InstruccionSemantica:
    """Construye la estructura semántica de una instrucción validada del AST."""
    if isinstance(nodo, Control):
        simbolo = tabla.obtener(nodo.dispositivo)
        return InstruccionSemantica(
            tipo_accion="SET_STATE",
            linea=nodo.linea,
            dispositivo=nodo.dispositivo,
            tipo_dispositivo=simbolo.tipo if simbolo else None,
            valor=ESTADO_DESTINO_POR_OPERACION[nodo.operacion],
        )

    if isinstance(nodo, Establecer):
        simbolo = tabla.obtener(nodo.dispositivo)
        return InstruccionSemantica(
            tipo_accion="SET_STATE",
            linea=nodo.linea,
            dispositivo=nodo.dispositivo,
            tipo_dispositivo=simbolo.tipo if simbolo else None,
            valor=nodo.valor,
        )

    if isinstance(nodo, Consultar):
        simbolo = tabla.obtener(nodo.dispositivo)
        return InstruccionSemantica(
            tipo_accion="GET_STATE",
            linea=nodo.linea,
            dispositivo=nodo.dispositivo,
            tipo_dispositivo=simbolo.tipo if simbolo else None,
        )

    if isinstance(nodo, Listar):
        return InstruccionSemantica(
            tipo_accion="LIST_DEVICES",
            linea=nodo.linea,
        )

    if isinstance(nodo, Notificar):
        return InstruccionSemantica(
            tipo_accion="NOTIFY",
            linea=nodo.linea,
            mensaje=nodo.mensaje,
        )

    if isinstance(nodo, EnviarCorreo):
        return InstruccionSemantica(
            tipo_accion="SEND_EMAIL",
            linea=nodo.linea,
            destinatario=nodo.destinatario,
            mensaje=nodo.mensaje,
        )

    if isinstance(nodo, Condicional):
        return InstruccionSemantica(
            tipo_accion="CONDITIONAL",
            linea=nodo.linea,
            condicion=nodo.condicion,
            accion_condicional=construir_instruccion(nodo.accion, tabla),
        )

    raise TypeError(f"Nodo de instrucción no soportado: {type(nodo).__name__}")


def analizar_y_construir(
    programa: Programa, tabla: TablaSimbolos | None = None
) -> list[InstruccionSemantica]:
    """Valida semánticamente un Programa y construye sus instrucciones semánticas."""
    tabla_efectiva = tabla if tabla is not None else TablaSimbolos.por_defecto()
    AnalizadorSemantico(tabla_efectiva).analizar(programa)
    return [construir_instruccion(inst, tabla_efectiva) for inst in programa.instrucciones]