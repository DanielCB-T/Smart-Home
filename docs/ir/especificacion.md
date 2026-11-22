# Especificación de Representación Intermedia (IR)

## 1. Estructura General
El generador de IR (`backend/app/semantic/ir.py`) recibe un `Programa` (AST) ya validado semánticamente y produce un diccionario serializable a JSON con versión `"1.0"`:

```json
{
  "version": "1.0",
  "instrucciones": [ ... ]
}