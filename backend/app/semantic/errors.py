"""Errores del análisis semántico."""

from __future__ import annotations

from app.language.errors import ErrorLenguaje


class ErrorSemantico(ErrorLenguaje):
    """Error detectado al validar existencia, tipos o compatibilidad de dispositivos."""

    tipo = "Error semántico" 