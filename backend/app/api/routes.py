"""Rutas de la API REST de SmartHome."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app import __version__
from app.db import (
    abrir,
    estado_completo,
    leer_dispositivos,
    leer_historial,
    leer_temperatura,
    registrar,
)
from app.servicios import dispositivos as servicio_dispositivos
from app.servicios.comandos import analizar_solo, procesar
from app.servicios.dispositivos import ErrorDispositivo

from .schemas import (
    AccionDispositivo,
    Analisis,
    Comando,
    Dispositivo,
    DispositivoEntrada,
    Estado,
    ErrorSimple,
    Health,
    Registro,
    RespuestaComando,
    Temperatura,
)

router = APIRouter(prefix="/api")

RESPUESTA_COMANDO = {
    200: {"model": RespuestaComando, "description": "Instrucción ejecutada"},
    422: {"model": RespuestaComando, "description": "Error léxico, sintáctico, semántico o de ejecución"},
    400: {"model": ErrorSimple, "description": "Solicitud inválida"},
}


def _cuerpo(codigo: int, cuerpo: dict) -> JSONResponse:
    return JSONResponse(status_code=codigo, content=cuerpo)


@router.get("/health", response_model=Health, tags=["Sistema"])
def salud() -> Health:
    return Health(version=__version__)


@router.get("/state", response_model=Estado, tags=["Estado"])
def estado() -> dict:
    return estado_completo()


@router.get("/devices", response_model=list[Dispositivo], tags=["Dispositivos"])
def dispositivos() -> list[dict]:
    with abrir() as conexion:
        return leer_dispositivos(conexion)


@router.get("/devices/{dispositivo_id}", response_model=Dispositivo, tags=["Dispositivos"],
            responses={404: {"model": ErrorSimple}})
def dispositivo(dispositivo_id: str) -> dict:
    with abrir() as conexion:
        for registro in leer_dispositivos(conexion):
            if registro["id"].lower() == dispositivo_id.lower():
                return registro
    raise HTTPException(status_code=404, detail=f'El dispositivo "{dispositivo_id}" no existe.')


@router.patch("/devices/{dispositivo_id}", response_model=RespuestaComando, tags=["Dispositivos"],
              responses=RESPUESTA_COMANDO,
              summary="Ejecuta una acción sobre un dispositivo")
def accion_dispositivo(dispositivo_id: str, cuerpo: AccionDispositivo) -> JSONResponse:
    codigo, respuesta = procesar(f"{cuerpo.action} {dispositivo_id}")
    return _cuerpo(codigo, respuesta)


@router.post("/command", response_model=RespuestaComando, tags=["Instrucciones"],
             responses=RESPUESTA_COMANDO,
             summary="Analiza y ejecuta una instrucción")
def ejecutar_comando(cuerpo: Comando) -> JSONResponse:
    codigo, respuesta = procesar(cuerpo.command)
    return _cuerpo(codigo, respuesta)


@router.post("/analyze", response_model=Analisis, tags=["Instrucciones"],
             responses={422: {"model": Analisis}, 400: {"model": ErrorSimple}},
             summary="Analiza una instrucción sin ejecutarla")
def analizar(cuerpo: Comando) -> JSONResponse:
    codigo, respuesta = analizar_solo(cuerpo.command)
    return _cuerpo(codigo, respuesta)


def _traducir(error: ErrorDispositivo) -> HTTPException:
    return HTTPException(status_code=error.codigo, detail=error.mensaje)


@router.post("/devices", response_model=Estado, status_code=201, tags=["Dispositivos"],
             responses={409: {"model": ErrorSimple}, 422: {"model": ErrorSimple}},
             summary="Registra un dispositivo nuevo")
def crear_dispositivo(cuerpo: DispositivoEntrada) -> dict:
    try:
        return servicio_dispositivos.crear(cuerpo.id, cuerpo.name, cuerpo.type)
    except ErrorDispositivo as error:
        raise _traducir(error) from error


@router.put("/devices/{dispositivo_id}", response_model=Estado, tags=["Dispositivos"],
            responses={404: {"model": ErrorSimple}, 409: {"model": ErrorSimple}, 422: {"model": ErrorSimple}},
            summary="Edita un dispositivo existente")
def editar_dispositivo(dispositivo_id: str, cuerpo: DispositivoEntrada) -> dict:
    try:
        return servicio_dispositivos.actualizar(dispositivo_id, cuerpo.id, cuerpo.name, cuerpo.type)
    except ErrorDispositivo as error:
        raise _traducir(error) from error


@router.delete("/devices/{dispositivo_id}", response_model=Estado, tags=["Dispositivos"],
               responses={404: {"model": ErrorSimple}}, summary="Elimina un dispositivo")
def eliminar_dispositivo(dispositivo_id: str) -> dict:
    try:
        return servicio_dispositivos.eliminar(dispositivo_id)
    except ErrorDispositivo as error:
        raise _traducir(error) from error


@router.get("/temperature", response_model=Temperatura, tags=["Sensor"])
def leer_temp() -> dict:
    with abrir() as conexion:
        return {"temperature": leer_temperatura(conexion)}


@router.put("/temperature", response_model=Estado, tags=["Sensor"])
def fijar_temperatura(cuerpo: Temperatura) -> dict:
    with abrir() as conexion:
        conexion.execute(
            "UPDATE settings SET value = ? WHERE key = 'temperature'", (cuerpo.temperature,)
        )
        registrar(
            conexion,
            f"TEMPERATURA {cuerpo.temperature:g}",
            f"Temperatura ajustada a {cuerpo.temperature:g} °C.",
            True,
        )
    return estado_completo()


@router.get("/history", response_model=list[Registro], tags=["Historial"])
def historial(limit: int = Query(100, ge=1, le=100)) -> list[dict]:
    with abrir() as conexion:
        return leer_historial(conexion, limit)
