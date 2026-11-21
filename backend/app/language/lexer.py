"""Analizador léxico (lexer) del lenguaje de instrucciones.

Convierte el texto de entrada en una lista de tokens. Reglas:
- Espacios, tabuladores y '\\r' se ignoran.
- Los comentarios empiezan con '#' y llegan hasta el fin de línea.
- Las cadenas van entre comillas dobles o simples y no cruzan líneas.
- Se agrega un SALTO_LINEA implícito antes de EOF si la última línea
  tiene contenido, para que no haga falta terminar con Enter.
- Ante el primer carácter inválido se lanza ErrorLexico.
"""

from __future__ import annotations

from .errors import ErrorLexico
from .tokens import OPERADORES, PALABRAS_RESERVADAS, Token, TipoToken


def _es_letra(c: str) -> bool:
    return c.isascii() and (c.isalpha() or c == "_")


def _es_digito(c: str) -> bool:
    return c.isascii() and c.isdigit()


def _es_alfanumerico(c: str) -> bool:
    return _es_letra(c) or _es_digito(c)


class Lexer:
    def __init__(self, texto: str):
        self.texto = texto
        self.pos = 0
        self.linea = 1
        self.columna = 1

    # ---- utilidades de lectura -------------------------------------------

    def _actual(self) -> str:
        """Carácter actual o '' si se llegó al final."""
        return self.texto[self.pos] if self.pos < len(self.texto) else ""

    def _siguiente(self) -> str:
        return self.texto[self.pos + 1] if self.pos + 1 < len(self.texto) else ""

    def _avanzar(self) -> str:
        c = self.texto[self.pos]
        self.pos += 1
        if c == "\n":
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        return c

    # ---- tokenización ----------------------------------------------------

    def tokenizar(self) -> list[Token]:
        tokens: list[Token] = []

        while self.pos < len(self.texto):
            c = self._actual()
            linea, col = self.linea, self.columna

            if c in " \t\r":
                self._avanzar()
            elif c == "#":
                while self._actual() not in ("", "\n"):
                    self._avanzar()
            elif c == "\n":
                self._avanzar()
                tokens.append(Token(TipoToken.SALTO_LINEA, "\n", linea, col))
            elif _es_letra(c):
                tokens.append(self._palabra(linea, col))
            elif _es_digito(c) or (c == "-" and _es_digito(self._siguiente())):
                tokens.append(self._numero(linea, col))
            elif c in "\"'":
                tokens.append(self._cadena(linea, col))
            elif c in "=!<>":
                tokens.append(self._operador(linea, col))
            else:
                raise ErrorLexico(f"carácter '{c}' no reconocido", linea, col)

        # SALTO_LINEA implícito para que la última instrucción quede cerrada.
        if tokens and tokens[-1].tipo != TipoToken.SALTO_LINEA:
            tokens.append(Token(TipoToken.SALTO_LINEA, "\n", self.linea, self.columna))
        tokens.append(Token(TipoToken.EOF, "", self.linea, self.columna))
        return tokens

    # ---- reglas ----------------------------------------------------------

    def _palabra(self, linea: int, col: int) -> Token:
        inicio = self.pos
        while _es_alfanumerico(self._actual()):
            self._avanzar()
        lexema = self.texto[inicio : self.pos]

        tipo = PALABRAS_RESERVADAS.get(lexema.upper())
        if tipo is None:
            return Token(TipoToken.IDENTIFICADOR, lexema, linea, col)
        return Token(tipo, lexema.upper(), linea, col)

    def _numero(self, linea: int, col: int) -> Token:
        inicio = self.pos
        if self._actual() == "-":
            self._avanzar()
        while _es_digito(self._actual()):
            self._avanzar()
        if self._actual() == "." and _es_digito(self._siguiente()):
            self._avanzar()
            while _es_digito(self._actual()):
                self._avanzar()

        lexema = self.texto[inicio : self.pos]
        if _es_letra(self._actual()):
            raise ErrorLexico(
                f"número mal formado '{lexema}{self._actual()}...': "
                "los identificadores no pueden empezar con un dígito",
                linea,
                col,
            )
        valor = float(lexema) if "." in lexema else int(lexema)
        return Token(TipoToken.NUMERO, valor, linea, col)

    def _cadena(self, linea: int, col: int) -> Token:
        comilla = self._avanzar()
        contenido: list[str] = []
        while True:
            c = self._actual()
            if c in ("", "\n"):
                # El error se reporta donde abrió la cadena.
                raise ErrorLexico("cadena sin cerrar", linea, col)
            if c == comilla:
                self._avanzar()
                break
            contenido.append(self._avanzar())
        return Token(TipoToken.CADENA, "".join(contenido), linea, col)

    def _operador(self, linea: int, col: int) -> Token:
        c = self._actual()
        dos = c + self._siguiente()
        if dos in OPERADORES:
            self._avanzar()
            self._avanzar()
            return Token(OPERADORES[dos], dos, linea, col)
        if c in OPERADORES:  # '>' y '<'
            self._avanzar()
            return Token(OPERADORES[c], c, linea, col)
        if c == "=":
            raise ErrorLexico("'=' solo no es válido, ¿quisiste decir '=='?", linea, col)
        raise ErrorLexico("'!' solo no es válido, ¿quisiste decir '!='?", linea, col)


def tokenizar(texto: str) -> list[Token]:
    """Atajo: tokeniza un texto completo."""
    return Lexer(texto).tokenizar()
