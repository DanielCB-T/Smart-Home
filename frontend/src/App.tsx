import { useCallback, useEffect, useState } from 'react';
import { api, ErrorApi } from './api';
import IrPanel from './components/IrPanel';
import CommandConsole from './components/CommandConsole';
import DeviceCard from './components/DeviceCard';
import DeviceModal from './components/DeviceModal';
import HistoryPanel from './components/HistoryPanel';
import ResultPanel from './components/ResultPanel';
import TemperaturePanel from './components/TemperaturePanel';
import { confirmarEliminacion, notificarError, notificarExito } from './alertas';
import { aplicarTema, temaInicial, type Tema } from './tema';
import type { Dispositivo, DispositivoEntrada, Estado, RespuestaComando } from './types';

const INTERVALO_ACTUALIZACION_MS = 5000;

function mensaje(error: unknown): string {
  return error instanceof Error ? error.message : 'Error inesperado.';
}

function IconoTema({ tema }: { tema: Tema }) {
  return tema === 'oscuro' ? (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="4" /><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4" />
    </svg>
  ) : (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
    </svg>
  );
}

export default function App() {
  const [estado, setEstado] = useState<Estado | null>(null);
  const [ultimo, setUltimo] = useState<RespuestaComando | null>(null);
  const [conectado, setConectado] = useState(true);
  const [ocupado, setOcupado] = useState(false);
  const [aviso, setAviso] = useState<string | null>(null);
  const [tema, setTema] = useState<Tema>(temaInicial);
  const [modal, setModal] = useState<{ dispositivo: Dispositivo | null } | null>(null);

  useEffect(() => aplicarTema(tema), [tema]);

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

  const aplicar = (r: Estado) => setEstado({ devices: r.devices, temperature: r.temperature, history: r.history });

  async function ejecutar(texto: string) {
    setOcupado(true); setAviso(null);
    try {
      const respuesta = await api.comando(texto);
      aplicar(respuesta);
      setUltimo(respuesta);
      setConectado(true);
    } catch (error) {
      setAviso(mensaje(error));
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
      setAviso(mensaje(error));
    } finally {
      setOcupado(false);
    }
  }

  async function fijarTemperatura(valor: number) {
    setOcupado(true); setAviso(null);
    try {
      aplicar(await api.temperatura(valor));
    } catch (error) {
      setAviso(mensaje(error));
    } finally {
      setOcupado(false);
    }
  }

  async function guardarDispositivo(datos: DispositivoEntrada, idOriginal: string | null): Promise<boolean> {
    setOcupado(true);
    try {
      const respuesta = idOriginal
        ? await api.editarDispositivo(idOriginal, datos)
        : await api.crearDispositivo(datos);
      aplicar(respuesta);
      notificarExito(idOriginal ? 'Dispositivo actualizado' : 'Dispositivo registrado', `${datos.name} (${datos.id})`);
      return true;
    } catch (error) {
      notificarError(mensaje(error));
      return false;
    } finally {
      setOcupado(false);
    }
  }

  async function eliminarDispositivo(dispositivo: Dispositivo) {
    const confirmado = await confirmarEliminacion(dispositivo.name, dispositivo.id);
    if (!confirmado) return;
    setOcupado(true);
    try {
      aplicar(await api.eliminarDispositivo(dispositivo.id));
      notificarExito('Dispositivo eliminado', dispositivo.name);
    } catch (error) {
      if (error instanceof ErrorApi) notificarError(error.message);
      else notificarError(mensaje(error));
    } finally {
      setOcupado(false);
    }
  }

  const activos = estado?.devices.filter(d => d.on || d.open).length ?? 0;

  return (
    <div className="app">
      <header className="encabezado">
        <div className="identidad">
          <span className="logo" aria-hidden="true">⌂</span>
          <div>
            <div className="titulo-fila">
              <strong>SmartHome</strong>
            </div>
            <span className="texto-suave">Centro de control · Lenguajes y Autómatas II</span>
          </div>
        </div>

        <div className="resumen" aria-label="Resumen">
          <span className="metrica"><strong>{estado?.devices.length ?? '—'}</strong> dispositivos</span>
          <span className="metrica"><strong>{activos}</strong> activos</span>
          <span className="metrica"><strong>{estado?.temperature ?? '—'}°C</strong> ambiente</span>
        </div>

        <div className="acciones-encabezado">
          <span className={`estado-conexion ${conectado ? 'en-linea' : 'sin-conexion'}`}>
            {conectado ? 'En línea' : 'Sin conexión'}
          </span>
          <button type="button" className="boton-icono boton-tema" onClick={() => setTema(t => (t === 'oscuro' ? 'claro' : 'oscuro'))}
            aria-label={tema === 'oscuro' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
            title={tema === 'oscuro' ? 'Modo claro' : 'Modo oscuro'}>
            <IconoTema tema={tema} />
          </button>
        </div>
      </header>

      <main className="contenido">
        {aviso && (
          <div className="aviso" role="alert">
            <span>{aviso}</span>
            <button type="button" className="boton-icono" onClick={() => setAviso(null)} aria-label="Cerrar aviso">✕</button>
          </div>
        )}

        <section aria-labelledby="titulo-dispositivos">
          <div className="cabecera-seccion">
            <div>
              <h2 id="titulo-dispositivos" className="titulo-seccion">Dispositivos conectados</h2>
              <p className="texto-suave">Control directo y gestión de dispositivos del hogar</p>
            </div>
            <button type="button" className="boton-primario" onClick={() => setModal({ dispositivo: null })} disabled={!estado}>
              ＋ Nuevo dispositivo
            </button>
          </div>

          {estado ? (
            <div className="cuadricula">
              {estado.devices.map(dispositivo => (
                <DeviceCard key={dispositivo.id} dispositivo={dispositivo} ocupado={ocupado}
                  onAccion={accion} onEditar={d => setModal({ dispositivo: d })} onEliminar={eliminarDispositivo} />
              ))}
              <button type="button" className="tarjeta tarjeta-nueva" onClick={() => setModal({ dispositivo: null })}>
                <span className="tarjeta-nueva-icono" aria-hidden="true">＋</span>
                <strong>Registrar dispositivo</strong>
                <span className="texto-suave">Añade un identificador al analizador</span>
              </button>
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
            <IrPanel analisis={ultimo?.analysis ?? null} />
          </div>
          <div className="columna columna-historial">
            <HistoryPanel historial={estado?.history ?? []} />
          </div>
        </div>
      </main>

      <footer className="pie">SmartHome · Proyecto integrador · Lenguajes y Autómatas II</footer>

      <DeviceModal
        abierto={modal !== null}
        dispositivo={modal?.dispositivo ?? null}
        onCerrar={() => setModal(null)}
        onGuardar={guardarDispositivo}
      />
    </div>
  );
}
