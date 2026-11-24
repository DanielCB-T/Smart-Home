"""Formato de tres direcciones del IR."""

from app.language.parser import analizar
from app.semantic import generar_ir
from app.semantic.tac import formatear_tac


def tac(texto):
    return formatear_tac(generar_ir(analizar(texto)))


def test_control_simple():
    assert tac("ENCENDER luz_sala") == ["luz_sala = ENCENDIDO"]


def test_apagar_y_abrir():
    assert tac("APAGAR luz_sala") == ["luz_sala = APAGADO"]
    assert tac("ABRIR puerta_principal") == ["puerta_principal = ABIERTA"]


def test_condicional_con_temporales_y_etiqueta():
    assert tac("SI temperatura > 30 ENTONCES ENCENDER ventilador1") == [
        "t1 = temperatura",
        "t2 = t1 > 30",
        "if_false t2 goto L1",
        "ventilador1 = ENCENDIDO",
        "L1:",
    ]


def test_condicional_sobre_estado():
    assert tac("SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala") == [
        "t1 = luz_sala",
        "t2 = t1 == ENCENDIDO",
        "if_false t2 goto L1",
        "luz_sala = APAGADO",
        "L1:",
    ]


def test_notificar_y_correo():
    assert tac('NOTIFICAR "Prueba"') == ['notify "Prueba"']
    assert tac('ENVIAR CORREO A "a@b.co" MENSAJE "Hola"') == ['send_email "a@b.co", "Hola"']


def test_establecer_sensor():
    assert tac("ESTABLECER temperatura 35") == ["temperatura = 35"]
