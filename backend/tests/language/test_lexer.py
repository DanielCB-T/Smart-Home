import pytest

from app.language.errors import ErrorLexico
from app.language.lexer import tokenizar
from app.language.tokens import PALABRAS_RESERVADAS, TipoToken

T = TipoToken


def tipos(texto: str) -> list[TipoToken]:
    return [t.tipo for t in tokenizar(texto)]


# ---------------------------------------------------------------- válidos


def test_instruccion_simple():
    assert tipos("ENCENDER led1") == [T.ENCENDER, T.IDENTIFICADOR, T.SALTO_LINEA, T.EOF]


def test_entrada_vacia():
    assert tipos("") == [T.EOF]


def test_solo_espacios_y_comentario():
    assert tipos("   \t # nada aquí") == [T.EOF]


def test_palabras_reservadas_no_distinguen_mayusculas():
    tokens = tokenizar("encender led1")
    assert tokens[0].tipo == T.ENCENDER
    assert tokens[0].valor == "ENCENDER"
    assert tipos("EnCeNdEr led1")[0] == T.ENCENDER


def test_identificadores_distinguen_mayusculas():
    tokens = tokenizar("ENCENDER LED1")
    assert tokens[1].tipo == T.IDENTIFICADOR
    assert tokens[1].valor == "LED1"


@pytest.mark.parametrize("palabra,tipo", list(PALABRAS_RESERVADAS.items()))
def test_cada_palabra_reservada(palabra, tipo):
    assert tokenizar(palabra)[0].tipo == tipo
    assert tokenizar(palabra.lower())[0].tipo == tipo


@pytest.mark.parametrize(
    "estado",
    ["ENCENDIDO", "APAGADO", "ACTIVADA", "DESACTIVADA", "ABIERTA", "CERRADA"],
)
def test_estados(estado):
    tokens = tokenizar(estado)
    assert tokens[0].tipo == T.ESTADO
    assert tokens[0].valor == estado


def test_identificador_con_guion_bajo_y_digitos():
    tokens = tokenizar("ENCENDER luz_sala2")
    assert tokens[1].tipo == T.IDENTIFICADOR
    assert tokens[1].valor == "luz_sala2"


def test_identificador_que_contiene_palabra_reservada():
    # "si_temp" no es la palabra SI, es un identificador.
    assert tokenizar("si_temp")[0].tipo == T.IDENTIFICADOR


@pytest.mark.parametrize(
    "texto,valor",
    [("30", 30), ("-5", -5), ("22.5", 22.5), ("0", 0), ("-0.5", -0.5)],
)
def test_numeros(texto, valor):
    tok = tokenizar(f"ESTABLECER temp1 {texto}")[2]
    assert tok.tipo == T.NUMERO
    assert tok.valor == valor
    assert type(tok.valor) is type(valor)


@pytest.mark.parametrize(
    "texto,contenido",
    [
        ('"Hola"', "Hola"),
        ("'Hola'", "Hola"),
        ('""', ""),
        ("\"it's\"", "it's"),
        ("'di \"hola\"'", 'di "hola"'),
        ('"con # símbolo"', "con # símbolo"),
        ('"usuario@ejemplo.com"', "usuario@ejemplo.com"),
    ],
)
def test_cadenas(texto, contenido):
    tok = tokenizar(f"NOTIFICAR {texto}")[1]
    assert tok.tipo == T.CADENA
    assert tok.valor == contenido


@pytest.mark.parametrize(
    "texto,tipo",
    [
        ("==", T.IGUAL),
        ("!=", T.DISTINTO),
        (">", T.MAYOR),
        ("<", T.MENOR),
        (">=", T.MAYOR_IGUAL),
        ("<=", T.MENOR_IGUAL),
    ],
)
def test_operadores(texto, tipo):
    tokens = tokenizar(f"temp1 {texto} 30")
    assert tokens[1].tipo == tipo
    assert tokens[1].valor == texto


def test_operadores_sin_espacios():
    assert tipos("temp1>=30")[:3] == [T.IDENTIFICADOR, T.MAYOR_IGUAL, T.NUMERO]


# ---------------------------------------------------------- saltos de línea


def test_salto_implicito_al_final():
    assert tipos("APAGAR led1")[-2:] == [T.SALTO_LINEA, T.EOF]


def test_no_duplica_salto_si_termina_con_enter():
    assert tipos("APAGAR led1\n") == [T.APAGAR, T.IDENTIFICADOR, T.SALTO_LINEA, T.EOF]


def test_varias_lineas():
    assert tipos("ENCENDER led1\nAPAGAR led2") == [
        T.ENCENDER, T.IDENTIFICADOR, T.SALTO_LINEA,
        T.APAGAR, T.IDENTIFICADOR, T.SALTO_LINEA,
        T.EOF,
    ]  # fmt: skip


def test_lineas_en_blanco_se_conservan_como_saltos():
    assert tipos("ENCENDER led1\n\n\nAPAGAR led1").count(T.SALTO_LINEA) == 4


def test_crlf():
    assert tipos("ENCENDER led1\r\nAPAGAR led1\r\n") == [
        T.ENCENDER, T.IDENTIFICADOR, T.SALTO_LINEA,
        T.APAGAR, T.IDENTIFICADOR, T.SALTO_LINEA,
        T.EOF,
    ]  # fmt: skip


def test_comentario_al_final_de_linea():
    assert tipos("ENCENDER led1 # enciende la luz\nAPAGAR led1") == [
        T.ENCENDER, T.IDENTIFICADOR, T.SALTO_LINEA,
        T.APAGAR, T.IDENTIFICADOR, T.SALTO_LINEA,
        T.EOF,
    ]  # fmt: skip


def test_linea_de_solo_comentario_entre_instrucciones():
    assert tipos("ENCENDER led1\n# nota\nAPAGAR led1").count(T.SALTO_LINEA) == 3


# ---------------------------------------------------------------- posiciones


def test_posiciones_en_una_linea():
    tokens = tokenizar("ENCENDER led1")
    assert (tokens[0].linea, tokens[0].columna) == (1, 1)
    assert (tokens[1].linea, tokens[1].columna) == (1, 10)


def test_posiciones_en_varias_lineas():
    tokens = tokenizar("ENCENDER led1\n  APAGAR led2")
    apagar = next(t for t in tokens if t.tipo == T.APAGAR)
    led2 = tokens[-3]
    assert (apagar.linea, apagar.columna) == (2, 3)
    assert (led2.linea, led2.columna) == (2, 10)


def test_posicion_despues_de_cadena():
    tokens = tokenizar('NOTIFICAR "hola" # x')
    assert (tokens[1].linea, tokens[1].columna) == (1, 11)


def test_a_dict():
    d = tokenizar("ENCENDER led1")[1].a_dict()
    assert d == {"tipo": "IDENTIFICADOR", "valor": "led1", "linea": 1, "columna": 10}


# ------------------------------------------------------------ errores léxicos


def test_error_caracter_no_reconocido():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar("ENCENDER led1@")
    assert "carácter '@' no reconocido" in exc.value.mensaje
    assert (exc.value.linea, exc.value.columna) == (1, 14)
    assert str(exc.value) == (
        "Error léxico: carácter '@' no reconocido (línea 1, col 14)"
    )


def test_error_en_segunda_linea():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar("ENCENDER led1\nAPAGAR $led2")
    assert (exc.value.linea, exc.value.columna) == (2, 8)


def test_error_cadena_sin_cerrar_al_final():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar('NOTIFICAR "hola')
    assert "cadena sin cerrar" in exc.value.mensaje
    assert (exc.value.linea, exc.value.columna) == (1, 11)


def test_error_cadena_sin_cerrar_antes_de_salto():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar('NOTIFICAR "hola\nAPAGAR led1')
    assert "cadena sin cerrar" in exc.value.mensaje
    assert exc.value.linea == 1


def test_error_cadena_con_comillas_distintas():
    with pytest.raises(ErrorLexico):
        tokenizar("NOTIFICAR \"hola'")


def test_error_igual_solo():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar("SI temp1 = 30 ENTONCES APAGAR led1")
    assert "¿quisiste decir '=='?" in exc.value.mensaje
    assert (exc.value.linea, exc.value.columna) == (1, 10)


def test_error_exclamacion_sola():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar("SI temp1 ! 30 ENTONCES APAGAR led1")
    assert "¿quisiste decir '!='?" in exc.value.mensaje


def test_error_numero_pegado_a_letras():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar("ENCENDER 1led")
    assert "número mal formado" in exc.value.mensaje
    assert (exc.value.linea, exc.value.columna) == (1, 10)


def test_error_guion_suelto():
    with pytest.raises(ErrorLexico) as exc:
        tokenizar("ESTABLECER temp1 - 5")
    assert "carácter '-' no reconocido" in exc.value.mensaje


def test_error_punto_suelto():
    with pytest.raises(ErrorLexico):
        tokenizar("ESTABLECER temp1 30.")


def test_error_caracter_unicode_no_ascii():
    with pytest.raises(ErrorLexico):
        tokenizar("ENCENDER luz_ñ")


# --------------------------------------------- escenarios de la sección 16


def test_correo_completo():
    tokens = tokenizar('ENVIAR CORREO A "usuario@ejemplo.com" MENSAJE "Hola, esta es una prueba"')
    assert [t.tipo for t in tokens] == [
        T.ENVIAR, T.CORREO, T.A, T.CADENA, T.MENSAJE, T.CADENA, T.SALTO_LINEA, T.EOF,
    ]  # fmt: skip
    assert tokens[3].valor == "usuario@ejemplo.com"
    assert tokens[5].valor == "Hola, esta es una prueba"


def test_condicional_completo():
    assert tipos("SI led1 == ENCENDIDO ENTONCES APAGAR led1") == [
        T.SI, T.IDENTIFICADOR, T.IGUAL, T.ESTADO, T.ENTONCES,
        T.APAGAR, T.IDENTIFICADOR, T.SALTO_LINEA, T.EOF,
    ]  # fmt: skip


def test_condicional_con_numero():
    assert tipos("SI temperatura > 30 ENTONCES ENCENDER ventilador1")[:4] == [
        T.SI, T.IDENTIFICADOR, T.MAYOR, T.NUMERO,
    ]


def test_listar_dispositivos():
    assert tipos("LISTAR DISPOSITIVOS") == [T.LISTAR, T.DISPOSITIVOS, T.SALTO_LINEA, T.EOF]


def test_notificar():
    assert tipos('NOTIFICAR "Prueba"') == [T.NOTIFICAR, T.CADENA, T.SALTO_LINEA, T.EOF]


def test_instruccion_incompleta_es_valida_lexicamente():
    # "ENCENDER" solo falla en el parser, no en el lexer.
    assert tipos("ENCENDER") == [T.ENCENDER, T.SALTO_LINEA, T.EOF]


def test_dispositivo_inexistente_es_valido_lexicamente():
    # "dispositivo99" lo rechaza la fase semántica, no el lexer.
    assert tipos("ENCENDER dispositivo99")[1] == T.IDENTIFICADOR


@pytest.mark.parametrize(
    "instruccion",
    [
        "ENCENDER led1", "APAGAR led1", "ACTIVAR alarma1", "DESACTIVAR alarma1",
        "ABRIR puerta_principal", "CERRAR ventana1", "CONSULTAR led1",
        "LISTAR DISPOSITIVOS", "ESTABLECER temp1 35", 'NOTIFICAR "Prueba"',
    ],
)  # fmt: skip
def test_comandos_del_catalogo_sin_errores(instruccion):
    assert tokenizar(instruccion)[-1].tipo == T.EOF
