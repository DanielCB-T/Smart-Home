from dataclasses import FrozenInstanceError

import pytest

from app.language.ast_nodes import (
    ESTADOS,
    OPERACIONES_CONTROL,
    OPERADORES_COMPARACION,
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


# ------------------------------------------------------------- construcción


def test_control():
    n = Control("ENCENDER", "led1", linea=2, columna=5)
    assert (n.operacion, n.dispositivo, n.linea, n.columna) == ("ENCENDER", "led1", 2, 5)


def test_control_acepta_argumentos_con_nombre():
    assert Control(operacion="APAGAR", dispositivo="led1").operacion == "APAGAR"


def test_posicion_por_defecto():
    n = Consultar("led1")
    assert (n.linea, n.columna) == (0, 0)


def test_listar_sin_campos():
    assert Listar(linea=1, columna=1).a_dict() == {"tipo": "Listar", "linea": 1, "columna": 1}


def test_establecer_con_entero_y_decimal():
    assert Establecer("temp1", 35).valor == 35
    assert Establecer("temp1", 22.5).valor == 22.5


def test_notificar_y_correo():
    assert Notificar("hola").mensaje == "hola"
    c = EnviarCorreo("a@b.com", "texto")
    assert (c.destinatario, c.mensaje) == ("a@b.com", "texto")


# ---------------------------------------------------------------- igualdad


def test_igualdad_ignora_la_posicion():
    assert Control("ENCENDER", "led1", linea=1, columna=1) == Control(
        "ENCENDER", "led1", linea=9, columna=9
    )


def test_igualdad_distingue_estructura():
    assert Control("ENCENDER", "led1") != Control("APAGAR", "led1")
    assert Control("ENCENDER", "led1") != Control("ENCENDER", "led2")
    assert Consultar("led1") != Control("ENCENDER", "led1")


def test_programas_iguales_con_distinta_posicion():
    a = Programa((Control("ENCENDER", "led1", linea=1, columna=1),))
    b = Programa((Control("ENCENDER", "led1", linea=4, columna=7),))
    assert a == b


# ----------------------------------------------------------- validaciones


@pytest.mark.parametrize("op", OPERACIONES_CONTROL)
def test_operaciones_de_control_validas(op):
    assert Control(op, "x").operacion == op


@pytest.mark.parametrize("op", ["CONSULTAR", "encender", "", "SALTAR"])
def test_operacion_de_control_invalida(op):
    with pytest.raises(ValueError):
        Control(op, "led1")


@pytest.mark.parametrize("op", ["==", "!=", ">", "<", ">=", "<="])
def test_operadores_validos(op):
    assert op in OPERADORES_COMPARACION
    assert Condicion("temp1", op, Numero(30)).operador == op


@pytest.mark.parametrize("op", ["=", "!", "=>", "IGUAL"])
def test_operador_invalido(op):
    with pytest.raises(ValueError):
        Condicion("temp1", op, Numero(30))


def test_conjuntos_de_valores():
    assert set(ESTADOS) == {
        "ENCENDIDO", "APAGADO", "ACTIVADA", "DESACTIVADA", "ABIERTA", "CERRADA",
    }  # fmt: skip
    assert set(OPERADORES_COMPARACION) == {"==", "!=", ">", "<", ">=", "<="}


@pytest.mark.parametrize("estado", ESTADOS)
def test_estados_validos(estado):
    assert Estado(estado).valor == estado


def test_estado_invalido():
    with pytest.raises(ValueError):
        Estado("ENCENDIDA")


# ----------------------------------------------------------- inmutabilidad


def test_nodos_son_inmutables():
    n = Control("ENCENDER", "led1")
    with pytest.raises(FrozenInstanceError):
        n.dispositivo = "led2"


# ----------------------------------------------------------------- a_dict


def test_a_dict_control():
    assert Control("ENCENDER", "led1", linea=1, columna=1).a_dict() == {
        "tipo": "Control",
        "operacion": "ENCENDER",
        "dispositivo": "led1",
        "linea": 1,
        "columna": 1,
    }


def test_a_dict_condicional_del_pdf():
    # SI led1 == ENCENDIDO ENTONCES APAGAR led1
    arbol = Condicional(
        condicion=Condicion("led1", "==", Estado("ENCENDIDO", linea=1, columna=11), linea=1, columna=4),
        accion=Control("APAGAR", "led1", linea=1, columna=29),
        linea=1,
        columna=1,
    )
    assert arbol.a_dict() == {
        "tipo": "Condicional",
        "condicion": {
            "tipo": "Condicion",
            "izquierda": "led1",
            "operador": "==",
            "derecha": {"tipo": "Estado", "valor": "ENCENDIDO", "linea": 1, "columna": 11},
            "linea": 1,
            "columna": 4,
        },
        "accion": {
            "tipo": "Control",
            "operacion": "APAGAR",
            "dispositivo": "led1",
            "linea": 1,
            "columna": 29,
        },
        "linea": 1,
        "columna": 1,
    }


def test_a_dict_programa_serializa_la_secuencia_como_lista():
    p = Programa((Control("ENCENDER", "led1"), Listar()))
    d = p.a_dict()
    assert d["tipo"] == "Programa"
    assert isinstance(d["instrucciones"], list)
    assert [i["tipo"] for i in d["instrucciones"]] == ["Control", "Listar"]


def test_a_dict_programa_vacio():
    assert Programa(()).a_dict()["instrucciones"] == []


def test_a_dict_es_serializable_a_json():
    import json

    p = Programa(
        (
            Establecer("temp1", 35),
            Condicional(
                Condicion("temp1", ">", Numero(30)),
                Control("ENCENDER", "ventilador1"),
            ),
            EnviarCorreo("a@b.com", "hola"),
        )
    )
    assert json.loads(json.dumps(p.a_dict()))["instrucciones"][1]["condicion"]["derecha"] == {
        "tipo": "Numero",
        "valor": 30,
        "linea": 0,
        "columna": 0,
    }
