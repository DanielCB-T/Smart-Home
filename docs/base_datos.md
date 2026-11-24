# Modelo de datos

La persistencia usa SQLite (ver ADR-002), accedida con el módulo `sqlite3` de Python. El esquema se crea con las migraciones de `backend/db/migrations/` y los datos iniciales se cargan con las semillas de `backend/db/seeders/`.

## Tablas

### devices

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id | TEXT | PRIMARY KEY | Identificador del dispositivo, por ejemplo `luz_sala`. |
| name | TEXT | NOT NULL | Nombre para mostrar. |
| type | TEXT | NOT NULL, CHECK en (luz, ventilador, puerta, alarma) | Tipo del dispositivo. |
| enabled | INTEGER | NOT NULL, DEFAULT 0, CHECK en (0, 1) | Estado: 1 encendido, activo o abierto; 0 apagado, inactivo o cerrado. |

### settings

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| key | TEXT | PRIMARY KEY | Nombre del parámetro. Hoy solo existe `temperature`. |
| value | REAL | NOT NULL | Valor del parámetro. |

### history

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Número de registro. |
| timestamp | TEXT | NOT NULL | Fecha y hora en formato ISO 8601. |
| command | TEXT | NOT NULL | Instrucción escrita por el usuario. |
| message | TEXT | NOT NULL | Resultado o mensaje de error. |
| success | INTEGER | NOT NULL, CHECK en (0, 1) | 1 si la instrucción se ejecutó. |
| skipped | INTEGER | NOT NULL, DEFAULT 0, CHECK en (0, 1) | 1 si una condición fue falsa y no hubo acción. |

Índice: `idx_history_timestamp` sobre `history(timestamp DESC)`.

### schema_migrations

Control interno de migraciones aplicadas: `name` (nombre del archivo) y `applied_at`.

## Datos iniciales

| id | name | type | enabled |
|---|---|---|---|
| luz_sala | Luz de sala | luz | 0 |
| luz_cocina | Luz de cocina | luz | 0 |
| ventilador1 | Ventilador 1 | ventilador | 0 |
| puerta_principal | Puerta principal | puerta | 0 |
| alarma1 | Alarma principal | alarma | 0 |

La temperatura inicial es 28 °C. El sensor de temperatura no está en `devices`: se guarda en `settings` y la tabla de símbolos lo agrega como tipo `sensor`.

## Inicialización

La API aplica las migraciones y las semillas automáticamente al iniciar (`app/db.py`, función `inicializar`):

- Las migraciones se ejecutan una sola vez y quedan registradas en `schema_migrations`.
- Las semillas usan `INSERT OR IGNORE`, así que se pueden repetir sin duplicar datos.

Para reiniciar la base de datos, borra el archivo `backend/data/smarthome.sqlite` (o el volumen `smarthome-data` en Docker).
