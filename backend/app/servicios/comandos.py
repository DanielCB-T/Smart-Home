"""Pipeline completo de una instrucción: análisis, ejecución y registro en el historial."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from app.config import ruta_base_datos
from app.db import abrir, leer_dispositivos, leer_historial, leer_temperatura, registrar
from app.language.errors import ErrorLenguaje
from app.language.parser import analizar
from app.semantic import TablaSimbolos, analizar_y_construir, generar_ir

from .ejecutor import ErrorEjecucion, ejecutar_todas

LONGITUD_MAXIMA = 300


def normalizar(texto: str) -> str:
    return texto.strip()


def procesar(texto: str, ruta: Optional[Path] = None) -> tuple[int, dict]:
    """Analiza y ejecuta una instrucción. Devuelve (código HTTP, cuerpo de respuesta)."""
    comando = normalizar(texto)
    if not comando or len(comando) > LONGITUD_MAXIMA:
        return 400, {"error": f"El comando debe tener de 1 a {LONGITUD_MAXIMA} caracteres."}

    with abrir(ruta) as conexion:
        try:
            programa = analizar(comando)
            tabla = TablaSimbolos.desde_sqlite(_ruta_real(ruta))
            instrucciones = analizar_y_construir(programa, tabla)
            ir = generar_ir(programa)
        except ErrorLenguaje as error:
            resultado = registrar(conexion, comando, error.mensaje, False)
            return 422, _respuesta(conexion, resultado, {"ok": False, "error": error.a_dict()})

        analisis = {"ok": True, "ast": programa.a_dict(), "ir": ir}
        try:
            mensaje, omitida = ejecutar_todas(conexion, instrucciones)
        except ErrorEjecucion as error:
            resultado = registrar(conexion, comando, str(error), False)
            return 422, _respuesta(conexion, resultado, analisis)

        resultado = registrar(conexion, comando, mensaje, True, omitida)
        return 200, _respuesta(conexion, resultado, analisis)


def analizar_solo(texto: str, ruta: Optional[Path] = None) -> tuple[int, dict]:
    """Solo analiza, sin ejecutar ni registrar en el historial."""
    comando = normalizar(texto)
    if not comando or len(comando) > LONGITUD_MAXIMA:
        return 400, {"error": f"El comando debe tener de 1 a {LONGITUD_MAXIMA} caracteres."}
    try:
        programa = analizar(comando)
        tabla = TablaSimbolos.desde_sqlite(_ruta_real(ruta))
        analizar_y_construir(programa, tabla)
    except ErrorLenguaje as error:
        return 422, {"ok": False, "error": error.a_dict()}
    return 200, {"ok": True, "ast": programa.a_dict(), "ir": generar_ir(programa)}


def _respuesta(conexion, resultado: dict, analisis: dict) -> dict:
    return {
        "result": resultado,
        "analysis": analisis,
        "devices": leer_dispositivos(conexion),
        "temperature": leer_temperatura(conexion),
        "history": leer_historial(conexion),
    }


def _ruta_real(ruta: Optional[Path]) -> Path:
    return Path(ruta) if ruta else ruta_base_datos()
