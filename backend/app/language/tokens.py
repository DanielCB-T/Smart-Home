"""Definición de tokens del lenguaje de instrucciones.
Decisiones de diseño:
- Las palabras reservadas NO distinguen mayúsculas/minúsculas.
- Los identificadores SÍ distinguen mayúsculas/minúsculas.
- Los estados (ENCENDIDO, APAGADO, ...) son palabras reservadas y se
  agrupan bajo un único tipo de token: ESTADO.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union


class TipoToken(Enum):
    # Comandos de control de dispositivos
    ENCENDER = "ENCENDER"
    APAGAR = "APAGAR"
    ACTIVAR = "ACTIVAR"
    DESACTIVAR = "DESACTIVAR"
    ABRIR = "ABRIR"
    CERRAR = "CERRAR"

    # Otros comandos
    CONSULTAR = "CONSULTAR"
    LISTAR = "LISTAR"
    DISPOSITIVOS = "DISPOSITIVOS"
    ESTABLECER = "ESTABLECER"
    NOTIFICAR = "NOTIFICAR"

    # Envío de correo
    ENVIAR = "ENVIAR"
    CORREO = "CORREO"
    A = "A"
    MENSAJE = "MENSAJE"

    # Condicional
    SI = "SI"
    ENTONCES = "ENTONCES"

    # Valores de estado
    ESTADO = "ESTADO"

    # Literales e identificadores
    IDENTIFICADOR = "IDENTIFICADOR"
    NUMERO = "NUMERO"
    CADENA = "CADENA"

    # Operadores de comparación
    IGUAL = "IGUAL"  # ==
    DISTINTO = "DISTINTO"  # !=
    MAYOR = "MAYOR"  # >
    MENOR = "MENOR"  # <
    MAYOR_IGUAL = "MAYOR_IGUAL"  # >=
    MENOR_IGUAL = "MENOR_IGUAL"  # <=

    # Estructura
    SALTO_LINEA = "SALTO_LINEA"
    EOF = "EOF"


# Palabras reservadas (en mayúsculas) -> tipo de token.
PALABRAS_RESERVADAS: dict[str, TipoToken] = {
    "ENCENDER": TipoToken.ENCENDER,
    "APAGAR": TipoToken.APAGAR,
    "ACTIVAR": TipoToken.ACTIVAR,
    "DESACTIVAR": TipoToken.DESACTIVAR,
    "ABRIR": TipoToken.ABRIR,
    "CERRAR": TipoToken.CERRAR,
    "CONSULTAR": TipoToken.CONSULTAR,
    "LISTAR": TipoToken.LISTAR,
    "DISPOSITIVOS": TipoToken.DISPOSITIVOS,
    "ESTABLECER": TipoToken.ESTABLECER,
    "NOTIFICAR": TipoToken.NOTIFICAR,
    "ENVIAR": TipoToken.ENVIAR,
    "CORREO": TipoToken.CORREO,
    "A": TipoToken.A,
    "MENSAJE": TipoToken.MENSAJE,
    "SI": TipoToken.SI,
    "ENTONCES": TipoToken.ENTONCES,
    # Estados
    "ENCENDIDO": TipoToken.ESTADO,
    "APAGADO": TipoToken.ESTADO,
    "ACTIVADA": TipoToken.ESTADO,
    "DESACTIVADA": TipoToken.ESTADO,
    "ABIERTA": TipoToken.ESTADO,
    "CERRADA": TipoToken.ESTADO,
}

# Operadores de comparación (lexema -> tipo).
OPERADORES: dict[str, TipoToken] = {
    "==": TipoToken.IGUAL,
    "!=": TipoToken.DISTINTO,
    ">=": TipoToken.MAYOR_IGUAL,
    "<=": TipoToken.MENOR_IGUAL,
    ">": TipoToken.MAYOR,
    "<": TipoToken.MENOR,
}

Valor = Union[str, int, float]


@dataclass(frozen=True)
class Token:
    """Un token con su posición (línea y columna, base 1).

    valor:
      - palabras reservadas y ESTADO: texto normalizado en mayúsculas
      - IDENTIFICADOR: texto tal cual se escribió
      - NUMERO: int o float
      - CADENA: contenido sin las comillas
      - operadores: el lexema (p. ej. "==")
    """

    tipo: TipoToken
    valor: Valor
    linea: int
    columna: int

    def a_dict(self) -> dict:
        """Representación serializable (útil para mostrarla en la interfaz)."""
        return {
            "tipo": self.tipo.name,
            "valor": self.valor,
            "linea": self.linea,
            "columna": self.columna,
        }
