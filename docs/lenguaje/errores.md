# Errores del lenguaje

Cada error incluye tipo, mensaje, línea y columna. La API devuelve el primer error encontrado.

| Tipo | Cuándo ocurre | Ejemplo | Mensaje |
|---|---|---|---|
| Error léxico | Carácter o token no válido | `ENCENDER led1@` | carácter '@' no reconocido |
| Error sintáctico | La secuencia de tokens no coincide con la gramática | `ENCENDER` | se esperaba un identificador de dispositivo y se encontró fin de línea |
| Error semántico | El dispositivo no existe o la operación no es compatible | `ENCENDER alarma1` | La acción ENCENDER no es compatible con "alarma1" (tipo alarma). Operaciones permitidas: ACTIVAR, DESACTIVAR. |
| Error semántico | El dispositivo no existe | `ENCENDER dispositivo99` | El dispositivo "dispositivo99" no existe. |
| Error semántico | Estado que no corresponde al tipo | `SI luz_sala == ACTIVADA ENTONCES APAGAR luz_sala` | El estado ACTIVADA no existe para "luz_sala" (tipo luz). |
| Error semántico | Correo con estructura inválida | `ENVIAR CORREO A "malcorreo" MENSAJE "Hola"` | El destinatario "malcorreo" no tiene una estructura de correo válida. |
