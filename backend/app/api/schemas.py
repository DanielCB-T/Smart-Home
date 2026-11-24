"""Modelos de entrada y salida de la API. Aparecen en la documentación OpenAPI (/docs)."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class Health(BaseModel):
    status: Literal["ok"] = "ok"
    version: str


class Dispositivo(BaseModel):
    id: str = Field(examples=["luz_sala"])
    name: str = Field(examples=["Luz de sala"])
    type: Literal["luz", "ventilador", "puerta", "alarma"]
    estado: str = Field(examples=["APAGADO"])
    on: Optional[bool] = None
    open: Optional[bool] = None


class Registro(BaseModel):
    id: int
    timestamp: str
    command: str
    message: str
    success: bool
    skipped: bool


class Estado(BaseModel):
    devices: list[Dispositivo]
    temperature: float
    history: list[Registro]


class Comando(BaseModel):
    command: str = Field(min_length=1, max_length=300, examples=["ENCENDER luz_sala"])


class AccionDispositivo(BaseModel):
    action: Literal["ENCENDER", "APAGAR", "ABRIR", "CERRAR", "ACTIVAR", "DESACTIVAR"]


class DispositivoEntrada(BaseModel):
    id: str = Field(min_length=1, max_length=40, examples=["luz_pasillo"])
    name: str = Field(min_length=1, max_length=60, examples=["Luz del pasillo"])
    type: Literal["luz", "ventilador", "puerta", "alarma"]


class Temperatura(BaseModel):
    temperature: float = Field(ge=-20, le=60, examples=[30])


class ErrorLenguajeModelo(BaseModel):
    tipo: str
    mensaje: str
    linea: int
    columna: int


class Analisis(BaseModel):
    ok: bool
    ast: Optional[dict] = None
    ir: Optional[dict] = None
    ir_tac: Optional[list[str]] = Field(default=None, description='IR en código de tres direcciones')
    error: Optional[ErrorLenguajeModelo] = None


class RespuestaComando(BaseModel):
    result: Registro
    analysis: Analisis
    devices: list[Dispositivo]
    temperature: float
    history: list[Registro]


class ErrorSimple(BaseModel):
    error: str
