"""Pruebas de la API FastAPI: flujos de la sección 16 del proyecto y casos de error."""

import pytest


def comando(cliente, texto):
    return cliente.post("/api/command", json={"command": texto})


def test_health(cliente):
    r = cliente.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_estado_inicial_tiene_dispositivos_y_temperatura(cliente):
    estado = cliente.get("/api/state").json()
    ids = {d["id"] for d in estado["devices"]}
    assert {"luz_sala", "luz_cocina", "ventilador1", "puerta_principal", "alarma1"} <= ids
    assert estado["temperature"] == 28


def test_encender_cambia_el_estado_del_dispositivo(cliente):
    r = comando(cliente, "ENCENDER luz_sala")
    assert r.status_code == 200
    assert r.json()["result"]["success"] is True
    luz = cliente.get("/api/devices/luz_sala").json()
    assert luz["on"] is True and luz["estado"] == "ENCENDIDO"


def test_apagar_despues_de_encender(cliente):
    comando(cliente, "ENCENDER luz_sala")
    r = comando(cliente, "APAGAR luz_sala")
    assert r.status_code == 200
    assert cliente.get("/api/devices/luz_sala").json()["on"] is False


def test_encender_un_dispositivo_ya_encendido_falla(cliente):
    comando(cliente, "ENCENDER luz_sala")
    r = comando(cliente, "ENCENDER luz_sala")
    assert r.status_code == 422
    assert "ya está ENCENDIDO" in r.json()["result"]["message"]


def test_activar_y_desactivar_alarma(cliente):
    # La alarma inicia DESACTIVADA: desactivarla de nuevo debe fallar.
    assert cliente.get("/api/devices/alarma1").json()["estado"] == "DESACTIVADA"
    assert comando(cliente, "DESACTIVAR alarma1").status_code == 422
    assert comando(cliente, "ACTIVAR alarma1").status_code == 200
    assert cliente.get("/api/devices/alarma1").json()["estado"] == "ACTIVADA"
    assert comando(cliente, "DESACTIVAR alarma1").status_code == 200


def test_abrir_puerta(cliente):
    r = comando(cliente, "ABRIR puerta_principal")
    assert r.status_code == 200
    assert cliente.get("/api/devices/puerta_principal").json()["open"] is True


def test_dispositivo_inexistente_es_error_semantico(cliente):
    r = comando(cliente, "ENCENDER dispositivo99")
    assert r.status_code == 422
    assert r.json()["analysis"]["error"]["tipo"] == "Error semántico"


def test_operacion_incompatible_es_error_semantico(cliente):
    r = comando(cliente, "ENCENDER alarma1")
    assert r.status_code == 422
    assert r.json()["analysis"]["error"]["tipo"] == "Error semántico"


def test_error_lexico(cliente):
    r = comando(cliente, "ENCENDER led1@")
    assert r.status_code == 422
    assert r.json()["analysis"]["error"]["tipo"] == "Error léxico"


def test_error_sintactico(cliente):
    r = comando(cliente, "ENCENDER")
    assert r.status_code == 422
    assert r.json()["analysis"]["error"]["tipo"] == "Error sintáctico"


def test_condicional_verdadera_ejecuta_la_accion(cliente):
    cliente.put("/api/temperature", json={"temperature": 35})
    r = comando(cliente, "SI temperatura > 30 ENTONCES ENCENDER ventilador1")
    assert r.status_code == 200
    assert r.json()["result"]["message"].startswith("Condición verdadera.")
    assert cliente.get("/api/devices/ventilador1").json()["on"] is True


def test_condicional_falsa_se_omite_sin_error(cliente):
    r = comando(cliente, "SI temperatura > 30 ENTONCES ENCENDER ventilador1")
    assert r.status_code == 200
    assert r.json()["result"]["skipped"] is True
    assert cliente.get("/api/devices/ventilador1").json()["on"] is False


def test_condicional_sobre_estado_de_dispositivo(cliente):
    # La luz inicia APAGADA: la condición es falsa y se omite.
    r = comando(cliente, "SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala")
    assert r.status_code == 200
    assert r.json()["result"]["skipped"] is True
    # Tras encenderla, la misma condición sí se cumple.
    comando(cliente, "ENCENDER luz_sala")
    r = comando(cliente, "SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala")
    assert r.status_code == 200
    assert r.json()["result"]["skipped"] is False
    assert cliente.get("/api/devices/luz_sala").json()["on"] is False


def test_notificar_es_valido_pero_pendiente(cliente):
    r = comando(cliente, 'NOTIFICAR "Prueba"')
    assert r.status_code == 422
    assert r.json()["analysis"]["ok"] is True
    assert "aún no tiene ejecución" in r.json()["result"]["message"]


def test_analyze_no_ejecuta_ni_registra(cliente):
    antes = len(cliente.get("/api/history").json())
    r = cliente.post("/api/analyze", json={"command": "ENCENDER luz_sala"})
    assert r.status_code == 200
    assert r.json()["ok"] is True
    assert "ir" in r.json()
    assert len(cliente.get("/api/history").json()) == antes
    assert cliente.get("/api/devices/luz_sala").json()["on"] is False


def test_comando_vacio_es_400(cliente):
    assert comando(cliente, "   ").status_code == 400


def test_temperatura_fuera_de_rango(cliente):
    assert cliente.put("/api/temperature", json={"temperature": 99}).status_code == 422


def test_temperatura_se_registra_en_historial(cliente):
    cliente.put("/api/temperature", json={"temperature": 25})
    historial = cliente.get("/api/history").json()
    assert historial[0]["command"] == "TEMPERATURA 25"


def test_patch_dispositivo(cliente):
    r = cliente.patch("/api/devices/luz_cocina", json={"action": "ENCENDER"})
    assert r.status_code == 200
    assert cliente.get("/api/devices/luz_cocina").json()["on"] is True


def test_patch_accion_invalida(cliente):
    assert cliente.patch("/api/devices/luz_cocina", json={"action": "EXPLOTAR"}).status_code == 422


def test_dispositivo_inexistente_404(cliente):
    assert cliente.get("/api/devices/nope").status_code == 404


def test_historial_respeta_el_limite(cliente):
    for _ in range(3):
        comando(cliente, "CONSULTAR luz_sala")
    assert len(cliente.get("/api/history?limit=2").json()) == 2


def test_historial_limite_invalido(cliente):
    assert cliente.get("/api/history?limit=0").status_code == 422


def test_persistencia_entre_clientes(tmp_path, monkeypatch):
    monkeypatch.setenv("SMART_HOME_DB", str(tmp_path / "persiste.sqlite"))
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as primero:
        primero.post("/api/command", json={"command": "ENCENDER luz_sala"})
    with TestClient(app) as segundo:
        assert segundo.get("/api/devices/luz_sala").json()["on"] is True


def test_documentacion_openapi_disponible(cliente):
    esquema = cliente.get("/openapi.json").json()
    assert "/api/command" in esquema["paths"]
    assert "/api/devices/{dispositivo_id}" in esquema["paths"]
