"""Pruebas unitarias para el análisis semántico y la generación de IR."""

import pytest

from app.language.parser import analizar
from app.semantic import (
    ErrorSemantico,
    SimboloDispositivo,
    TablaSimbolos,
    analizar_y_construir,
    generar_ir,
    validar_semantica,
)


def tabla_pruebas() -> TablaSimbolos:
    tabla = TablaSimbolos.por_defecto()
    # Dispositivos extra usados en ejemplos del documento de lenguaje
    tabla.registrar(SimboloDispositivo("led1", "luz"))
    tabla.registrar(SimboloDispositivo("temp1", "sensor_temperatura"))
    tabla.registrar(SimboloDispositivo("ventana1", "ventana"))
    return tabla


def test_instrucciones_validas_pasan_semantica():
    codigo = """
    ENCENDER luz_sala
    APAGAR ventilador1
    ACTIVAR alarma1
    ABRIR puerta_principal
    CERRAR ventana1
    ESTABLECER temperatura 25
    CONSULTAR luz_sala
    LISTAR DISPOSITIVOS
    NOTIFICAR "Todo bien"
    ENVIAR CORREO A "usuario@ejemplo.com" MENSAJE "Alerta"
    SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala
    SI temperatura > 30 ENTONCES ENCENDER ventilador1
    """
    ast = analizar(codigo)
    validado = validar_semantica(ast, tabla_pruebas())
    assert validado == ast


def test_dispositivo_inexistente_lanza_error_semantico():
    ast = analizar("ENCENDER dispositivo99")
    with pytest.raises(ErrorSemantico) as exc:
        validar_semantica(ast, tabla_pruebas())
    assert exc.value.tipo == "Error semántico"
    assert "dispositivo99" in exc.value.mensaje
    assert exc.value.linea == 1


def test_sensibilidad_mayusculas_en_dispositivos():
    ast = analizar("ENCENDER LUZ_SALA")
    with pytest.raises(ErrorSemantico):
        validar_semantica(ast, tabla_pruebas())


def test_operacion_incompatible_con_tipo():
    with pytest.raises(ErrorSemantico):
        validar_semantica(analizar("ENCENDER alarma1"), tabla_pruebas())

    with pytest.raises(ErrorSemantico):
        validar_semantica(analizar("ABRIR luz_sala"), tabla_pruebas())

    with pytest.raises(ErrorSemantico):
        validar_semantica(analizar("ESTABLECER luz_sala 35"), tabla_pruebas())


def test_condicional_tipos_incompatibles():
    # Sensor numérico comparado con estado
    with pytest.raises(ErrorSemantico):
        validar_semantica(
            analizar("SI temperatura > ENCENDIDO ENTONCES APAGAR luz_sala"),
            tabla_pruebas(),
        )

    # Luz comparada con número
    with pytest.raises(ErrorSemantico):
        validar_semantica(
            analizar("SI luz_sala == 1 ENTONCES APAGAR luz_sala"),
            tabla_pruebas(),
        )

    # Luz comparada con estado de puerta
    with pytest.raises(ErrorSemantico):
        validar_semantica(
            analizar("SI luz_sala == ABIERTA ENTONCES APAGAR luz_sala"),
            tabla_pruebas(),
        )

    # Operador de orden en estado discreto
    with pytest.raises(ErrorSemantico):
        validar_semantica(
            analizar("SI luz_sala > ENCENDIDO ENTONCES APAGAR luz_sala"),
            tabla_pruebas(),
        )


def test_correo_invalido():
    with pytest.raises(ErrorSemantico):
        validar_semantica(
            analizar('ENVIAR CORREO A "correo-sin-arroba" MENSAJE "Hola"'),
            tabla_pruebas(),
        )


def test_construir_instruccion_y_generar_ir():
    ast = analizar("SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala")
    tabla = tabla_pruebas()
    instrucciones_sem = analizar_y_construir(ast, tabla)
    assert len(instrucciones_sem) == 1
    assert instrucciones_sem[0].tipo_accion == "CONDITIONAL"

    ir = generar_ir(ast)
    assert ir["version"] == "1.0"
    ops = [i["op"] for i in ir["instrucciones"]]
    assert ops == ["GET_STATE", "COMPARE", "JUMP_IF_FALSE", "SET_STATE", "HALT"]
    assert ir["instrucciones"][-1].get("etiqueta") == "L1"