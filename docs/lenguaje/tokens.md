# Tokens reconocidos

El analizador léxico (`backend/app/language/lexer.py`) convierte el texto en tokens con tipo, valor, línea y columna. Las palabras reservadas no distinguen mayúsculas; los identificadores sí se conservan tal como se escribieron.

| Token | Patrón | Ejemplo | Valor guardado |
|---|---|---|---|
| ENCENDER, APAGAR, ACTIVAR, DESACTIVAR, ABRIR, CERRAR | palabra reservada | `ENCENDER` | `ENCENDER` |
| CONSULTAR, LISTAR, DISPOSITIVOS, ESTABLECER, NOTIFICAR | palabra reservada | `LISTAR` | `LISTAR` |
| ENVIAR, CORREO, A, MENSAJE | palabra reservada | `MENSAJE` | `MENSAJE` |
| SI, ENTONCES | palabra reservada | `SI` | `SI` |
| ESTADO | ENCENDIDO, APAGADO, ACTIVADA, DESACTIVADA, ABIERTA, CERRADA | `ENCENDIDO` | `ENCENDIDO` |
| IDENTIFICADOR | letra o `_` seguido de letras, dígitos o `_` | `luz_sala` | `luz_sala` |
| NUMERO | entero o decimal, opcional `-` | `-5`, `22.5` | `-5`, `22.5` |
| CADENA | texto entre comillas dobles o simples | `"hola"` | `hola` |
| IGUAL, DISTINTO, MAYOR, MENOR, MAYOR_IGUAL, MENOR_IGUAL | `==`, `!=`, `>`, `<`, `>=`, `<=` | `>=` | `>=` |
| SALTO_LINEA | fin de línea | | |
| EOF | fin de la entrada | | |

Espacios, tabuladores y `\r` se ignoran. Los comentarios empiezan con `#`.

## Errores léxicos

| Entrada | Mensaje |
|---|---|
| `ENCENDER led1@` | Error léxico: carácter '@' no reconocido (línea 1, col 14) |
| `SI temperatura = 30` | Error léxico: '=' solo no es válido, ¿quisiste decir '=='? |
| `ESTABLECER temp 1a` | Error léxico: número mal formado '1a...': los identificadores no pueden empezar con un dígito |
| `NOTIFICAR "Prueba` | Error léxico: cadena sin cerrar |
