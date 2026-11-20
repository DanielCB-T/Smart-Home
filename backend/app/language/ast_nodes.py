"""Nodos del árbol sintáctico abstracto (AST).

El parser construye estos nodos y la fase semántica los recorre. Así el resto
del sistema no depende del texto original.

Correspondencia con la gramática:

    programa      -> Programa
    control       -> Control          (ENCENDER, APAGAR, ACTIVAR, DESACTIVAR, ABRIR, CERRAR)
    consultar     -> Consultar
    listar        -> Listar
    establecer    -> Establecer
    notificar     -> Notificar
    enviar_correo -> EnviarCorreo
    condicional   -> Condicional(Condicion, <instrucción simple>)
    valor         -> Numero | Estado

Convenciones:
- Los nodos son inmutables (frozen): la fase semántica no debe modificarlos.
- Todos llevan `linea` y `columna` (base 1) para reportar errores con posición.
  Esos campos NO participan en la igualdad: dos ASTs son iguales si tienen la
  misma estructura, sin importar dónde se escribieron.
- Los nombres de dispositivo conservan mayúsculas/minúsculas tal como se
  escribieron; las operaciones, operadores y estados van normalizados.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Union

from .tokens import OPERADORES, PALABRAS_RESERVADAS, TipoToken

# --- Conjuntos de valores válidos --------------------------------------------

OPERACIONES_CONTROL: tuple[str, ...] = (
    "ENCENDER",
    "APAGAR",
    "ACTIVAR",
    "DESACTIVAR",
    "ABRIR",
    "CERRAR",
)

OPERADORES_COMPARACION: tuple[str, ...] = tuple(OPERADORES)  # ==, !=, >=, <=, >, <

ESTADOS: tuple[str, ...] = tuple(
    palabra for palabra, tipo in PALABRAS_RESERVADAS.items() if tipo == TipoToken.ESTADO
)


# --- Base --------------------------------------------------------------------


@dataclass(frozen=True)
class Nodo:
    """Base de todos los nodos. Guarda la posición en el código fuente."""

    linea: int = field(default=0, kw_only=True, compare=False)
    columna: int = field(default=0, kw_only=True, compare=False)

    def a_dict(self) -> dict:
        """Representación serializable (para la API y para mostrar el árbol)."""
        datos: dict = {"tipo": type(self).__name__}
        for f in fields(self):
            if f.name in ("linea", "columna"):
                continue
            datos[f.name] = _serializar(getattr(self, f.name))
        datos["linea"] = self.linea
        datos["columna"] = self.columna
        return datos


def _serializar(valor):
    if isinstance(valor, Nodo):
        return valor.a_dict()
    if isinstance(valor, (list, tuple)):
        return [_serializar(v) for v in valor]
    return valor


# --- Valores (lado derecho de una condición) -----------------------------------


@dataclass(frozen=True)
class Numero(Nodo):
    """Literal numérico: 30, -5, 22.5."""

    valor: Union[int, float]


@dataclass(frozen=True)
class Estado(Nodo):
    """Literal de estado: ENCENDIDO, APAGADO, ACTIVADA, DESACTIVADA, ABIERTA, CERRADA."""

    valor: str

    def __post_init__(self):
        if self.valor not in ESTADOS:
            raise ValueError(f"Estado inválido: {self.valor!r}")


# --- Instrucciones -------------------------------------------------------------


@dataclass(frozen=True)
class Control(Nodo):
    """ENCENDER led1 / APAGAR led1 / ACTIVAR alarma1 / DESACTIVAR alarma1 /
    ABRIR puerta1 / CERRAR puerta1."""

    operacion: str
    dispositivo: str

    def __post_init__(self):
        if self.operacion not in OPERACIONES_CONTROL:
            raise ValueError(f"Operación de control inválida: {self.operacion!r}")


@dataclass(frozen=True)
class Consultar(Nodo):
    """CONSULTAR led1"""

    dispositivo: str


@dataclass(frozen=True)
class Listar(Nodo):
    """LISTAR DISPOSITIVOS"""


@dataclass(frozen=True)
class Establecer(Nodo):
    """ESTABLECER temp1 35  (fija el valor simulado de un sensor)."""

    dispositivo: str
    valor: Union[int, float]


@dataclass(frozen=True)
class Notificar(Nodo):
    """NOTIFICAR "mensaje" """

    mensaje: str


@dataclass(frozen=True)
class EnviarCorreo(Nodo):
    """ENVIAR CORREO A "destinatario" MENSAJE "texto" """

    destinatario: str
    mensaje: str


# --- Condicional -----------------------------------------------------------------


@dataclass(frozen=True)
class Condicion(Nodo):
    """IDENTIFICADOR operador valor, por ejemplo: led1 == ENCENDIDO."""

    izquierda: str
    operador: str
    derecha: Union[Numero, Estado]

    def __post_init__(self):
        if self.operador not in OPERADORES_COMPARACION:
            raise ValueError(f"Operador de comparación inválido: {self.operador!r}")


# Instrucción que puede ir dentro de un SI (sin SI anidado).
InstruccionSimple = Union[Control, Consultar, Listar, Establecer, Notificar, EnviarCorreo]


@dataclass(frozen=True)
class Condicional(Nodo):
    """SI <condicion> ENTONCES <accion>"""

    condicion: Condicion
    accion: InstruccionSimple


# --- Programa --------------------------------------------------------------------

Instruccion = Union[InstruccionSimple, Condicional]


@dataclass(frozen=True)
class Programa(Nodo):
    """Secuencia de instrucciones, en el orden en que se escribieron."""

    instrucciones: tuple[Instruccion, ...]
