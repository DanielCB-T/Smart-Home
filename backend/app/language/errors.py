"""Errores del procesamiento del lenguaje."""

from __future__ import annotations


class ErrorLenguaje(Exception):
    """Base de los errores con posición en el código fuente."""

    tipo = "Error"

    def __init__(self, mensaje: str, linea: int, columna: int):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna

    def __str__(self) -> str:
        return f"{self.tipo}: {self.mensaje} (línea {self.linea}, col {self.columna})"

    def a_dict(self) -> dict:
        """Representación serializable para la API."""
        return {
            "tipo": self.tipo,
            "mensaje": self.mensaje,
            "linea": self.linea,
            "columna": self.columna,
        }


class ErrorLexico(ErrorLenguaje):
    tipo = "Error léxico"


class ErrorSintactico(ErrorLenguaje):
    tipo = "Error sintáctico"
