import { useEffect, useState } from 'react';
import { api } from './api';
import type { Device, HomeState } from './types';

const icons = { luz: '☀', ventilador: '✺', puerta: '▣', alarma: '♢' };
const descriptions = { luz: 'Iluminación inteligente', ventilador: 'Ventilación del hogar', puerta: 'Control de acceso', alarma: 'Sistema de seguridad' };
const names = { luz: ['Encendida', 'Apagada'], ventilador: ['Encendido', 'Apagado'], puerta: ['Abierta', 'Cerrada'], alarma: ['Activada', 'Desactivada'] };
const examples = [
  'ENCENDER luz_sala',
  'APAGAR ventilador1',
  'ABRIR puerta_principal',
  'ACTIVAR alarma1',
  'SI temperatura > 30 ENTONCES ENCENDER ventilador1'
];
function active(device: Device) {
  return device.type === 'puerta' ? Boolean(device.open) : Boolean(device.on);
}
function nextAction(device: Device) {
  switch (device.type) {
    case 'luz':
    case 'ventilador': return active(device) ? 'APAGAR' : 'ENCENDER';
    case 'puerta': return active(device) ? 'CERRAR' : 'ABRIR';
    case 'alarma': return active(device) ? 'DESACTIVAR' : 'ACTIVAR';
  }
}

export default function App() {
  const [state, setState] = useState<HomeState | null>(null);
  const [temperature, setTemperature] = useState('28');
  const [commandText, setCommandText] = useState('');
  const [result, setResult] = useState('Esperando instrucciones…');
  const [failed, setFailed] = useState(false);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.state().then(data => {
      setState(data); setTemperature(String(data.temperature));
    }).catch(err => setError((err as Error).message));
  }, []);

  async function runCommand(text: string) {
    if (busy) return;
    setBusy(true); setError('');
    try {
      const data = await api.command(text);
      setState(data);
      setResult(data.result.message);
      setFailed(!data.result.success);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function updateTemperature() {
    const number = Number(temperature);
    if (!temperature.trim() || !Number.isFinite(number)) {
      setError('Ingresa una temperatura válida.'); return;
    }
    setBusy(true); setError('');
    try {
      const data = await api.temperature(number);
      setState(data); setTemperature(String(data.temperature));
      setResult(`Temperatura ajustada a ${data.temperature} °C.`);
      setFailed(false);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return <div className="layout">
    <aside className="sidebar">
      <div className="brand"><span className="brand-logo">⌂</span><span>Smart<span className="accent">Home</span><small>SISTEMA INTELIGENTE</small></span></div>
      <p className="side-heading">PANEL PRINCIPAL</p>
      <a className="nav-active" href="#dispositivos">▦ &nbsp; Dispositivos</a>
      <a href="#consola">⌘ &nbsp; Consola de comandos</a>
      <a href="#historial">◷ &nbsp; Historial</a>
      <div className="sidebar-bottom"><span className="online-dot" /> Servidor {state ? 'conectado' : 'sin conexión'} <small>Simulador doméstico · v2.0</small></div>
    </aside>
    <main>
      <header className="topbar"><div><span className="eyebrow">SMART HOME / DASHBOARD</span><h1>Centro de control — SmartHome</h1><p>Luces, ventiladores, puertas, alarmas y condiciones.</p></div><div className="avatar">SH</div></header>
      {error && <div className="alert visible" role="alert">{error}</div>}
      <section className="stats">
        <div className="stat"><span>DISPOSITIVOS</span><strong>{state?.devices.length ?? '—'}</strong><small>Registrados en el sistema</small></div>
        <div className="stat"><span>ACTIVOS / ABIERTOS</span><strong>{state?.devices.filter(active).length ?? '—'}</strong><small>En funcionamiento ahora</small></div>
        <div className="stat temp-stat"><span>TEMPERATURA AMBIENTE</span><strong>{state?.temperature ?? '—'}<span className="unit">°C</span></strong><label htmlFor="temperature">Modificar temperatura</label><div className="temp-control"><input id="temperature" type="number" min="-20" max="60" step="1" value={temperature} onChange={e => setTemperature(e.target.value)} /><button type="button" disabled={busy} onClick={updateTemperature}>Actualizar</button></div></div>
      </section>
      <section id="dispositivos" className="section"><div className="section-title"><div><h2>Dispositivos de la casa</h2><p>Estado actual de tus equipos simulados</p></div><span className="section-tag">ESTADO ACTUAL</span></div>
        <div className="device-grid">{state?.devices.map(device => {
          const enabled = active(device);
          const action = nextAction(device);
          return <article key={device.id} className={`device${enabled ? ' active' : ''}`}>
            <div className="device-top"><span className="device-icon">{icons[device.type]}</span><span className="status">{names[device.type][enabled ? 0 : 1]}</span></div>
            <h3>{device.name}</h3><small>{descriptions[device.type]} · {device.id}</small>
            <button type="button" className="device-control" disabled={busy} onClick={() => void runCommand(`${action} ${device.id}`)}>{action.charAt(0) + action.slice(1).toLowerCase()}</button>
          </article>;
        })}</div>
      </section>
      <div className="bottom-grid">
        <section id="consola" className="panel"><div className="panel-heading"><div><h2>⌘ &nbsp; Consola de instrucciones</h2><p>Controla dispositivos mediante comandos escritos</p></div><span className="terminal-dot" /></div>
          <form onSubmit={event => { event.preventDefault(); void runCommand(commandText); setCommandText(''); }}><label htmlFor="command">ESCRIBE UNA INSTRUCCIÓN</label><div className="command-row"><input id="command" maxLength={300} type="text" value={commandText} onChange={event => setCommandText(event.target.value)} placeholder="Ej. ENCENDER luz_sala" required /><button disabled={busy} type="submit">Ejecutar →</button></div></form>
          <div className="examples"><span>PRUEBA ESTOS COMANDOS</span>{examples.map(example => <button type="button" key={example} className="example" onClick={() => setCommandText(example)}>{example}</button>)}</div>
          <div className={`result${failed ? ' error' : ''}`} aria-live="polite">{result}</div>
        </section>
        <section id="historial" className="panel"><div className="panel-heading"><div><h2>◷ &nbsp; Historial de actividad</h2><p>Últimas instrucciones y operaciones</p></div><span className="history-label">RECIENTES</span></div>
          <div className="history">{!state?.history.length ? <p className="empty">Aún no hay actividad.</p> : state.history.map(entry => <div key={entry.id} className={`history-item${!entry.success ? ' failed' : entry.skipped ? ' skipped' : ''}`}>
            <span className="history-icon">{!entry.success ? '✕' : entry.skipped ? '○' : '✓'}</span><div className="history-text"><strong>{entry.command}</strong><p>{entry.message}</p><time>{new Date(entry.timestamp).toLocaleString('es-MX')}</time></div>
          </div>)}</div>
        </section>
      </div>
      <footer>SmartHome · Simulación de automatización inteligente · Proyecto académico</footer>
    </main>
  </div>;
}
