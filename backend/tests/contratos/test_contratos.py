"""Verifica que el código cumple los contratos publicados en contratos/."""

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

from app.language.parser import analizar
from app.semantic import generar_ir

RAIZ = Path(__file__).resolve().parents[3]
CONTRATOS = RAIZ / "contratos"

EJEMPLOS = [
    "ENCENDER luz_sala",
    "APAGAR ventilador1",
    "ACTIVAR alarma1",
    "ABRIR puerta_principal",
    "CONSULTAR luz_sala",
    "LISTAR DISPOSITIVOS",
    "ESTABLECER temperatura 35",
    'NOTIFICAR "Prueba"',
    'ENVIAR CORREO A "usuario@ejemplo.com" MENSAJE "Hola"',
    "SI temperatura > 30 ENTONCES ENCENDER ventilador1",
    "SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala",
]

OPERACIONES_IR = {
    "SET_STATE", "GET_STATE", "COMPARE", "JUMP_IF_FALSE",
    "NOTIFY", "SEND_EMAIL", "LIST_DEVICES", "HALT",
}


@pytest.fixture(scope="module")
def esquema_ast():
    return json.loads((CONTRATOS / "ast.schema.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("texto", EJEMPLOS)
def test_ast_cumple_el_esquema(esquema_ast, texto):
    jsonschema.validate(analizar(texto).a_dict(), esquema_ast)


@pytest.mark.parametrize("texto", EJEMPLOS)
def test_ir_usa_solo_las_operaciones_del_contrato(texto):
    ir = generar_ir(analizar(texto))
    assert ir["version"] == "1.0"
    assert all(instr["op"] in OPERACIONES_IR for instr in ir["instrucciones"])


def test_ir_termina_con_halt():
    ir = generar_ir(analizar("ENCENDER luz_sala"))
    assert ir["instrucciones"][-1]["op"] == "HALT"


def test_openapi_es_yaml_valido_y_declara_los_endpoints():
    documento = yaml.safe_load((CONTRATOS / "openapi.yaml").read_text(encoding="utf-8"))
    rutas = set(documento["paths"])
    esperadas = {
        "/api/health", "/api/state", "/api/devices", "/api/devices/{dispositivo_id}",
        "/api/command", "/api/analyze", "/api/temperature", "/api/history",
    }
    assert esperadas <= rutas
