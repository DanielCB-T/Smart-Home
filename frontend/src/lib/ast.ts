// Convierte el AST que devuelve la API (diccionarios anidados) en un árbol visual.

export interface NodoArbol {
  etiqueta: string;
  atributos: [string, string][];
  hijos: NodoArbol[];
}

const OCULTOS = new Set(['tipo', 'linea', 'columna']);

function texto(valor: unknown): string {
  return typeof valor === 'string' ? `"${valor}"` : String(valor);
}

function nodoDesde(valor: unknown, etiquetaPadre: string): NodoArbol {
  if (Array.isArray(valor)) {
    return {
      etiqueta: etiquetaPadre,
      atributos: [],
      hijos: valor.map((elemento, i) => nodoDesde(elemento, `${etiquetaPadre}[${i}]`))
    };
  }
  if (valor && typeof valor === 'object') {
    const datos = valor as Record<string, unknown>;
    const etiqueta = typeof datos.tipo === 'string' ? datos.tipo : etiquetaPadre;
    const atributos: [string, string][] = [];
    const hijos: NodoArbol[] = [];
    for (const [clave, contenido] of Object.entries(datos)) {
      if (OCULTOS.has(clave)) continue;
      if (contenido && typeof contenido === 'object') hijos.push(nodoDesde(contenido, clave));
      else atributos.push([clave, texto(contenido)]);
    }
    return { etiqueta, atributos, hijos };
  }
  return { etiqueta: etiquetaPadre, atributos: [['valor', texto(valor)]], hijos: [] };
}

export function arbolDesdeAst(ast: unknown): NodoArbol {
  return nodoDesde(ast, 'Programa');
}
