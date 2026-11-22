"""Tabla de símbolos y reglas de compatibilidad de dispositivos."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

# Tipos alineados con V001__initial_schema.sql ('luz', 'ventilador', 'puerta', 'alarma')
# más 'ventana' y 'sensor_temperatura' definidos en el lenguaje.
OPERACIONES_POR_TIPO: dict[str, frozenset[str]] = {
    "luz": frozenset({"ENCENDER", "APAGAR", "CONSULTAR"}),
    "ventilador": frozenset({"ENCENDER", "APAGAR", "CONSULTAR"}),
    "puerta": frozenset({"ABRIR", "CERRAR", "CONSULTAR"}),
    "ventana": frozenset({"ABRIR", "CERRAR", "CONSULTAR"}),
    "alarma": frozenset({"ACTIVAR", "DESACTIVAR", "CONSULTAR"}),
    "sensor_temperatura": frozenset({"ESTABLECER", "CONSULTAR"}),
}

ESTADOS_POR_TIPO: dict[str, frozenset[str]] = {
    "luz": frozenset({"ENCENDIDO", "APAGADO"}),
    "ventilador": frozenset({"ENCENDIDO", "APAGADO"}),
    "puerta": frozenset({"ABIERTA", "CERRADA"}),
    "ventana": frozenset({"ABIERTA", "CERRADA"}),
    "alarma": frozenset({"ACTIVADA", "DESACTIVADA"}),
    "sensor_temperatura": frozenset(),  # Usa valores numéricos
}

# Catálogo exacto de backend/db/seeders/S001__initial_devices.sql + settings('temperature')
CATALOGO_SEED_SQL: tuple[dict[str, str], ...] = (
    {"id": "luz_sala", "tipo": "luz"},
    {"id": "luz_cocina", "tipo": "luz"},
    {"id": "ventilador1", "tipo": "ventilador"},
    {"id": "puerta_principal", "tipo": "puerta"},
    {"id": "alarma1", "tipo": "alarma"},
    {"id": "temperatura", "tipo": "sensor_temperatura"},
)


@dataclass(frozen=True)
class SimboloDispositivo:
    """Entrada de un dispositivo o sensor en la tabla de símbolos."""

    nombre: str
    tipo: str

    def __post_init__(self):
        if self.tipo not in OPERACIONES_POR_TIPO:
            raise ValueError(f"Tipo de dispositivo desconocido: {self.tipo!r}")

    @property
    def es_numerico(self) -> bool:
        return self.tipo == "sensor_temperatura"

    @property
    def operaciones_permitidas(self) -> frozenset[str]:
        return OPERACIONES_POR_TIPO[self.tipo]

    @property
    def estados_permitidos(self) -> frozenset[str]:
        return ESTADOS_POR_TIPO[self.tipo]


class TablaSimbolos:
    """Almacena los dispositivos registrados y consulta sus reglas semánticas."""

    def __init__(self, dispositivos: Optional[Iterable[SimboloDispositivo]] = None):
        self._simbolos: dict[str, SimboloDispositivo] = {}
        if dispositivos:
            for disp in dispositivos:
                self.registrar(disp)

    def registrar(self, simbolo: SimboloDispositivo) -> None:
        self._simbolos[simbolo.nombre] = simbolo

    def existe(self, nombre: str) -> bool:
        return nombre in self._simbolos

    def obtener(self, nombre: str) -> Optional[SimboloDispositivo]:
        return self._simbolos.get(nombre)

    def todos(self) -> list[SimboloDispositivo]:
        return list(self._simbolos.values())

    @classmethod
    def desde_lista_dicts(cls, registros: Iterable[dict]) -> TablaSimbolos:
        """Construye la tabla desde registros ({'id': ..., 'tipo'/'type': ...})."""
        simbolos = []
        for reg in registros:
            nombre = reg.get("id") or reg.get("nombre")
            tipo = reg.get("tipo") or reg.get("type")
            simbolos.append(SimboloDispositivo(nombre=nombre, tipo=tipo))
        return cls(simbolos)

    @classmethod
    def desde_sqlite(cls, ruta_db: str | Path) -> TablaSimbolos:
        """Carga los dispositivos y sensores directamente desde la BD SQLite del backend."""
        tabla = cls()
        with sqlite3.connect(ruta_db) as conn:
            filas = conn.execute("SELECT id, type FROM devices").fetchall()
            for dev_id, dev_type in filas:
                tabla.registrar(SimboloDispositivo(nombre=dev_id, tipo=dev_type))

            sensores = conn.execute("SELECT key FROM settings").fetchall()
            for (key,) in sensores:
                nombre = "temperatura" if key == "temperature" else key
                tabla.registrar(
                    SimboloDispositivo(nombre=nombre, tipo="sensor_temperatura")
                )
        return tabla

    @classmethod
    def por_defecto(cls) -> TablaSimbolos:
        """Crea la tabla con los dispositivos iniciales de S001__initial_devices.sql."""
        return cls.desde_lista_dicts(CATALOGO_SEED_SQL)