import type { RespuestaComando } from '../types';

interface Props {
  respuesta: RespuestaComando | null;
}

type Paso = { titulo: string; estado: 'ok' | 'error' | 'aviso' | 'neutro'; detalle: string };

function pasos(r: RespuestaComando): Paso[] {
  const instruccion = r.result.command.trim().split(/\s+/)[0]?.toUpperCase() || '—';
  const error = r.analysis.error;

  // Un error léxico o sintáctico impide reconocer la instrucción.
  const fallaAntesDeReconocer = Boolean(error && (error.tipo === 'Error léxico' || error.tipo === 'Error sintáctico'));
  const reconocida: Paso = fallaAntesDeReconocer
    ? { titulo: 'Instrucción reconocida', estado: 'error', detalle: 'No reconocida' }
    : { titulo: 'Instrucción reconocida', estado: 'ok', detalle: instruccion };

  if (fallaAntesDeReconocer) {
    return [
      reconocida,
      { titulo: 'Validación', estado: 'neutro', detalle: 'No se llegó a validar' },
      { titulo: 'Ejecución', estado: 'neutro', detalle: 'No se ejecutó' }
    ];
  }
  if (error) {
    return [
      reconocida,
      { titulo: 'Validación', estado: 'error', detalle: error.tipo },
      { titulo: 'Ejecución', estado: 'neutro', detalle: 'No se ejecutó' }
    ];
  }

  const ejecucion: Paso = r.result.success
    ? r.result.skipped
      ? { titulo: 'Ejecución', estado: 'aviso', detalle: 'Omitida (condición falsa)' }
      : { titulo: 'Ejecución', estado: 'ok', detalle: 'Exitosa' }
    : { titulo: 'Ejecución', estado: 'error', detalle: 'Fallida' };
  return [reconocida, { titulo: 'Validación', estado: 'ok', detalle: 'Correcta' }, ejecucion];
}

export default function ResultPanel({ respuesta }: Props) {
  if (!respuesta) {
    return (
      <section className="tarjeta resultado" aria-live="polite">
        <header className="tarjeta-titulo"><h2>Resultado</h2></header>
        <p className="texto-suave">Ejecuta una instrucción para ver el resultado de cada etapa.</p>
      </section>
    );
  }
  const { analysis, result } = respuesta;
  const error = analysis.error;
  return (
    <section className="tarjeta resultado" aria-live="polite">
      <header className="tarjeta-titulo"><h2>Resultado</h2></header>
      <ol className="pasos">
        {pasos(respuesta).map(paso => (
          <li key={paso.titulo} className={`paso paso-${paso.estado}`}>
            <span className="paso-marca" aria-hidden="true">
              {paso.estado === 'ok' ? '✓' : paso.estado === 'error' ? '✕' : paso.estado === 'aviso' ? '○' : '–'}
            </span>
            <div>
              <strong>{paso.titulo}</strong>
              <span className="texto-suave"> · {paso.detalle}</span>
            </div>
          </li>
        ))}
      </ol>
      <p className={`mensaje ${result.success ? 'mensaje-ok' : 'mensaje-error'}`}>
        {error
          ? `${error.tipo} (línea ${error.linea}, columna ${error.columna}): ${error.mensaje}`
          : result.message}
      </p>
      {analysis.ok && (
        <details className="detalles">
          <summary>Ver representación intermedia (IR)</summary>
          <pre>{JSON.stringify(analysis.ir, null, 2)}</pre>
        </details>
      )}
    </section>
  );
}
