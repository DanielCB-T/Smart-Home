import { useMemo, useState } from 'react';
import { arbolDesdeAst, type NodoArbol } from '../lib/ast';
import type { Analisis } from '../types';

type Pestana = 'arbol' | 'ir' | 'json';

function Nodo({ nodo, profundidad }: { nodo: NodoArbol; profundidad: number }) {
  return (
    <li className="arbol-item" style={{ animationDelay: `${profundidad * 120}ms` }}>
      <div className="arbol-nodo">
        <strong>{nodo.etiqueta}</strong>
        {nodo.atributos.map(([clave, valor]) => (
          <span key={clave} className="arbol-atributo">{clave}: <code>{valor}</code></span>
        ))}
      </div>
      {nodo.hijos.length > 0 && (
        <ul className="arbol-hijos">
          {nodo.hijos.map((hijo, i) => <Nodo key={`${hijo.etiqueta}-${i}`} nodo={hijo} profundidad={profundidad + 1} />)}
        </ul>
      )}
    </li>
  );
}

interface Props {
  analisis: Analisis | null;
}

export default function AstPanel({ analisis }: Props) {
  const [pestana, setPestana] = useState<Pestana>('arbol');
  const arbol = useMemo(() => (analisis?.ast ? arbolDesdeAst(analisis.ast) : null), [analisis]);

  const pestanas: { valor: Pestana; texto: string }[] = [
    { valor: 'arbol', texto: 'Árbol' },
    { valor: 'ir', texto: 'IR' },
    { valor: 'json', texto: 'JSON AST' }
  ];

  return (
    <section className="tarjeta ast" aria-labelledby="titulo-ast">
      <header className="tarjeta-titulo">
        <div>
          <h2 id="titulo-ast">Árbol sintáctico abstracto (AST) e IR</h2>
          <p className="texto-suave">Representación de la última instrucción analizada</p>
        </div>
        <div className="pestanas" role="tablist" aria-label="Vista del análisis">
          {pestanas.map(p => (
            <button key={p.valor} type="button" role="tab" aria-selected={pestana === p.valor}
              className={`pestana ${pestana === p.valor ? 'pestana-activa' : ''}`} onClick={() => setPestana(p.valor)}>
              {p.texto}
            </button>
          ))}
        </div>
      </header>

      {!analisis ? (
        <p className="texto-suave vacio">Ejecuta una instrucción para ver su árbol.</p>
      ) : !analisis.ok || !arbol ? (
        <p className="texto-suave vacio">
          Esta instrucción no tiene árbol porque falló en la etapa de {analisis.error?.tipo.toLowerCase() ?? 'análisis'}.
        </p>
      ) : pestana === 'arbol' ? (
        <div className="arbol-contenedor">
          <ul className="arbol-raiz"><Nodo nodo={arbol} profundidad={0} /></ul>
        </div>
      ) : pestana === 'ir' ? (
        <ol className="ir-lista">
          {(analisis.ir?.instrucciones ?? []).map((instruccion, i) => {
            const { op, ...resto } = instruccion;
            return (
              <li key={i} className="ir-fila">
                <span className="ir-op">{String(op)}</span>
                <span className="ir-campos">
                  {Object.entries(resto).map(([k, v]) => (
                    <span key={k}>{k}: <code>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</code></span>
                  ))}
                </span>
              </li>
            );
          })}
        </ol>
      ) : (
        <pre className="json-ast">{JSON.stringify(analisis.ast, null, 2)}</pre>
      )}
    </section>
  );
}
