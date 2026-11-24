# Wireframes de la interfaz (S1-05)

Boceto de baja fidelidad de las tres zonas principales. El diseño final puede cambiar, pero estas zonas y sus datos son obligatorios.

```
+-------------------------------------------------------------------+
| SmartHome                                        Temperatura 28°C |
+-----------------------------------+-------------------------------+
| PANEL DE DISPOSITIVOS             | CONSOLA DE INSTRUCCIONES      |
|                                   |                               |
| [ Luz de sala     ]  ENCENDIDO    | > ENCENDER luz_sala_          |
|   [Encender] [Apagar]             |                               |
|                                   |              [ Ejecutar ]     |
| [ Luz de cocina   ]  APAGADO      |                               |
|   [Encender] [Apagar]             | RESULTADO                     |
|                                   | Reconocida: ENCENDER          |
| [ Ventilador 1    ]  APAGADO      | Validación: CORRECTA          |
|   [Encender] [Apagar]             | Ejecución: EXITOSA            |
|                                   | "Luz de sala encendida."      |
| [ Puerta principal] CERRADA       |                               |
|   [Abrir] [Cerrar]                +-------------------------------+
|                                   | HISTORIAL                     |
| [ Alarma principal] DESACTIVADA   | 10:42  ENCENDER luz_sala   OK |
|   [Activar] [Desactivar]          | 10:40  ENCENDER alarma1  ERR  |
|                                   | 10:38  SI temp > 30   OMITIDA |
| Sensor de temperatura: 28 °C      |                               |
+-----------------------------------+-------------------------------+
```

## Elementos y datos

| Zona | Elemento | Datos que muestra |
|---|---|---|
| Panel de dispositivos | Tarjeta por dispositivo | Nombre, estado actual, botones de acción según el tipo |
| Panel de dispositivos | Sensor de temperatura | Valor en °C |
| Consola | Campo de texto y botón Ejecutar | Instrucción escrita (máximo 300 caracteres) |
| Resultado | Bloque de etapas | Instrucción reconocida, validación (correcta o tipo de error), ejecución y mensaje |
| Historial | Lista de registros | Hora, instrucción, resultado (OK, ERROR u OMITIDA) |

## Estados visuales

- **Dispositivo encendido o activo:** color verde.
- **Dispositivo apagado o desactivado:** color gris.
- **Error léxico, sintáctico o semántico:** mensaje en rojo con la posición (línea y columna).
- **Condición falsa en SI ... ENTONCES:** estado OMITIDA en el historial, sin error.
