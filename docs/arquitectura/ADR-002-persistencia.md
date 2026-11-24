# ADR-002: Stack de backend (FastAPI) y persistencia con SQLite

- **Estado:** aceptada (reemplaza la versión con Node.js y el puente JSON)
- **Fecha:** 23 de noviembre de 2026
- **Responsable:** P3 (backend), revisado por P1

## Contexto

El documento del proyecto recomienda FastAPI y PostgreSQL, y permite usar tecnologías equivalentes si el equipo las justifica. Durante el Sprint 1 la API estaba escrita en Node.js, y el análisis en Python se conectaba mediante un proceso hijo y JSON. Esa separación hacía difícil mantener la tabla de símbolos sincronizada con la base de datos, y dos lenguajes en el backend complicaban las pruebas y el contenedor Docker.

## Decisión

- La API se escribe en **FastAPI** (Python 3.12), con Uvicorn como servidor.
- La persistencia usa **SQLite** con el módulo `sqlite3` de la biblioteca estándar.
- Las migraciones y semillas son archivos SQL en `backend/db/`. Se aplican al iniciar la API mediante `app/db.py`, y el control de migraciones aplicadas se guarda en la tabla `schema_migrations`.
- Se elimina la API Node.js y el puente JSON.

## Motivos

1. **Un solo lenguaje en el backend.** El análisis, la validación, la ejecución y la API corren en el mismo proceso, lo que simplifica las pruebas y el despliegue.
2. **Documentación automática.** FastAPI genera el contrato OpenAPI, que se exporta a `contratos/openapi.yaml`. Una prueba verifica que el contrato publicado coincida con el código.
3. **Persistencia sin servicios adicionales.** SQLite se guarda en un volumen de Docker, sin necesidad de un servidor de base de datos.
4. **Alcance.** PostgreSQL aporta concurrencia y escalabilidad que este proyecto no necesita, y su configuración agregaría tiempo a un calendario ajustado.

## Consecuencias

- `docker-compose.yml` no incluye PostgreSQL. La tarjeta S1-16 se cumple con los servicios de backend, frontend y Mailpit.
- Si el equipo decide migrar a PostgreSQL, el cambio afecta a `app/db.py`, a las migraciones y a las consultas, pero no a los módulos de lenguaje.
- SQLite admite una escritura a la vez. Para una casa simulada con un solo usuario, esto no limita el uso.
