# SmartHome

SmartHome es una plataforma web que simula la administración de una casa inteligente mediante instrucciones escritas. El usuario escribe comandos en una consola; el sistema los analiza (léxico, sintáctico y semántico), los convierte en representación intermedia, los ejecuta sobre dispositivos simulados y guarda el historial.

Proyecto integrador de Lenguajes y Autómatas II. Opción 1: SmartHome.

## Stack

| Capa | Tecnología |
|---|---|
| API | FastAPI + Uvicorn (Python 3.12) |
| Lenguaje (léxico, sintaxis, semántica, IR) | Python, módulos `app/language` y `app/semantic` |
| Persistencia | SQLite (módulo `sqlite3`), migraciones SQL en `backend/db/` |
| Interfaz | React 19 + TypeScript + Vite |
| Correo de pruebas | Mailpit (reservado para la tarjeta S2-18) |
| Contenedores | Docker Compose |

## Documentación interactiva de la API

Con el backend en ejecución:

- Swagger UI: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc
- Esquema OpenAPI: http://localhost:3001/openapi.json

## Ejecución local (sin Docker)

Requisitos: Python 3.11 o superior, Node.js 20 o superior y npm.

### 1. API

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 3001
```

Al iniciar, la API crea la base de datos en `backend/data/smarthome.sqlite`, aplica las migraciones y carga los dispositivos iniciales. Para usar otra ruta, define `SMART_HOME_DB`.

### 2. Interfaz

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

Abre http://localhost:5173. Vite redirige las peticiones `/api` a `http://localhost:3001`.

## Ejecución con Docker

```bash
cp .env.example .env
docker compose up --build
```

| Servicio | Dirección |
|---|---|
| Interfaz | http://localhost:5173 |
| API y documentación | http://localhost:3001/docs |
| Mailpit | http://localhost:8025 |

Detener: `docker compose down`. Borrar también la base de datos: `docker compose down -v`.

## Pruebas

### Backend (pytest)

Desde la carpeta `backend`, con el entorno virtual activo:

```bash
python -m pytest -q                       # todas las pruebas
python -m pytest -q tests/api             # solo la API
python -m pytest -q tests/language        # léxico, sintaxis y AST
python -m pytest -q tests/semantic        # tabla de símbolos, validación e IR
python -m pytest -v tests/api -k condicional   # un grupo de pruebas
```

Con Docker, sin instalar nada localmente:

```bash
docker compose run --rm --no-deps --entrypoint python backend -m pip install -q -r requirements-dev.txt
docker compose run --rm --no-deps --entrypoint python backend -m pytest -q
```

### Frontend (compilación)

```bash
cd frontend
npm run build      # verifica TypeScript y genera dist/
```

### Pruebas manuales de la API

Con la API en `http://localhost:3001`:

```bash
# Salud del servicio
curl http://localhost:3001/api/health

# Estado completo: dispositivos, temperatura e historial
curl http://localhost:3001/api/state

# Ejecutar una instrucción
curl -X POST http://localhost:3001/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "ENCENDER luz_sala"}'

# Analizar sin ejecutar
curl -X POST http://localhost:3001/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"command": "SI temperatura > 30 ENTONCES ENCENDER ventilador1"}'

# Cambiar la temperatura y luego probar la condición
curl -X PUT http://localhost:3001/api/temperature \
  -H "Content-Type: application/json" \
  -d '{"temperature": 35}'

# Acción directa sobre un dispositivo
curl -X PATCH http://localhost:3001/api/devices/alarma1 \
  -H "Content-Type: application/json" \
  -d '{"action": "ACTIVAR"}'

# Historial (los 5 más recientes)
curl "http://localhost:3001/api/history?limit=5"
```

### Casos de prueba funcionales

Ejecuta estas instrucciones en la consola o con `POST /api/command`, en este orden:

| Instrucción | Resultado esperado |
|---|---|
| `ENCENDER luz_sala` | 200, la luz queda ENCENDIDO |
| `ENCENDER luz_sala` | 422, ya está ENCENDIDO |
| `APAGAR luz_sala` | 200, la luz queda APAGADO |
| `ACTIVAR alarma1` | 200, la alarma queda ACTIVADA |
| `DESACTIVAR alarma1` | 200, la alarma queda DESACTIVADA |
| `ABRIR puerta_principal` | 200, la puerta queda ABIERTA |
| `ENCENDER dispositivo99` | 422, error semántico: no existe |
| `ENCENDER alarma1` | 422, error semántico: operación incompatible |
| `ENCENDER led1@` | 422, error léxico: carácter '@' no reconocido |
| `ENCENDER` | 422, error sintáctico: falta el identificador |
| `SI temperatura > 30 ENTONCES ENCENDER ventilador1` | 200, condición falsa (temperatura 28 °C) |
| Después de `PUT /api/temperature` con `{"temperature": 35}`, repite `SI temperatura > 30 ENTONCES ENCENDER ventilador1` | 200, el ventilador se enciende |
| `SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala` | 200, se ejecuta solo si la luz está encendida |
| `NOTIFICAR "Prueba"` | 422, sintaxis válida; ejecución pendiente (S2-10) |

## Gestión de dispositivos

Desde la interfaz, el botón **Nuevo dispositivo** (o la tarjeta punteada) abre un modal para registrar un dispositivo. El lápiz edita y el icono de papelera elimina, con confirmación. Cada alta, edición y baja se registra en el historial y se muestra con una alerta de SweetAlert2.

Reglas de los identificadores: empiezan con letra o guion bajo, usan solo letras, números y guion bajo (máximo 40), no pueden ser palabras reservadas del lenguaje (ENCENDER, SI, ENTONCES, etc.) ni repetir otro identificador, sin distinguir mayúsculas.

Endpoints correspondientes:

| Método | Ruta | Uso |
|---|---|---|
| POST | `/api/devices` | Registrar (201) |
| PUT | `/api/devices/{id}` | Editar nombre, identificador o categoría |
| DELETE | `/api/devices/{id}` | Eliminar |

Ejemplo en PowerShell:

```powershell
Invoke-RestMethod -Method Post http://localhost:3001/api/devices -ContentType "application/json" `
  -Body '{"id":"luz_pasillo","name":"Luz del pasillo","type":"luz"}'
Invoke-RestMethod -Method Delete http://localhost:3001/api/devices/luz_pasillo
```

## Tema claro y oscuro

El botón de la barra superior alterna entre modo claro y oscuro. La preferencia se guarda en el navegador; la primera vez sigue la configuración del sistema.

## Árbol AST e IR

El panel **Árbol sintáctico abstracto** muestra el AST de la última instrucción analizada, con tres vistas: árbol gráfico, IR (instrucciones intermedias) y JSON del AST.

## Dispositivos iniciales

| Identificador | Tipo | Estado inicial | Operaciones |
|---|---|---|---|
| luz_sala | luz | APAGADO | ENCENDER, APAGAR |
| luz_cocina | luz | APAGADO | ENCENDER, APAGAR |
| ventilador1 | ventilador | APAGADO | ENCENDER, APAGAR |
| puerta_principal | puerta | CERRADA | ABRIR, CERRAR |
| alarma1 | alarma | DESACTIVADA | ACTIVAR, DESACTIVAR |

El sensor de temperatura (28 °C) se consulta y modifica con `/api/temperature`. Las condiciones `SI` lo usan como `temperatura`.

## Estructura del repositorio

```
backend/
├── app/
│   ├── main.py              Aplicación FastAPI y ciclo de vida
│   ├── config.py            Configuración desde el entorno
│   ├── db.py                SQLite: conexión, migraciones, consultas
│   ├── api/                 Rutas y esquemas HTTP
│   ├── servicios/           Pipeline de comandos y ejecutor
│   ├── language/            Lexer, parser, AST
│   └── semantic/            Tabla de símbolos, validador, IR
├── db/                      Migraciones y semillas SQL
├── tests/                   Pruebas de API, lenguaje y semántica
├── requirements.txt
└── Dockerfile
frontend/
├── src/
│   ├── App.tsx              Estructura de la página y estado
│   ├── api.ts               Cliente HTTP
│   ├── components/          Tarjetas, consola, resultado, historial
│   └── styles.css
└── Dockerfile
docs/                        Documentación técnica
docker-compose.yml
```

## Solución de problemas

**`ModuleNotFoundError: No module named 'app'`.** Ejecuta los comandos desde la carpeta `backend`.

**La interfaz muestra "Sin conexión".** Revisa que la API responda en http://localhost:3001/api/health.

**Puerto en uso.** Cierra el proceso que lo usa o cambia el puerto en el comando de Uvicorn o en `.env`.

**Quiero reiniciar los datos.** Borra `backend/data/smarthome.sqlite`; se vuelve a crear al iniciar la API.

## Flujo de trabajo

Ramas: `main`, `develop` y `feature/<id>-<descripción>`. Cada cambio entra por Pull Request con la aprobación de otra persona. Commits con formato `tipo(módulo): descripción`.
