"""Analizador semántico para el AST de CommandFlow (SmartHome)."""

from __future__ import annotations

import re

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
from .errors import ErrorSemantico
from .tabla_simbolos import SimboloDispositivo, TablaSimbolos

_REGEX_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_OPERADORES_ORDEN = frozenset({">", "<", ">=", "<="})


class AnalizadorSemantico:
    """Valida un AST contra una TablaSimbolos."""

    def __init__(self, tabla: TablaSimbolos):
        self.tabla = tabla

    def analizar(self, programa: Programa) -> Programa:
        """Valida todas las instrucciones del programa y retorna el AST validado."""
        for instruccion in programa.instrucciones:
            self._validar_instruccion(instruccion)
        return programa

    def _validar_instruccion(self, nodo: Instruccion) -> None:
        if isinstance(nodo, Control):
            self._validar_control(nodo)
        elif isinstance(nodo, Consultar):
            self._validar_consultar(nodo)
        elif isinstance(nodo, Establecer):
            self._validar_establecer(nodo)
        elif isinstance(nodo, Listar):
            pass
        elif isinstance(nodo, Notificar):
            self._validar_notificar(nodo)
        elif isinstance(nodo, EnviarCorreo):
            self._validar_enviar_correo(nodo)
        elif isinstance(nodo, Condicional):
            self._validar_condicion(nodo.condicion)
            self._validar_instruccion(nodo.accion)

    def _obtener_dispositivo_o_error(
        self, nombre: str, linea: int, columna: int
    ) -> SimboloDispositivo:
        simbolo = self.tabla.obtener(nombre)
        if simbolo is None:
            raise ErrorSemantico(
                f"el dispositivo '{nombre}' no existe", linea, columna
            )
        return simbolo

    def _validar_control(self, nodo: Control) -> None:
        simbolo = self._obtener_dispositivo_o_error(
            nodo.dispositivo, nodo.linea, nodo.columna
        )
        if nodo.operacion not in simbolo.operaciones_permitidas:
            permitidas = ", ".join(sorted(simbolo.operaciones_permitidas))
            raise ErrorSemantico(
                f"la operación '{nodo.operacion}' no es compatible con '{nodo.dispositivo}' "
                f"(tipo '{simbolo.tipo}'; operaciones permitidas: {permitidas})",
                nodo.linea,
                nodo.columna,
            )

    def _validar_consultar(self, nodo: Consultar) -> None:
        simbolo = self._obtener_dispositivo_o_error(
            nodo.dispositivo, nodo.linea, nodo.columna
        )
        if "CONSULTAR" not in simbolo.operaciones_permitidas:
            raise ErrorSemantico(
                f"el dispositivo '{nodo.dispositivo}' no admite 'CONSULTAR'",
                nodo.linea,
                nodo.columna,
            )

    def _validar_establecer(self, nodo: Establecer) -> None:
        simbolo = self._obtener_dispositivo_o_error(
            nodo.dispositivo, nodo.linea, nodo.columna
        )
        if not simbolo.es_numerico or "ESTABLECER" not in simbolo.operaciones_permitidas:
            raise ErrorSemantico(
                f"'{nodo.dispositivo}' es de tipo '{simbolo.tipo}' y no admite 'ESTABLECER' "
                f"(solo sensores numéricos)",
                nodo.linea,
                nodo.columna,
            )

    def _validar_notificar(self, nodo: Notificar) -> None:
        if not nodo.mensaje.strip():
            raise ErrorSemantico(
                "el mensaje de notificación no puede estar vacío",
                nodo.linea,
                nodo.columna,
            )

    def _validar_enviar_correo(self, nodo: EnviarCorreo) -> None:
        if not _REGEX_EMAIL.match(nodo.destinatario):
            raise ErrorSemantico(
                f"dirección de correo inválida: '{nodo.destinatario}'",
                nodo.linea,
                nodo.columna,
            )
        if not nodo.mensaje.strip():
            raise ErrorSemantico(
                "el mensaje del correo no puede estar vacío",
                nodo.linea,
                nodo.columna,
            )

    def _validar_condicion(self, cond: Condicion) -> None:
        simbolo = self._obtener_dispositivo_o_error(
            cond.izquierda, cond.linea, cond.columna
        )

        if simbolo.es_numerico:
            if not isinstance(cond.derecha, Numero):
                raise ErrorSemantico(
                    f"no se puede comparar el sensor numérico '{cond.izquierda}' "
                    f"con el estado '{cond.derecha.valor}'",
                    cond.derecha.linea,
                    cond.derecha.columna,
                )
        else:
            if not isinstance(cond.derecha, Estado):
                raise ErrorSemantico(
                    f"el dispositivo '{cond.izquierda}' (tipo '{simbolo.tipo}') "
                    f"solo puede compararse con un estado, no con el número {cond.derecha.valor}",
                    cond.derecha.linea,
                    cond.derecha.columna,
                )
            if cond.operador in _OPERADORES_ORDEN:
                raise ErrorSemantico(
                    f"el operador '{cond.operador}' no es válido para estados; "
                    f"use '==' o '!='",
                    cond.linea,
                    cond.columna,
                )
            if cond.derecha.valor not in simbolo.estados_permitidos:
                permitidos = ", ".join(sorted(simbolo.estados_permitidos))
                raise ErrorSemantico(
                    f"el estado '{cond.derecha.valor}' no aplica para '{cond.izquierda}' "
                    f"(tipo '{simbolo.tipo}'; estados válidos: {permitidos})",
                    cond.derecha.linea,
                    cond.derecha.columna,
                )


def validar_semantica(programa: Programa, tabla: TablaSimbolos | None = None) -> Programa:
    """Valida semánticamente un Programa usando la tabla indicada o la tabla por defecto."""
    tabla_efectiva = tabla if tabla is not None else TablaSimbolos.por_defecto()
    return AnalizadorSemantico(tabla_efectiva).analizar(programa)