import { useMemo, useState } from 'react';
import type { Registro } from '../types';

type Filtro = 'todos' | 'exitos' | 'errores' | 'omitidas';

const filtros: { valor: Filtro; texto: string }[] = [
  { valor: 'todos', texto: 'Todos' },
  { valor: 'exitos', texto: 'Exitosos' },
  { valor: 'errores', texto: 'Errores' },
  { valor: 'omitidas', texto: 'Omitidos' }
];

interface Props {
  historial: Registro[];
}

export default function HistoryPanel({ historial }: Props) {
  const [filtro, setFiltro] = useState<Filtro>('todos');

  const visibles = useMemo(() => historial.filter(r => {
    if (filtro === 'exitos') return r.success && !r.skipped;
    if (filtro === 'errores') return !r.success;
    if (filtro === 'omitidas') return r.skipped;
    return true;
  }), [historial, filtro]);

  return (
    <section className="tarjeta historial" aria-labelledby="titulo-historial">
      <header className="tarjeta-titulo">
        <h2 id="titulo-historial">Historial</h2>
        <span className="texto-suave">{historial.length} registros</span>
      </header>
      <div className="filtros" role="group" aria-label="Filtrar historial">
        {filtros.map(f => (
          <button key={f.valor} type="button" className={`chip ${filtro === f.valor ? 'chip-activo' : ''}`} onClick={() => setFiltro(f.valor)}>
            {f.texto}
          </button>
        ))}
      </div>
      {visibles.length === 0 ? (
        <p className="texto-suave vacio">No hay registros para este filtro.</p>
      ) : (
        <ul className="lista-historial">
          {visibles.map(r => {
            const clase = !r.success ? 'fallo' : r.skipped ? 'omitida' : 'exito';
            const marca = !r.success ? '✕' : r.skipped ? '○' : '✓';
            return (
              <li key={r.id} className={`entrada-historial ${clase}`}>
                <span className="marca" aria-hidden="true">{marca}</span>
                <div>
                  <code>{r.command}</code>
                  <p>{r.message}</p>
                  <time dateTime={r.timestamp}>{new Date(r.timestamp).toLocaleTimeString('es-MX')}</time>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
