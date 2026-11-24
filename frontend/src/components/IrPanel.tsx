import type { Analisis } from '../types';

interface Props {
  analisis: Analisis | null;
}

// Muestra el IR de la última instrucción en código de tres direcciones.
export default function IrPanel({ analisis }: Props) {
  return (
    <section className="tarjeta ir" aria-labelledby="titulo-ir">
      <header className="tarjeta-titulo">
        <div>
          <h2 id="titulo-ir">Representación intermedia (IR)</h2>
          <p className="texto-suave">Código de tres direcciones de la última instrucción</p>
        </div>
      </header>

      {!analisis ? (
        <p className="texto-suave vacio">Ejecuta una instrucción para ver su código intermedio.</p>
      ) : !analisis.ok || !analisis.ir_tac ? (
        <p className="texto-suave vacio">
          Esta instrucción no genera IR porque falló en la etapa de {analisis.error?.tipo.toLowerCase() ?? 'análisis'}.
        </p>
      ) : analisis.ir_tac.length === 0 ? (
        <p className="texto-suave vacio">La instrucción no genera código intermedio.</p>
      ) : (
        <pre className="codigo-ir" aria-label="Código de tres direcciones">
          {analisis.ir_tac.map((linea, i) => (
            <div key={i} className={linea.endsWith(':') ? 'linea-etiqueta' : 'linea-codigo'}>
              {linea}
            </div>
          ))}
        </pre>
      )}
    </section>
  );
}
