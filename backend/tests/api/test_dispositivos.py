"""Alta, edición y baja de dispositivos desde la API."""


def nuevo(cliente, id_="luz_pasillo", nombre="Luz del pasillo", tipo="luz"):
    return cliente.post("/api/devices", json={"id": id_, "name": nombre, "type": tipo})


def test_crear_dispositivo(cliente):
    r = nuevo(cliente)
    assert r.status_code == 201
    ids = [d["id"] for d in r.json()["devices"]]
    assert "luz_pasillo" in ids
    assert cliente.get("/api/devices/luz_pasillo").json()["estado"] == "APAGADO"


def test_crear_registra_historial(cliente):
    nuevo(cliente)
    assert cliente.get("/api/history").json()[0]["command"] == "SYM_DECL luz_pasillo"


def test_crear_duplicado_sin_distinguir_mayusculas(cliente):
    nuevo(cliente)
    r = nuevo(cliente, id_="LUZ_PASILLO")
    assert r.status_code == 409


def test_crear_palabra_reservada_es_rechazado(cliente):
    r = nuevo(cliente, id_="encender")
    assert r.status_code == 422
    assert "palabra reservada" in r.json()["detail"]


def test_crear_temperatura_es_rechazado(cliente):
    assert nuevo(cliente, id_="temperatura").status_code == 422


def test_identificador_con_formato_invalido(cliente):
    assert nuevo(cliente, id_="1luz").status_code == 422
    assert nuevo(cliente, id_="luz-sala").status_code == 422
    assert nuevo(cliente, id_="luz sala").status_code == 422


def test_tipo_invalido(cliente):
    assert nuevo(cliente, tipo="horno").status_code == 422


def test_nombre_vacio(cliente):
    assert nuevo(cliente, nombre="   ").status_code == 422


def test_el_dispositivo_creado_se_puede_controlar(cliente):
    nuevo(cliente)
    r = cliente.post("/api/command", json={"command": "ENCENDER luz_pasillo"})
    assert r.status_code == 200


def test_editar_nombre(cliente):
    nuevo(cliente)
    r = cliente.put("/api/devices/luz_pasillo", json={"id": "luz_pasillo", "name": "Luz principal", "type": "luz"})
    assert r.status_code == 200
    assert cliente.get("/api/devices/luz_pasillo").json()["name"] == "Luz principal"


def test_renombrar_y_comando_usa_el_nuevo_id(cliente):
    nuevo(cliente)
    r = cliente.put("/api/devices/luz_pasillo", json={"id": "luz_techo", "name": "Luz de techo", "type": "luz"})
    assert r.status_code == 200
    assert cliente.get("/api/devices/luz_pasillo").status_code == 404
    assert cliente.post("/api/command", json={"command": "ENCENDER luz_techo"}).status_code == 200
    assert cliente.post("/api/command", json={"command": "ENCENDER luz_pasillo"}).status_code == 422


def test_editar_conserva_el_estado(cliente):
    nuevo(cliente)
    cliente.post("/api/command", json={"command": "ENCENDER luz_pasillo"})
    cliente.put("/api/devices/luz_pasillo", json={"id": "luz_pasillo", "name": "Otra", "type": "luz"})
    assert cliente.get("/api/devices/luz_pasillo").json()["on"] is True


def test_editar_a_un_id_existente_es_conflicto(cliente):
    r = cliente.put("/api/devices/luz_sala", json={"id": "luz_cocina", "name": "X", "type": "luz"})
    assert r.status_code == 409


def test_editar_inexistente_404(cliente):
    r = cliente.put("/api/devices/fantasma", json={"id": "fantasma", "name": "X", "type": "luz"})
    assert r.status_code == 404


def test_eliminar_dispositivo(cliente):
    nuevo(cliente)
    r = cliente.delete("/api/devices/luz_pasillo")
    assert r.status_code == 200
    assert "luz_pasillo" not in [d["id"] for d in r.json()["devices"]]
    assert cliente.post("/api/command", json={"command": "ENCENDER luz_pasillo"}).status_code == 422


def test_eliminar_inexistente_404(cliente):
    assert cliente.delete("/api/devices/fantasma").status_code == 404


def test_editar_y_eliminar_quedan_en_historial(cliente):
    nuevo(cliente)
    cliente.put("/api/devices/luz_pasillo", json={"id": "luz_pasillo", "name": "B", "type": "luz"})
    cliente.delete("/api/devices/luz_pasillo")
    comandos = [h["command"] for h in cliente.get("/api/history").json()]
    assert "SYM_DELETE luz_pasillo" in comandos
    assert "SYM_UPDATE luz_pasillo" in comandos
