# Contrato: representación intermedia (IR)

Este documento describe el IR que produce `backend/app/semantic/ir.py` (función `generar_ir`) y su versión legible en código de tres direcciones (`backend/app/semantic/tac.py`). Cambiar el formato requiere un ADR y avisar a los módulos que lo consumen (la máquina virtual y el ejecutor).

## Forma general

El IR de un programa es un objeto JSON:

```json
{ "version": "1.0", "instrucciones": [ ... ] }
```

Cada instrucción tiene el campo `op` (operación) y el campo `linea`. Una instrucción puede llevar `etiqueta`, que es el destino de un salto. El último elemento siempre es `HALT`.

## Operaciones

| op | Campos | Significado |
|---|---|---|
| SET_STATE | dispositivo, valor | Asigna un estado al dispositivo. Es idempotente. |
| GET_STATE | dispositivo, destino, mostrar (opcional) | Lee el estado del dispositivo o del sensor y lo guarda en el temporal `destino`. |
| COMPARE | izquierda, operador, derecha, destino | Compara dos operandos y guarda el resultado booleano en `destino`. |
| JUMP_IF_FALSE | condicion, salto_a | Salta a la etiqueta `salto_a` si el temporal `condicion` es falso. |
| NOTIFY | mensaje | Genera una notificación. Tiene efectos externos: no se elimina ni se reordena. |
| SEND_EMAIL | destinatario, mensaje | Solicita el envío de un correo. Tiene efectos externos. |
| LIST_DEVICES | (ninguno) | Lista los dispositivos. |
| HALT | (ninguno) | Fin del programa. Solo se usa como destino de una etiqueta. |

Los operandos de COMPARE son `{"temp": "t1"}` para temporales y `{"valor": 30}` para constantes.

Los temporales se nombran `t1`, `t2`, … dentro de cada programa, y las etiquetas `L1`, `L2`, …

## Ejemplos

Para `ENCENDER luz_sala`:

```json
{"version": "1.0", "instrucciones": [
  {"op": "SET_STATE", "dispositivo": "luz_sala", "valor": "ENCENDIDO", "linea": 1},
  {"op": "HALT", "linea": 1}
]}
```

Para `SI temperatura > 30 ENTONCES ENCENDER ventilador1`:

```json
{"version": "1.0", "instrucciones": [
  {"op": "GET_STATE", "dispositivo": "temperatura", "destino": "t1", "linea": 1},
  {"op": "COMPARE", "izquierda": {"temp": "t1"}, "operador": ">", "derecha": {"valor": 30}, "destino": "t2", "linea": 1},
  {"op": "JUMP_IF_FALSE", "condicion": "t2", "salto_a": "L1", "linea": 1},
  {"op": "SET_STATE", "dispositivo": "ventilador1", "valor": "ENCENDIDO", "linea": 1},
  {"op": "HALT", "linea": 1, "etiqueta": "L1"}
]}
```

## Código de tres direcciones

La API devuelve además `ir_tac`, con el mismo programa en forma legible. Para el ejemplo anterior:

```
t1 = temperatura
t2 = t1 > 30
if_false t2 goto L1
ventilador1 = ENCENDIDO
L1:
```

Las reglas de conversión están en `tac.py`. `HALT` no se imprime, pero sí su etiqueta.

## Reglas

1. El IR no contiene texto del código fuente, solo nombres ya validados.
2. Ningún campo fuera de esta tabla debe aparecer en una instrucción.
3. Las instrucciones con efectos externos (NOTIFY, SEND_EMAIL) no se eliminan ni se reordenan en la optimización.
4. Los temporales se usan una sola vez, para pasar un valor de una instrucción a otra.
