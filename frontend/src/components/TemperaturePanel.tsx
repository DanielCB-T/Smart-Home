import { useEffect, useState } from 'react';

const preajustes = [20, 25, 30, 35];
const MIN = -20;
const MAX = 60;

interface Props {
  temperatura: number;
  ocupado: boolean;
  onFijar: (valor: number) => void;
}

export default function TemperaturePanel({ temperatura, ocupado, onFijar }: Props) {
  const [valor, setValor] = useState(temperatura);

  useEffect(() => setValor(temperatura), [temperatura]);

  const valido = Number.isFinite(valor) && valor >= MIN && valor <= MAX;
  const porcentaje = ((temperatura - MIN) / (MAX - MIN)) * 100;

  return (
    <section className="tarjeta temperatura">
      <header className="tarjeta-titulo">
        <h2>Sensor de temperatura</h2>
        <span className="texto-suave">Simulado · condiciones SI usan este valor</span>
      </header>
      <div className="temperatura-lectura">
        <strong>{temperatura}</strong><span>°C</span>
      </div>
      <div className="barra" aria-hidden="true">
        <div className="barra-relleno" style={{ width: `${Math.min(100, Math.max(0, porcentaje))}%` }} />
      </div>
      <div className="temperatura-controles">
        <input
          type="range"
          min={MIN}
          max={MAX}
          step={1}
          value={Number.isFinite(valor) ? valor : temperatura}
          onChange={e => setValor(Number(e.target.value))}
          aria-label="Ajustar temperatura"
        />
        <input
          type="number"
          min={MIN}
          max={MAX}
          value={Number.isFinite(valor) ? valor : ''}
          onChange={e => setValor(Number(e.target.value))}
          aria-label="Temperatura en grados"
        />
        <button type="button" className="boton-primario" disabled={ocupado || !valido} onClick={() => onFijar(valor)}>
          Aplicar
        </button>
      </div>
      <div className="preajustes">
        {preajustes.map(p => (
          <button key={p} type="button" className="chip" disabled={ocupado} onClick={() => onFijar(p)}>{p} °C</button>
        ))}
      </div>
    </section>
  );
}
