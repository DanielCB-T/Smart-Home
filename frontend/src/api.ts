import type { Estado, RespuestaComando } from './types';

export class ErrorApi extends Error {}

function mensajeDeError(cuerpo: unknown, estado: number): string {
  if (cuerpo && typeof cuerpo === 'object') {
    const datos = cuerpo as Record<string, unknown>;
    if (typeof datos.error === 'string') return datos.error;
    if (typeof datos.detail === 'string') return datos.detail;
    if (Array.isArray(datos.detail)) return 'Los datos enviados no son válidos.';
  }
  return `Error del servidor (${estado}).`;
}

async function peticion<T>(ruta: string, init?: RequestInit): Promise<T> {
  let respuesta: Response;
  try {
    respuesta = await fetch(ruta, init);
  } catch {
    throw new ErrorApi('No hay conexión con el servidor de SmartHome.');
  }
  const cuerpo: unknown = await respuesta.json().catch(() => null);

  // Las instrucciones fallidas responden 422 con el resultado: no son errores de red.
  if (cuerpo && typeof cuerpo === 'object' && 'result' in cuerpo) return cuerpo as T;
  if (!respuesta.ok) throw new ErrorApi(mensajeDeError(cuerpo, respuesta.status));
  return cuerpo as T;
}

const json = (cuerpo: unknown): RequestInit => ({
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo)
});

export const api = {
  estado: () => peticion<Estado>('/api/state'),
  comando: (command: string) => peticion<RespuestaComando>('/api/command', { method: 'POST', ...json({ command }) }),
  accion: (id: string, action: string) =>
    peticion<RespuestaComando>(`/api/devices/${encodeURIComponent(id)}`, { method: 'PATCH', ...json({ action }) }),
  temperatura: (temperature: number) => peticion<Estado>('/api/temperature', { method: 'PUT', ...json({ temperature }) })
};

