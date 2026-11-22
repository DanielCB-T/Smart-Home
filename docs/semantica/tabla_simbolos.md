# Tabla de Símbolos — SmartHome (CommandFlow)

## 1. Propósito y Estructura
La tabla de símbolos (`backend/app/semantic/tabla_simbolos.py`) almacena los dispositivos y sensores registrados en el sistema para validar su existencia, operaciones permitidas y tipos de datos sin modificar el AST.

Cada entrada (`SimboloDispositivo`) contiene:
* **`nombre`** (`str`): Identificador único del dispositivo. Distingue mayúsculas y minúsculas (`luz_sala` ≠ `LUZ_SALA`).
* **`tipo`** (`str`): Categoría funcional del dispositivo (`luz`, `ventilador`, `puerta`, `ventana`, `alarma`, `sensor_temperatura`).

## 2. Matriz de Compatibilidad por Tipo

| Tipo de dispositivo | Operaciones permitidas | Estados válidos | Tipo de valor |
| :--- | :--- | :--- | :--- |
| `luz` | `ENCENDER`, `APAGAR`, `CONSULTAR` | `ENCENDIDO`, `APAGADO` | Estado discreto |
| `ventilador` | `ENCENDER`, `APAGAR`, `CONSULTAR` | `ENCENDIDO`, `APAGADO` | Estado discreto |
| `puerta` | `ABRIR`, `CERRAR`, `CONSULTAR` | `ABIERTA`, `CERRADA` | Estado discreto |
| `ventana` | `ABRIR`, `CERRAR`, `CONSULTAR` | `ABIERTA`, `CERRADA` | Estado discreto |
| `alarma` | `ACTIVAR`, `DESACTIVAR`, `CONSULTAR` | `ACTIVADA`, `DESACTIVADA` | Estado discreto |
| `sensor_temperatura` | `ESTABLECER`, `CONSULTAR` | *(ninguno)* | Numérico (`int` / `float`) |

## 3. Catálogo Inicial Registrado (Seed)

| Identificador (`id`) | Tipo | Fuente |
| :--- | :--- | :--- |
| `luz_sala` | `luz` | `S001__initial_devices.sql` |
| `luz_cocina` | `luz` | `S001__initial_devices.sql` |
| `ventilador1` | `ventilador` | `S001__initial_devices.sql` |
| `puerta_principal` | `puerta` | `S001__initial_devices.sql` |
| `alarma1` | `alarma` | `S001__initial_devices.sql` |
| `temperatura` | `sensor_temperatura` | `settings` (`temperature`) |