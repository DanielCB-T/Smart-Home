import { useState, type KeyboardEvent } from 'react';

export const ejemplos = [
  'ENCENDER luz_sala',
  'APAGAR luz_sala',
  'ENCENDER ventilador1',
  'ABRIR puerta_principal',
  'DESACTIVAR alarma1',
  'SI temperatura > 30 ENTONCES ENCENDER ventilador1',
  'SI luz_sala == ENCENDIDO ENTONCES APAGAR luz_sala',
  'ENCENDER dispositivo99',
  'ENCENDER alarma1',
  'ENCENDER led1@'
];

interface Props {
  ocupado: boolean;
  onEjecutar: (texto: string) => void;
}

export default function CommandConsole({ ocupado, onEjecutar }: Props) {
  const [texto, setTexto] = useState('');
  const [historial, setHistorial] = useState<string[]>([]);
  const [indice, setIndice] = useState<number | null>(null);

  function enviar(valor = texto) {
    const limpio = valor.trim();
    if (!limpio || ocupado) return;
    setHistorial(prev => [limpio, ...prev.filter(c => c !== limpio)].slice(0, 20));
    setIndice(null);
    onEjecutar(limpio);
    setTexto('');
  }

  function teclas(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') { e.preventDefault(); enviar(); }
    if (e.key === 'ArrowUp' && historial.length) {
      e.preventDefault();
      const siguiente = indice === null ? 0 : Math.min(indice + 1, historial.length - 1);
      setIndice(siguiente); setTexto(historial[siguiente]);
    }
    if (e.key === 'ArrowDown' && indice !== null) {
      e.preventDefault();
      const siguiente = indice - 1;
      if (siguiente < 0) { setIndice(null); setTexto(''); }
      else { setIndice(siguiente); setTexto(historial[siguiente]); }
    }
  }

  return (
    <section className="tarjeta consola" aria-labelledby="titulo-consola">
      <header className="tarjeta-titulo">
        <h2 id="titulo-consola">Consola de instrucciones</h2>
        <span className="texto-suave">↑ ↓ para repetir comandos</span>
      </header>
      <div className="entrada-comando">
        <span className="prompt" aria-hidden="true">&gt;</span>
        <input
          type="text"
          value={texto}
          maxLength={300}
          placeholder="Escribe una instrucción, por ejemplo: ENCENDER luz_sala"
          onChange={e => setTexto(e.target.value)}
          onKeyDown={teclas}
          aria-label="Instrucción"
          spellCheck={false}
          autoComplete="off"
        />
        <button type="button" className="boton-primario" disabled={ocupado || !texto.trim()} onClick={() => enviar()}>
          {ocupado ? 'Ejecutando…' : 'Ejecutar'}
        </button>
      </div>
      <div className="ejemplos">
        <span className="texto-suave">Prueba:</span>
        {ejemplos.map(ej => (
          <button key={ej} type="button" className="chip chip-codigo" onClick={() => enviar(ej)} disabled={ocupado}>
            {ej}
          </button>
        ))}
      </div>
    </section>
  );
}
