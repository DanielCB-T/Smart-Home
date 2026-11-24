export type Tema = 'oscuro' | 'claro';

const CLAVE = 'smarthome-tema';

export function temaInicial(): Tema {
  const guardado = localStorage.getItem(CLAVE);
  if (guardado === 'claro' || guardado === 'oscuro') return guardado;
  return window.matchMedia?.('(prefers-color-scheme: light)').matches ? 'claro' : 'oscuro';
}

export function aplicarTema(tema: Tema): void {
  document.documentElement.dataset.theme = tema;
  localStorage.setItem(CLAVE, tema);
}
