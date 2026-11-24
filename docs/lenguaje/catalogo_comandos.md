# Catálogo de comandos

Cada comando tiene una producción en `gramatica.ebnf`, un nodo en el AST y una construcción en el IR. Los ejemplos son válidos según la fase léxica y sintáctica.

| Comando | Sintaxis | Nodo AST | IR generado | Ejecución |
|---|---|---|---|---|
| ENCENDER | `ENCENDER <dispositivo>` | `Control` | `CONTROL_DISPOSITIVO` | S1 (FastAPI) |
| APAGAR | `APAGAR <dispositivo>` | `Control` | `CONTROL_DISPOSITIVO` | S1 (FastAPI) |
| ACTIVAR | `ACTIVAR <alarma>` | `Control` | `CONTROL_DISPOSITIVO` | S1 (FastAPI) |
| DESACTIVAR | `DESACTIVAR <alarma>` | `Control` | `CONTROL_DISPOSITIVO` | S1 (FastAPI) |
| ABRIR | `ABRIR <puerta>` | `Control` | `CONTROL_DISPOSITIVO` | S1 (FastAPI) |
| CERRAR | `CERRAR <puerta>` | `Control` | `CONTROL_DISPOSITIVO` | S1 (FastAPI) |
| CONSULTAR | `CONSULTAR <dispositivo>` | `Consultar` | `CONSULTA_DISPOSITIVO` | Pendiente, S2-09 |
| LISTAR | `LISTAR DISPOSITIVOS` | `Listar` | `LISTAR_DISPOSITIVOS` | Pendiente, S2-09 |
| ESTABLECER | `ESTABLECER <sensor> <número>` | `Establecer` | `ESTABLECER_SENSOR` | Pendiente |
| NOTIFICAR | `NOTIFICAR "<mensaje>"` | `Notificar` | `NOTIFICACION` | Pendiente, S2-10 |
| ENVIAR CORREO | `ENVIAR CORREO A "<correo>" MENSAJE "<texto>"` | `EnviarCorreo` | `ENVIO_CORREO` | Pendiente, S2-18 |
| SI ... ENTONCES | `SI <identificador> <operador> <valor> ENTONCES <instrucción simple>` | `Condicional` | `CONDICIONAL` | Parcial: solo condiciones sobre `temperatura` |

## Dispositivos y operaciones

| Tipo | Dispositivos | Operaciones de control | Estados válidos |
|---|---|---|---|
| luz | luz_sala, luz_cocina | ENCENDER, APAGAR | ENCENDIDO, APAGADO |
| ventilador | ventilador1 | ENCENDER, APAGAR | ENCENDIDO, APAGADO |
| puerta | puerta_principal | ABRIR, CERRAR | ABIERTA, CERRADA |
| alarma | alarma1 | ACTIVAR, DESACTIVAR | ACTIVADA, DESACTIVADA |
| sensor | temperatura | ninguna | valor numérico |

Todos los dispositivos aceptan CONSULTAR. Las condiciones sobre estados solo admiten `==` y `!=`.
