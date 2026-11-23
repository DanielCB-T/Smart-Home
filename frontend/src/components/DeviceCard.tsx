import type { Dispositivo } from '../types';

const iconos = { luz: '💡', ventilador: '🌀', puerta: '🚪', alarma: '🚨' } as const;
const etiquetas = { luz: 'Iluminación', ventilador: 'Ventilación', puerta: 'Acceso', alarma: 'Seguridad' } as const;

export function activo(d: Dispositivo): boolean {
  return d.type === 'puerta' ? Boolean(d.open) : Boolean(d.on);
}

export function accionSiguiente(d: Dispositivo): { action: string; label: string } {
  const on = activo(d);
  switch (d.type) {
    case 'luz':
    case 'ventilador': return on ? { action: 'APAGAR', label: 'Apagar' } : { action: 'ENCENDER', label: 'Encender' };
    case 'puerta': return on ? { action: 'CERRAR', label: 'Cerrar' } : { action: 'ABRIR', label: 'Abrir' };
    case 'alarma': return on ? { action: 'DESACTIVAR', label: 'Desactivar' } : { action: 'ACTIVAR', label: 'Activar' };
  }
}

interface Props {
  dispositivo: Dispositivo;
  ocupado: boolean;
  onAccion: (id: string, action: string) => void;
}

export default function DeviceCard({ dispositivo, ocupado, onAccion }: Props) {
  const encendido = activo(dispositivo);
  const accion = accionSiguiente(dispositivo);
  return (
    <article className={`tarjeta dispositivo ${encendido ? 'activo' : ''}`}>
      <div className="dispositivo-cabecera">
        <span className="dispositivo-icono" aria-hidden="true">{iconos[dispositivo.type]}</span>
        <span className={`insignia ${encendido ? 'insignia-ok' : ''}`}>{dispositivo.estado}</span>
      </div>
      <h3>{dispositivo.name}</h3>
      <p className="texto-suave">{etiquetas[dispositivo.type]} · <code>{dispositivo.id}</code></p>
      <button
        type="button"
        className={encendido ? 'boton-secundario' : 'boton-primario'}
        disabled={ocupado}
        onClick={() => onAccion(dispositivo.id, accion.action)}
      >
        {accion.label}
      </button>
    </article>
  );
}
