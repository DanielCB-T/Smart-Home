"""Pruebas del esqueleto de la máquina virtual (S1-18)."""

import pytest

from app.ejecucion.vm import OPERACIONES_IR, PASOS, MaquinaVirtual, OperacionDesconocida


def test_los_seis_pasos_estan_en_el_orden_del_proyecto():
    assert PASOS == (
        "identificar_operacion",
        "obtener_dispositivo",
        "validar_estado",
        "actualizar_estado",
        "guardar_resultado",
        "notificar_interfaz",
    )


def test_ejecutar_llama_los_seis_pasos_en_orden(monkeypatch):
    llamadas = []

    def registrar(nombre):
        def paso(self, contexto):
            llamadas.append(nombre)
            return contexto
        return paso

    for nombre in PASOS:
        monkeypatch.setattr(MaquinaVirtual, nombre, registrar(nombre))

    MaquinaVirtual().ejecutar({"op": "HALT"})
    assert llamadas == list(PASOS)


@pytest.mark.parametrize("operacion", sorted(OPERACIONES_IR))
def test_identifica_todas_las_operaciones_del_contrato(operacion):
    contexto = MaquinaVirtual().identificar_operacion({"instruccion": {"op": operacion}})
    assert contexto["operacion"] == operacion


def test_rechaza_operaciones_fuera_del_contrato():
    with pytest.raises(OperacionDesconocida):
        MaquinaVirtual().identificar_operacion({"instruccion": {"op": "MULTIPLY"}})


@pytest.mark.parametrize("paso", PASOS[1:])
def test_pasos_pendientes_indican_la_tarjeta(paso):
    with pytest.raises(NotImplementedError, match="S2-17"):
        getattr(MaquinaVirtual(), paso)({})
