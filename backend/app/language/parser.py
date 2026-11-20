"""Analizador sintáctico (parser) del lenguaje de instrucciones.

Parser de descenso recursivo: recibe los tokens del lexer y construye el AST.
Hay un método por cada regla de la gramática:

    programa      = { SALTO_LINEA },
                    { instruccion, SALTO_LINEA, { SALTO_LINEA } },
                    EOF ;
    instruccion   = simple | condicional ;
    simple        = control | consultar | listar | establecer
                  | notificar | enviar_correo ;
    control       = ( ENCENDER | APAGAR | ACTIVAR | DESACTIVAR | ABRIR | CERRAR ),
                    IDENTIFICADOR ;
    consultar     = CONSULTAR, IDENTIFICADOR ;
    listar        = LISTAR, DISPOSITIVOS ;
    establecer    = ESTABLECER, IDENTIFICADOR, NUMERO ;
    notificar     = NOTIFICAR, CADENA ;
    enviar_correo = ENVIAR, CORREO, A, CADENA, MENSAJE, CADENA ;
    condicional   = SI, condicion, ENTONCES, simple ;
    condicion     = IDENTIFICADOR, operador, valor ;
    operador      = IGUAL | DISTINTO | MAYOR | MENOR | MAYOR_IGUAL | MENOR_IGUAL ;
    valor         = NUMERO | ESTADO ;

El parser solo valida la estructura. Si un dispositivo existe o es compatible
con la operación lo decide la fase semántica.

Ante el primer error lanza ErrorSintactico con línea y columna del token
inesperado.
"""

from __future__ import annotations

from typing import Callable

from .ast_nodes import (
    ESTADOS,
    Condicion,
    Condicional,
    Consultar,
    Control,
    EnviarCorreo,
    Establecer,
    Estado,
    Instruccion,
    InstruccionSimple,
    Listar,
    Notificar,
    Numero,
    Programa,
)
from .errors import ErrorSintactico
from .lexer import tokenizar
from .tokens import TipoToken, Token

T = TipoToken

TOKENS_CONTROL = {T.ENCENDER, T.APAGAR, T.ACTIVAR, T.DESACTIVAR, T.ABRIR, T.CERRAR}
TOKENS_OPERADOR = {
    T.IGUAL,
    T.DISTINTO,
    T.MAYOR,
    T.MENOR,
    T.MAYOR_IGUAL,
    T.MENOR_IGUAL,
}

_COMANDOS = "ENCENDER, APAGAR, ACTIVAR, DESACTIVAR, ABRIR, CERRAR, CONSULTAR, LISTAR, ESTABLECER, NOTIFICAR, ENVIAR"

ESPERADO_INSTRUCCION = f"una instrucción ({_COMANDOS} o SI)"
ESPERADO_ACCION = f"una instrucción después de 'ENTONCES' ({_COMANDOS})"
ESPERADO_DISPOSITIVO = "un identificador de dispositivo"
ESPERADO_OPERADOR = "un operador de comparación (==, !=, >, <, >=, <=)"
ESPERADO_VALOR = f"un número o un estado ({', '.join(ESTADOS)})"


def _describir(token: Token) -> str:
    """Texto legible de un token, para el 'se encontró ...' de los errores."""
    if token.tipo == T.SALTO_LINEA:
        return "fin de línea"
    if token.tipo == T.EOF:
        return "fin de la entrada"
    if token.tipo == T.CADENA:
        return f'la cadena "{token.valor}"'
    return f"'{token.valor}'"


class Parser:
    def __init__(self, tokens: list[Token]):
        if not tokens or tokens[-1].tipo != T.EOF:
            raise ValueError("La lista de tokens debe terminar con EOF")
        self.tokens = tokens
        self.pos = 0
        self._simples: dict[TipoToken, Callable[[], InstruccionSimple]] = {
            **{tipo: self._control for tipo in TOKENS_CONTROL},
            T.CONSULTAR: self._consultar,
            T.LISTAR: self._listar,
            T.ESTABLECER: self._establecer,
            T.NOTIFICAR: self._notificar,
            T.ENVIAR: self._enviar_correo,
        }

    # ---- utilidades --------------------------------------------------------

    def _actual(self) -> Token:
        return self.tokens[self.pos]

    def _avanzar(self) -> Token:
        token = self.tokens[self.pos]
        if token.tipo != T.EOF:
            self.pos += 1
        return token

    def _error(self, esperado: str) -> ErrorSintactico:
        """Error 'se esperaba X y se encontró Y' en el token actual."""
        token = self._actual()
        return ErrorSintactico(
            f"se esperaba {esperado} y se encontró {_describir(token)}",
            token.linea,
            token.columna,
        )

    def _esperar(self, tipo: TipoToken, esperado: str) -> Token:
        if self._actual().tipo != tipo:
            raise self._error(esperado)
        return self._avanzar()

    def _saltar_saltos(self) -> None:
        while self._actual().tipo == T.SALTO_LINEA:
            self._avanzar()

    # ---- programa ----------------------------------------------------------

    def programa(self) -> Programa:
        self._saltar_saltos()
        instrucciones: list[Instruccion] = []

        while self._actual().tipo != T.EOF:
            instrucciones.append(self._instruccion())
            # Cada instrucción debe terminar la línea.
            if self._actual().tipo not in (T.SALTO_LINEA, T.EOF):
                raise self._error("fin de línea")
            self._saltar_saltos()

        return Programa(tuple(instrucciones), linea=1, columna=1)

    def _instruccion(self) -> Instruccion:
        if self._actual().tipo == T.SI:
            return self._condicional()
        return self._simple(ESPERADO_INSTRUCCION)

    def _simple(self, esperado: str) -> InstruccionSimple:
        metodo = self._simples.get(self._actual().tipo)
        if metodo is None:
            raise self._error(esperado)
        return metodo()

    # ---- instrucciones simples -----------------------------------------------

    def _control(self) -> Control:
        operacion = self._avanzar()
        dispositivo = self._esperar(T.IDENTIFICADOR, ESPERADO_DISPOSITIVO)
        return Control(
            operacion.valor,
            dispositivo.valor,
            linea=operacion.linea,
            columna=operacion.columna,
        )

    def _consultar(self) -> Consultar:
        inicio = self._avanzar()
        dispositivo = self._esperar(T.IDENTIFICADOR, ESPERADO_DISPOSITIVO)
        return Consultar(dispositivo.valor, linea=inicio.linea, columna=inicio.columna)

    def _listar(self) -> Listar:
        inicio = self._avanzar()
        self._esperar(T.DISPOSITIVOS, "'DISPOSITIVOS'")
        return Listar(linea=inicio.linea, columna=inicio.columna)

    def _establecer(self) -> Establecer:
        inicio = self._avanzar()
        dispositivo = self._esperar(T.IDENTIFICADOR, ESPERADO_DISPOSITIVO)
        valor = self._esperar(T.NUMERO, "un número")
        return Establecer(
            dispositivo.valor, valor.valor, linea=inicio.linea, columna=inicio.columna
        )

    def _notificar(self) -> Notificar:
        inicio = self._avanzar()
        mensaje = self._esperar(T.CADENA, "una cadena de texto entre comillas")
        return Notificar(mensaje.valor, linea=inicio.linea, columna=inicio.columna)

    def _enviar_correo(self) -> EnviarCorreo:
        inicio = self._avanzar()
        self._esperar(T.CORREO, "'CORREO'")
        self._esperar(T.A, "'A'")
        destinatario = self._esperar(T.CADENA, "una cadena con el destinatario")
        self._esperar(T.MENSAJE, "'MENSAJE'")
        mensaje = self._esperar(T.CADENA, "una cadena con el mensaje")
        return EnviarCorreo(
            destinatario.valor,
            mensaje.valor,
            linea=inicio.linea,
            columna=inicio.columna,
        )

    # ---- condicional ---------------------------------------------------------

    def _condicional(self) -> Condicional:
        si = self._avanzar()
        condicion = self._condicion()
        self._esperar(T.ENTONCES, "'ENTONCES'")

        siguiente = self._actual()
        if siguiente.tipo == T.SI:
            raise ErrorSintactico(
                "no se permite un SI dentro de otro SI",
                siguiente.linea,
                siguiente.columna,
            )
        accion = self._simple(ESPERADO_ACCION)
        return Condicional(condicion, accion, linea=si.linea, columna=si.columna)

    def _condicion(self) -> Condicion:
        izquierda = self._esperar(T.IDENTIFICADOR, ESPERADO_DISPOSITIVO)

        if self._actual().tipo not in TOKENS_OPERADOR:
            raise self._error(ESPERADO_OPERADOR)
        operador = self._avanzar()

        derecha = self._actual()
        if derecha.tipo == T.NUMERO:
            valor = Numero(derecha.valor, linea=derecha.linea, columna=derecha.columna)
        elif derecha.tipo == T.ESTADO:
            valor = Estado(derecha.valor, linea=derecha.linea, columna=derecha.columna)
        else:
            raise self._error(ESPERADO_VALOR)
        self._avanzar()

        return Condicion(
            izquierda.valor,
            operador.valor,
            valor,
            linea=izquierda.linea,
            columna=izquierda.columna,
        )


# ---- funciones de entrada ----------------------------------------------------


def parsear(tokens: list[Token]) -> Programa:
    """Construye el AST a partir de una lista de tokens (terminada en EOF)."""
    return Parser(tokens).programa()


def analizar(texto: str) -> Programa:
    """Análisis léxico + sintáctico de un texto completo.

    Lanza ErrorLexico o ErrorSintactico (ambos heredan de ErrorLenguaje) con
    mensaje, línea y columna.
    """
    return parsear(tokenizar(texto))
