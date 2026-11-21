import type { HomeState, CommandResponse } from './types';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, init);
  const body: unknown = await response.json();
  if (!response.ok && !(body && typeof body === 'object' && 'result' in body)) {
    const message = body && typeof body === 'object' && 'error' in body
      ? String(body.error) : 'Error al contactar el servidor.';
    throw new Error(message);
  }
  return body as T;
}
const jsonHeaders = { 'Content-Type': 'application/json' };
export const api = {
  state: () => request<HomeState>('/api/state'),
  command: (command: string) => request<CommandResponse>('/api/command', {
    method: 'POST', headers: jsonHeaders, body: JSON.stringify({ command })
  }),
  temperature: (temperature: number) => request<HomeState>('/api/temperature', {
    method: 'PUT', headers: jsonHeaders, body: JSON.stringify({ temperature })
  }),
  devices: () => request<HomeState['devices']>('/api/devices'),
  history: () => request<HomeState['history']>('/api/history')
};
