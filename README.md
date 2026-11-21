# SmartHome

SmartHome es una aplicación web que simula la administración de una casa inteligente mediante instrucciones escritas. El usuario escribe comandos en una consola, el sistema los analiza, valida y ejecuta, y el panel de dispositivos muestra los cambios de estado en tiempo real. Los dispositivos son simulados, y el envío de notificaciones y correos se hace contra un servidor SMTP de pruebas (Mailpit).

Proyecto integrador de la asignatura Lenguajes y Autómatas II. Opción 1: SmartHome.

## Integrantes

| Nombre | GitHub | Rol principal | Módulo |
|---|---|---|---|
| Nombre P1 | @usuario | Líder técnico | Arquitectura, contratos, integración |
| Nombre P2 | @usuario | Frontend | Consola, panel, historial |
| Nombre P3 | @usuario | Backend | API, PostgreSQL, persistencia |
| Nombre P4 | @usuario | Lenguaje | Catálogo, lexer, parser, AST |
| Nombre P5 | @usuario | Semántico e IR | Tabla de símbolos, validaciones, IR |
| Nombre P6 | @usuario | Ejecución y DevOps | Optimizador, VM, SMTP, Docker |

## Requisitos

- Docker y Docker Compose.
- Git.

Para ejecutar sin contenedores también se necesita Python 3.11 o superior, Node.js 20 o superior y PostgreSQL 15 o superior. Esta vía no es la recomendada.

## Instalación y ejecución

Clona el repositorio, crea el archivo de variables de entorno y levanta los servicios:

```bash
git clone https://github.com/<organizacion>/smarthome.git
cd smarthome
cp .env.example .env
docker compose up --build
```

La primera vez, la construcción de las imágenes puede tardar varios minutos.

### Accesos

| Servicio | Dirección | Descripción |
|---|---|---|
| Aplicación web | http://localhost:5173 | Consola de instrucciones y panel de dispositivos |
| API (documentación) | http://localhost:8000/docs | Endpoints REST con ejemplos |
| Mailpit | http://localhost:8025 | Bandeja de correos de prueba |
| PostgreSQL | localhost:5432 | Base de datos (solo para depuración) |

El servidor SMTP de Mailpit escucha en `mailpit:1025` dentro de la red de Docker. Los correos enviados nunca salen a internet.

Para detener los servicios, ejecuta `docker compose down`. Para borrar también los datos de la base, usa `docker compose down -v`.

## Uso

Escribe una instrucción en la consola y presiona **Ejecutar**. La interfaz muestra el resultado de cada etapa: instrucción reconocida, validación, ejecución y mensaje final.

```
ENCENDER led1
APAGAR led1
ACTIVAR alarma1
DESACTIVAR alarma1
CONSULTAR led1
LISTAR DISPOSITIVOS
NOTIFICAR "Prueba"
ENVIAR CORREO A "usuario@ejemplo.com" MENSAJE "Hola, esta es una prueba"
SI led1 == ENCENDIDO ENTONCES APAGAR led1
```

Varias instrucciones pueden escribirse una por línea. Se ejecutan en orden.

### Dispositivos disponibles

| Identificador | Tipo | Estado inicial | Operaciones permitidas |
|---|---|---|---|
| led1 | LED | APAGADO | ENCENDER, APAGAR, CONSULTAR |
| led2 | LED | ENCENDIDO | ENCENDER, APAGAR, CONSULTAR |
| alarma1 | ALARMA | ACTIVADA | ACTIVAR, DESACTIVAR, CONSULTAR |
| ventilador1 | VENTILADOR | APAGADO | ENCENDER, APAGAR, CONSULTAR |

## Catálogo de comandos

| Comando | Sintaxis | Qué hace |
|---|---|---|
| ENCENDER | `ENCENDER <dispositivo>` | Enciende un LED o ventilador |
| APAGAR | `APAGAR <dispositivo>` | Apaga un LED o ventilador |
| ACTIVAR | `ACTIVAR <alarma>` | Activa una alarma |
| DESACTIVAR | `DESACTIVAR <alarma>` | Desactiva una alarma |
| CONSULTAR | `CONSULTAR <dispositivo>` | Muestra el estado actual de un dispositivo |
| LISTAR | `LISTAR DISPOSITIVOS` | Muestra todos los dispositivos y su estado |
| NOTIFICAR | `NOTIFICAR "<mensaje>"` | Registra una notificación en el historial |
| ENVIAR CORREO | `ENVIAR CORREO A "<correo>" MENSAJE "<texto>"` | Envía un correo al servidor SMTP de pruebas |
| SI ... ENTONCES | `SI <dispositivo> == <estado> ENTONCES <instrucción>` | Ejecuta la instrucción solo si la condición se cumple |

Si una instrucción es incorrecta, la consola muestra el tipo de error:

| Ejemplo | Tipo de error | Mensaje |
|---|---|---|
| `ENCENDER led1@` | Léxico | Carácter '@' no reconocido |
| `ENCENDER` | Sintáctico | Se esperaba un identificador de dispositivo |
| `ENCENDER dispositivo99` | Semántico | El dispositivo no existe |
| `ENCENDER alarma1` | Semántico | Las alarmas solo admiten ACTIVAR / DESACTIVAR |

## Arquitectura

El flujo de una instrucción tiene dos fases. En la primera, el pipeline de compilación analiza el texto y produce código intermedio. En la segunda, el ejecutor modifica el estado de los dispositivos o envía el correo.

```
Usuario → Frontend (React) → API (FastAPI) → Pipeline de compilación → Ejecutor
                                                  │                    │
                                  Léxico → Sintáctico → AST → Semántico → IR → Optimizador
                                                                          │
                                                        Dispositivos (PostgreSQL) / Correo (Mailpit)
```

El procesamiento del lenguaje y la ejecución de acciones están separados, de modo que se pueden agregar comandos nuevos sin rediseñar el sistema. La descripción completa de cada componente está en `docs/arquitectura/`.

## Estructura del repositorio

```
smarthome/
├── README.md               Este archivo
├── docker-compose.yml      Servicios: frontend, backend, postgres, mailpit
├── .env.example            Variables de entorno de ejemplo
├── contratos/              Esquema del AST, formato del IR y OpenAPI
├── backend/                API, pipeline de compilación, ejecutor y pruebas
│   ├── app/api/            Endpoints REST
│   ├── app/db/             Modelos, sesión, seed y migraciones
│   ├── app/compilador/     Lexer, parser, AST, semántica, IR y optimizador
│   ├── app/ejecucion/      Máquina virtual y cliente SMTP
│   └── tests/              Pruebas por módulo
├── frontend/               Consola, panel de dispositivos e historial
└── docs/                   Documentación técnica del proyecto
```

## Pruebas

Las pruebas del backend se ejecutan con pytest desde la carpeta `backend`:

```bash
docker compose run --rm backend pytest
```

Las pruebas del frontend:

```bash
docker compose run --rm frontend npm test
```

Los escenarios funcionales obligatorios del proyecto (sección 16) están descritos en `docs/pruebas.md`.

## Documentación

| Documento | Contenido |
|---|---|
| `docs/arquitectura/` | Arquitectura del sistema y decisiones de diseño (ADR) |
| `docs/lenguaje/` | Gramática EBNF, tokens, diseño del AST y errores |
| `docs/semantica/` | Tabla de símbolos y reglas semánticas |
| `docs/ir/` | Especificación de la representación intermedia |
| `docs/optimizaciones/` | Optimizaciones, precondiciones y justificación |
| `docs/ejecutor.md` | Funcionamiento de la máquina virtual |
| `docs/base_datos.md` | Modelo de datos |
| `docs/api.md` | Descripción de la API |
| `docs/instalacion.md` | Instalación detallada y solución de problemas |
| `docs/pruebas.md` | Pruebas y evidencia |
| `docs/demo/guion.md` | Guion de la demostración |

## Flujo de trabajo

El repositorio usa tres niveles de ramas: `main` (versión entregable), `develop` (integración) y `feature/<id>-<descripción>` (una por tarjeta del tablero). Por ejemplo, `feature/s1-10-lexer`.

Cada cambio entra por Pull Request hacia `develop` y requiere la aprobación de una persona distinta a su autor. Los commits siguen el formato `tipo(módulo): descripción`, por ejemplo `feat(parser): agrega producción de condicional`.

El tablero de tareas está en GitHub Projects, con las columnas Backlog, Ready, In progress, In review, Testing y Done.

## Solución de problemas

**El puerto 5173, 8000, 5432 o 8025 ya está en uso.** Cierra el programa que lo usa o cambia el puerto en `docker-compose.yml`.

**La API no conecta con PostgreSQL.** Espera unos segundos a que la base de datos termine de iniciar. Si persiste, revisa que los valores de `.env` coincidan con los del servicio `postgres`.

**No aparecen correos en Mailpit.** Verifica que el servicio `mailpit` esté activo con `docker compose ps` y que la variable `SMTP_HOST` apunte a `mailpit`.

**Cambios en el código no se reflejan.** Vuelve a construir las imágenes con `docker compose up --build`.

Si el problema no aparece aquí, abre un issue en GitHub con el mensaje de error completo y los pasos para reproducirlo.

## Licencia

Proyecto académico. Uso educativo.