# Reglas Semánticas — SmartHome (CommandFlow)

## 1. Formato de Errores Semánticos
Todos los errores semánticos se reportan mediante `ErrorSemantico` (subclase de `ErrorLenguaje`), produciendo la estructura uniforme:

```json
{
  "tipo": "Error semántico",
  "mensaje": "<descripción del error>",
  "linea": 1,
  "columna": 10
}