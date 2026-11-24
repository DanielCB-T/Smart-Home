# ADR-001: Arquitectura en capas del pipeline de instrucciones

- **Estado:** aceptada
- **Fecha:** 23 de noviembre de 2026
- **Responsable:** P1 (líder técnico)

## Contexto

SmartHome debe reconocer instrucciones escritas por el usuario, validarlas, ejecutarlas y mostrar el resultado. El proyecto exige separar el procesamiento del lenguaje de la ejecución de acciones, para poder agregar comandos sin rediseñar el sistema.

## Decisión

El sistema se organiza en cuatro capas:

1. **Interfaz (frontend, React + TypeScript + Vite).** Envía texto y muestra respuestas. No interpreta nada.
2. **API (backend, FastAPI).** Recibe las solicitudes, coordina el análisis y la ejecución, y guarda el historial. Expone la documentación OpenAPI en `/docs`.
3. **Pipeline de lenguaje (Python).** Tres fases dentro del mismo proceso:
   - Léxica y sintáctica: `app/language/` (lexer, parser, AST).
   - Semántica: `app/semantic/` (tabla de símbolos, validador, construcción de instrucciones, IR y código de tres direcciones).
4. **Ejecución.** `app/servicios/ejecutor.py` aplica las instrucciones sobre la base de datos. `app/ejecucion/vm.py` define el esqueleto de la máquina virtual con sus seis pasos, que se implementará en S2-17.

## Flujo de una instrucción

1. La interfaz envía `POST /api/command` con el texto.
2. La API analiza el texto con el parser.
3. La tabla de símbolos se carga desde la base de datos, para que el análisis use los dispositivos reales.
4. El validador semántico comprueba existencia, compatibilidad y estados. Se detiene en el primer error.
5. Se construyen las instrucciones semánticas y el IR.
6. El ejecutor aplica las instrucciones en orden y registra el resultado en el historial.
7. La API devuelve el resultado, el AST, el IR y el estado completo del sistema.

## Consecuencias

- El análisis y la ejecución comparten la misma base de datos, así que no hay riesgo de que la validación use datos distintos de los que se modifican.
- Cada fase tiene su módulo y sus pruebas en `backend/tests/`.
- La ejecución de `CONSULTAR`, `LISTAR`, `NOTIFICAR` y `ENVIAR CORREO` está pendiente (S2-09, S2-10 y S2-18). Esas instrucciones se analizan completamente, pero la API responde que su ejecución aún no está implementada.
- La máquina virtual todavía no ejecuta el IR. Hoy el ejecutor interpreta directamente las instrucciones semánticas.
