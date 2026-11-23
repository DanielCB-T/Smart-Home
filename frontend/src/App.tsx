import { useCallback, useEffect, useState } from 'react';
import { api } from './api';
import CommandConsole from './components/CommandConsole';
import DeviceCard from './components/DeviceCard';
import HistoryPanel from './components/HistoryPanel';
import ResultPanel from './components/ResultPanel';
import TemperaturePanel from './components/TemperaturePanel';
import type { Estado, RespuestaComando } from './types';

const INTERVALO_ACTUALIZACION_MS = 5000;

export default function App() {
  const [estado, setEstado] = useState<Estado | null>(null);
  const [ultimo, setUltimo] = useState<RespuestaComando | null>(null);
  const [conectado, setConectado] = useState(true);
  const [ocupado, setOcupado] = useState(false);
  const [aviso, setAviso] = useState<string | null>(null);

  const cargar = useCallback(async () => {
    try {
      setEstado(await api.estado());
      setConectado(true);
    } catch {
      setConectado(false);
    }
  }, []);

  useEffect(() => {
    void cargar();
    const temporizador = window.setInterval(() => void cargar(), INTERVALO_ACTUALIZACION_MS);
    return () => window.clearInterval(temporizador);
  }, [cargar]);

  // Aplica el estado que devuelve cualquier operación que cambie el sistema.
  const aplicar = (r: Estado) => setEstado({ devices: r.devices, temperature: r.temperature, history: r.history });

  async function ejecutar(texto: string) {
    setOcupado(true); setAviso(null);
    try {
      const respuesta = await api.comando(texto);
      aplicar(respuesta);
      setUltimo(respuesta);
      setConectado(true);
    } catch (error) {
      setAviso(error instanceof Error ? error.message : 'Error inesperado.');
      setConectado(false);
    } finally {
      setOcupado(false);
    }
  }

  async function accion(id: string, action: string) {
    setOcupado(true); setAviso(null);
    try {
      const respuesta = await api.accion(id, action);
      aplicar(respuesta);
      setUltimo(respuesta);
    } catch (error) {
      setAviso(error instanceof Error ? error.message : 'Error inesperado.');
    } finally {
      setOcupado(false);
    }
  }

  async function fijarTemperatura(valor: number) {
    setOcupado(true); setAviso(null);
    try {
      aplicar(await api.temperatura(valor));
    } catch (error) {
      setAviso(error instanceof Error ? error.message : 'Error inesperado.');
    } finally {
      setOcupado(false);
    }
  }

  const activos = estado?.devices.filter(d => d.on || d.open).length ?? 0;

  return (
    <div className="app">
      <header className="encabezado">
        <div className="marca">
          <span className="marca-logo" aria-hidden="true">⌂</span>
          <div>
            <strong>SmartHome</strong>
            <span className="texto-suave">Centro de control</span>
          </div>
        </div>
        <div className="resumen">
          <span><strong>{estado?.devices.length ?? '—'}</strong> dispositivos</span>
          <span><strong>{activos}</strong> activos</span>
          <span><strong>{estado?.temperature ?? '—'}°C</strong> ambiente</span>
        </div>
        <span className={`estado-conexion ${conectado ? 'en-linea' : 'sin-conexion'}`}>
          {conectado ? 'Conectado' : 'Sin conexión'}
        </span>
      </header>

      <main className="contenido">
        {aviso && (
          <div className="aviso" role="alert">
            <span>{aviso}</span>
            <button type="button" className="boton-texto" onClick={() => setAviso(null)} aria-label="Cerrar aviso">×</button>
          </div>
        )}

        <section aria-labelledby="titulo-dispositivos">
          <h2 id="titulo-dispositivos" className="titulo-seccion">Dispositivos</h2>
          {estado ? (
            <div className="cuadricula">
              {estado.devices.map(dispositivo => (
                <DeviceCard key={dispositivo.id} dispositivo={dispositivo} ocupado={ocupado} onAccion={accion} />
              ))}
            </div>
          ) : (
            <p className="texto-suave">{conectado ? 'Cargando dispositivos…' : 'No se pudo conectar con la API. Revisa que el backend esté activo en el puerto 3001.'}</p>
          )}
        </section>

        <div className="dos-columnas">
          <div className="columna">
            <TemperaturePanel temperatura={estado?.temperature ?? 28} ocupado={ocupado} onFijar={fijarTemperatura} />
            <CommandConsole ocupado={ocupado} onEjecutar={ejecutar} />
            <ResultPanel respuesta={ultimo} />
          </div>
          <div className="columna">
            <HistoryPanel historial={estado?.history ?? []} />
          </div>
        </div>
      </main>

      <footer className="pie">SmartHome · Proyecto integrador · Lenguajes y Autómatas II</footer>
    </div>
  );
}
