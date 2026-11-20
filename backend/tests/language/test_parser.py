import pytest

from app.language.ast_nodes import (
    Condicion,
    Condicional,
    Consultar,
    Control,
    EnviarCorreo,
    Establecer,
    Estado,
    Listar,
    Notificar,
    Numero,
    Programa,
)
from app.language.errors import ErrorLexico, ErrorSintactico
from app.language.lexer import tokenizar
from app.language.parser import analizar, parsear
from app.language.tokens import TipoToken, Token


def una(texto):
    """Analiza un texto con una sola instrucción y devuelve esa instrucción."""
    programa = analizar(texto)
    assert len(programa.instrucciones) == 1
    return programa.instrucciones[0]


def error(texto) -> ErrorSintactico:
    with pytest.raises(ErrorSintactico) as exc:
        analizar(texto)
    return exc.value


# ------------------------------------------------------ instrucciones válidas


@pytest.mark.parametrize(
    "operacion", ["ENCENDER", "APAGAR", "ACTIVAR", "DESACTIVAR", "ABRIR", "CERRAR"]
)
def test_control(operacion):
    assert una(f"{operacion} dispositivo1") == Control(operacion, "dispositivo1")


def test_palabras_reservadas_en_minusculas():
    assert una("encender led1") == Control("ENCENDER", "led1")
    assert una("Listar Dispositivos") == Listar()


def test_el_identificador_conserva_mayusculas():
    assert una("ENCENDER LED1") == Control("ENCENDER", "LED1")


def test_consultar():
    assert una("CONSULTAR led1") == Consultar("led1")


def test_listar():
    assert una("LISTAR DISPOSITIVOS") == Listar()


@pytest.mark.parametrize("texto,valor", [("35", 35), ("-5", -5), ("22.5", 22.5)])
def test_establecer(texto, valor):
    assert una(f"ESTABLECER temp1 {texto}") == Establecer("temp1", valor)


def test_notificar():
    assert una('NOTIFICAR "Prueba"') == Notificar("Prueba")
    assert una("NOTIFICAR 'Prueba'") == Notificar("Prueba")
    assert una('NOTIFICAR ""') == Notificar("")


def test_enviar_correo():
    assert una(
        'ENVIAR CORREO A "usuario@ejemplo.com" MENSAJE "Hola, esta es una prueba"'
    ) == EnviarCorreo("usuario@ejemplo.com", "Hola, esta es una prueba")


# --------------------------------------------------------------- condicionales


def test_condicional_del_pdf():
    assert una("SI led1 == ENCENDIDO ENTONCES APAGAR led1") == Condicional(
        Condicion("led1", "==", Estado("ENCENDIDO")),
        Control("APAGAR", "led1"),
    )


def test_condicional_con_numero():
    assert una("SI temperatura > 30 ENTONCES ENCENDER ventilador1") == Condicional(
        Condicion("temperatura", ">", Numero(30)),
        Control("ENCENDER", "ventilador1"),
    )


@pytest.mark.parametrize("op", ["==", "!=", ">", "<", ">=", "<="])
def test_condicional_con_cada_operador(op):
    arbol = una(f"SI temp1 {op} 25.5 ENTONCES NOTIFICAR \"x\"")
    assert arbol.condicion.operador == op
    assert arbol.condicion.derecha == Numero(25.5)


def test_condicional_con_estado_negativo_y_distinto():
    assert una("SI alarma1 != DESACTIVADA ENTONCES NOTIFICAR \"Alarma activada\"") == Condicional(
        Condicion("alarma1", "!=", Estado("DESACTIVADA")),
        Notificar("Alarma activada"),
    )


@pytest.mark.parametrize(
    "accion_texto,accion",
    [
        ("CONSULTAR led1", Consultar("led1")),
        ("LISTAR DISPOSITIVOS", Listar()),
        ("ESTABLECER temp1 20", Establecer("temp1", 20)),
        ('NOTIFICAR "hola"', Notificar("hola")),
        ('ENVIAR CORREO A "a@b.com" MENSAJE "hola"', EnviarCorreo("a@b.com", "hola")),
        ("CERRAR puerta1", Control("CERRAR", "puerta1")),
    ],
)
def test_condicional_con_distintas_acciones(accion_texto, accion):
    assert una(f"SI temp1 > 30 ENTONCES {accion_texto}").accion == accion


def test_condicional_sin_espacios_en_el_operador():
    assert una("SI temp1>30 ENTONCES APAGAR led1").condicion.operador == ">"


# ---------------------------------------------------------------- programas


def test_programa_vacio():
    assert analizar("") == Programa(())


def test_programa_solo_comentarios_y_espacios():
    assert analizar("\n  \n# nada\n\n") == Programa(())


def test_secuencia_del_pdf():
    assert analizar("ENCENDER led1\nENCENDER led2\nDESACTIVAR alarma1") == Programa(
        (
            Control("ENCENDER", "led1"),
            Control("ENCENDER", "led2"),
            Control("DESACTIVAR", "alarma1"),
        )
    )


def test_ultima_linea_sin_enter_y_con_enter():
    assert analizar("ENCENDER led1") == analizar("ENCENDER led1\n")


def test_lineas_en_blanco_al_inicio_en_medio_y_al_final():
    assert analizar("\n\nENCENDER led1\n\n\nAPAGAR led1\n\n") == Programa(
        (Control("ENCENDER", "led1"), Control("APAGAR", "led1"))
    )


def test_crlf():
    assert analizar("ENCENDER led1\r\nAPAGAR led1\r\n") == Programa(
        (Control("ENCENDER", "led1"), Control("APAGAR", "led1"))
    )


def test_comentarios_entre_y_al_final_de_instrucciones():
    texto = "# encender\nENCENDER led1 # luz\n# apagar\nAPAGAR led1"
    assert analizar(texto) == Programa(
        (Control("ENCENDER", "led1"), Control("APAGAR", "led1"))
    )


def test_programa_mixto():
    texto = (
        "ESTABLECER temp1 35\n"
        "SI temp1 > 30 ENTONCES ENCENDER ventilador1\n"
        'NOTIFICAR "Listo"\n'
    )
    assert analizar(texto) == Programa(
        (
            Establecer("temp1", 35),
            Condicional(
                Condicion("temp1", ">", Numero(30)), Control("ENCENDER", "ventilador1")
            ),
            Notificar("Listo"),
        )
    )


def test_parsear_acepta_tokens_directamente():
    assert parsear(tokenizar("APAGAR led1")) == Programa((Control("APAGAR", "led1"),))


def test_parsear_exige_eof():
    with pytest.raises(ValueError):
        parsear([Token(TipoToken.SALTO_LINEA, "\n", 1, 1)])
    with pytest.raises(ValueError):
        parsear([])


# ---------------------------------------------------------------- posiciones


def test_posicion_del_programa_y_las_instrucciones():
    p = analizar("ENCENDER led1\n  APAGAR led2")
    assert (p.linea, p.columna) == (1, 1)
    a, b = p.instrucciones
    assert (a.linea, a.columna) == (1, 1)
    assert (b.linea, b.columna) == (2, 3)


def test_posiciones_dentro_del_condicional():
    c = una("SI temp1 > 30 ENTONCES ENCENDER ventilador1")
    assert (c.linea, c.columna) == (1, 1)
    assert (c.condicion.linea, c.condicion.columna) == (1, 4)
    assert (c.condicion.derecha.linea, c.condicion.derecha.columna) == (1, 12)
    assert (c.accion.linea, c.accion.columna) == (1, 24)


def test_posicion_de_cada_tipo_de_instruccion():
    p = analizar('LISTAR DISPOSITIVOS\nNOTIFICAR "x"\nENVIAR CORREO A "a" MENSAJE "b"')
    assert [(i.linea, i.columna) for i in p.instrucciones] == [(1, 1), (2, 1), (3, 1)]


# ---------------------------------------------------- errores sintácticos


def test_falta_identificador():
    e = error("ENCENDER")
    assert e.mensaje.startswith("se esperaba un identificador de dispositivo")
    assert (e.linea, e.columna) == (1, 9)
    assert str(e) == (
        "Error sintáctico: se esperaba un identificador de dispositivo "
        "y se encontró fin de línea (línea 1, col 9)"
    )


@pytest.mark.parametrize("comando", ["APAGAR", "ACTIVAR", "DESACTIVAR", "ABRIR", "CERRAR", "CONSULTAR"])
def test_falta_identificador_en_cada_comando(comando):
    assert "identificador de dispositivo" in error(comando).mensaje


def test_estado_no_sirve_como_identificador():
    e = error("ENCENDER ENCENDIDO")
    assert "identificador de dispositivo" in e.mensaje
    assert "'ENCENDIDO'" in e.mensaje
    assert (e.linea, e.columna) == (1, 10)


def test_numero_no_sirve_como_identificador():
    assert "'5'" in error("ENCENDER 5").mensaje


def test_texto_sobrante_despues_de_la_instruccion():
    e = error("APAGAR led1 led2")
    assert e.mensaje == "se esperaba fin de línea y se encontró 'led2'"
    assert (e.linea, e.columna) == (1, 13)


def test_dos_instrucciones_en_la_misma_linea():
    e = error("ENCENDER led1 APAGAR led2")
    assert e.mensaje == "se esperaba fin de línea y se encontró 'APAGAR'"


def test_texto_sobrante_despues_de_cadena():
    assert "la cadena" in error('NOTIFICAR "a" "b"').mensaje


def test_listar_sin_dispositivos():
    assert "'DISPOSITIVOS'" in error("LISTAR").mensaje
    assert "'led1'" in error("LISTAR led1").mensaje


def test_establecer_incompleto():
    assert "identificador de dispositivo" in error("ESTABLECER").mensaje
    assert "identificador de dispositivo" in error("ESTABLECER 5").mensaje
    assert "se esperaba un número" in error("ESTABLECER temp1").mensaje
    assert "se esperaba un número" in error("ESTABLECER temp1 ENCENDIDO").mensaje


def test_notificar_sin_cadena():
    assert "cadena de texto" in error("NOTIFICAR").mensaje
    assert "cadena de texto" in error("NOTIFICAR hola").mensaje
    assert "cadena de texto" in error("NOTIFICAR 5").mensaje


def test_correo_sin_mensaje():
    e = error('ENVIAR CORREO A "x"')
    assert e.mensaje == "se esperaba 'MENSAJE' y se encontró fin de línea"
    assert (e.linea, e.columna) == (1, 20)


def test_correo_sin_palabras_clave():
    assert "'CORREO'" in error('ENVIAR A "x" MENSAJE "y"').mensaje
    assert "se esperaba 'A'" in error('ENVIAR CORREO "x" MENSAJE "y"').mensaje
    assert "'MENSAJE'" in error('ENVIAR CORREO A "x" "y"').mensaje


def test_correo_con_destinatario_o_mensaje_sin_comillas():
    assert "destinatario" in error('ENVIAR CORREO A usuario MENSAJE "y"').mensaje
    assert "el mensaje" in error('ENVIAR CORREO A "x" MENSAJE hola').mensaje
    assert "el mensaje" in error('ENVIAR CORREO A "x" MENSAJE').mensaje


def test_condicional_sin_entonces():
    e = error("SI led1 == ENCENDIDO APAGAR led1")
    assert e.mensaje == "se esperaba 'ENTONCES' y se encontró 'APAGAR'"
    assert (e.linea, e.columna) == (1, 22)


def test_condicional_sin_condicion():
    assert "identificador de dispositivo" in error("SI").mensaje
    assert "identificador de dispositivo" in error("SI ENTONCES APAGAR led1").mensaje
    assert "identificador de dispositivo" in error("SI 5 > 3 ENTONCES APAGAR led1").mensaje


def test_condicional_sin_operador():
    e = error("SI led1 ENTONCES APAGAR led1")
    assert "operador de comparación" in e.mensaje
    assert "'ENTONCES'" in e.mensaje


def test_condicional_sin_valor():
    e = error("SI led1 == ENTONCES APAGAR led1")
    assert "un número o un estado" in e.mensaje
    assert "ENCENDIDO" in e.mensaje
    assert "'ENTONCES'" in e.mensaje


def test_condicional_con_valor_que_no_es_numero_ni_estado():
    assert "un número o un estado" in error("SI led1 == led2 ENTONCES APAGAR led1").mensaje


def test_condicional_sin_accion():
    e = error("SI led1 == ENCENDIDO ENTONCES")
    assert "una instrucción después de 'ENTONCES'" in e.mensaje
    assert "fin de línea" in e.mensaje


def test_condicional_con_accion_invalida():
    e = error("SI led1 == ENCENDIDO ENTONCES led1")
    assert "una instrucción después de 'ENTONCES'" in e.mensaje
    assert "'led1'" in e.mensaje


def test_condicional_anidado_no_permitido():
    e = error("SI led1 == ENCENDIDO ENTONCES SI led2 == APAGADO ENTONCES APAGAR led1")
    assert e.mensaje == "no se permite un SI dentro de otro SI"
    assert (e.linea, e.columna) == (1, 31)


def test_condicion_incompleta_al_final():
    assert "operador de comparación" in error("SI led1").mensaje
    assert "un número o un estado" in error("SI led1 ==").mensaje


@pytest.mark.parametrize("texto", ["led1 ENCENDER", "5", '"hola"', "ENTONCES", "==", "A"])
def test_linea_que_no_empieza_con_instruccion(texto):
    e = error(texto)
    assert e.mensaje.startswith("se esperaba una instrucción (ENCENDER")
    assert (e.linea, e.columna) == (1, 1)


def test_error_en_la_segunda_linea():
    e = error("ENCENDER led1\nAPAGAR")
    assert (e.linea, e.columna) == (2, 7)


def test_error_despues_de_lineas_en_blanco_y_comentarios():
    e = error("\n# nota\n\nENCENDER")
    assert (e.linea, e.columna) == (4, 9)


def test_se_detiene_en_el_primer_error():
    e = error("ENCENDER\nAPAGAR")
    assert e.linea == 1


def test_a_dict_del_error():
    assert error("ENCENDER").a_dict() == {
        "tipo": "Error sintáctico",
        "mensaje": "se esperaba un identificador de dispositivo y se encontró fin de línea",
        "linea": 1,
        "columna": 9,
    }


# --------------------------------------------- escenarios de la sección 16


def test_error_lexico_se_propaga_desde_analizar():
    with pytest.raises(ErrorLexico) as exc:
        analizar("ENCENDER led1@")
    assert "carácter '@' no reconocido" in exc.value.mensaje


def test_encender_sin_dispositivo_es_error_sintactico():
    assert isinstance(error("ENCENDER"), ErrorSintactico)


def test_errores_semanticos_pasan_el_parser():
    # Los rechaza la fase semántica, no el parser.
    assert una("ENCENDER dispositivo99") == Control("ENCENDER", "dispositivo99")
    assert una("ENCENDER alarma1") == Control("ENCENDER", "alarma1")
    assert una("ABRIR luz1") == Control("ABRIR", "luz1")
    assert una("SI temp1 > ENCENDIDO ENTONCES APAGAR led1").condicion.derecha == Estado(
        "ENCENDIDO"
    )


@pytest.mark.parametrize(
    "texto,tipo",
    [
        ("ENCENDER led1", Control),
        ("APAGAR led1", Control),
        ("ACTIVAR alarma1", Control),
        ("DESACTIVAR alarma1", Control),
        ("CONSULTAR led1", Consultar),
        ("LISTAR DISPOSITIVOS", Listar),
        ('NOTIFICAR "Prueba"', Notificar),
        ('ENVIAR CORREO A "usuario@ejemplo.com" MENSAJE "Hola"', EnviarCorreo),
        ("SI led1 == ENCENDIDO ENTONCES APAGAR led1", Condicional),
    ],
)
def test_catalogo_de_la_seccion_16(texto, tipo):
    assert isinstance(una(texto), tipo)
