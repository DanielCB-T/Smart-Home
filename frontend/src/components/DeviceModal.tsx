import { useEffect, useRef, useState, type FormEvent } from 'react';
import type { Dispositivo, DispositivoEntrada, TipoDispositivo } from '../types';

const PATRON_ID = /^[A-Za-z_][A-Za-z0-9_]{0,39}$/;

const tipos: { valor: TipoDispositivo; texto: string }[] = [
  { valor: 'luz', texto: 'Iluminación (luz)' },
  { valor: 'ventilador', texto: 'Ventilación (ventilador)' },
  { valor: 'puerta', texto: 'Acceso (puerta)' },
  { valor: 'alarma', texto: 'Seguridad (alarma)' }
];

// Sugiere un identificador válido a partir del nombre: "Luz del pasillo" → "luz_del_pasillo".
export function sugerirIdentificador(nombre: string): string {
  const limpio = nombre
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 40);
  if (!limpio) return '';
  return /^[0-9]/.test(limpio) ? `dev_${limpio}`.slice(0, 40) : limpio;
}

interface Props {
  abierto: boolean;
  dispositivo: Dispositivo | null; // null = crear
  onCerrar: () => void;
  onGuardar: (datos: DispositivoEntrada, idOriginal: string | null) => Promise<boolean>;
}

export default function DeviceModal({ abierto, dispositivo, onCerrar, onGuardar }: Props) {
  const editando = dispositivo !== null;
  const [nombre, setNombre] = useState('');
  const [identificador, setIdentificador] = useState('');
  const [tipo, setTipo] = useState<TipoDispositivo>('luz');
  const [idManual, setIdManual] = useState(false);
  const [error, setError] = useState('');
  const [guardando, setGuardando] = useState(false);
  const primerCampo = useRef<HTMLInputElement>(null);

  // Reinicia el formulario cada vez que se abre.
  useEffect(() => {
    if (!abierto) return;
    setNombre(dispositivo?.name ?? '');
    setIdentificador(dispositivo?.id ?? '');
    setTipo(dispositivo?.type ?? 'luz');
    setIdManual(editando);
    setError('');
    setGuardando(false);
    const temporizador = window.setTimeout(() => primerCampo.current?.focus(), 30);
    return () => window.clearTimeout(temporizador);
  }, [abierto, dispositivo, editando]);

  // Cierra con Escape y bloquea el scroll de la página mientras el modal está abierto.
  useEffect(() => {
    if (!abierto) return;
    const alPresionar = (e: KeyboardEvent) => { if (e.key === 'Escape' && !guardando) onCerrar(); };
    document.addEventListener('keydown', alPresionar);
    const scroll = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', alPresionar);
      document.body.style.overflow = scroll;
    };
  }, [abierto, guardando, onCerrar]);

  if (!abierto) return null;

  function cambiarNombre(valor: string) {
    setNombre(valor);
    if (!idManual) setIdentificador(sugerirIdentificador(valor));
  }

  function validar(): string | null {
    if (!nombre.trim()) return 'Escribe un nombre para el dispositivo.';
    if (!PATRON_ID.test(identificador)) {
      return 'El identificador debe empezar con letra o guion bajo y usar solo letras, números o guion bajo (máximo 40).';
    }
    return null;
  }

  async function enviar(evento: FormEvent) {
    evento.preventDefault();
    const problema = validar();
    if (problema) { setError(problema); return; }
    setError('');
    setGuardando(true);
    const exito = await onGuardar({ id: identificador, name: nombre.trim(), type: tipo }, dispositivo?.id ?? null);
    setGuardando(false);
    if (exito) onCerrar();
  }

  return (
    <div className="modal-fondo" onMouseDown={e => { if (e.target === e.currentTarget && !guardando) onCerrar(); }}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby="titulo-modal">
        <header className="modal-cabecera">
          <div className="modal-titulo">
            <span className="modal-icono" aria-hidden="true">{editando ? '✎' : '＋'}</span>
            <div>
              <h2 id="titulo-modal">{editando ? 'Editar dispositivo' : 'Registrar dispositivo'}</h2>
              <p className="texto-suave">Tabla de símbolos del compilador</p>
            </div>
          </div>
          <button type="button" className="boton-icono" onClick={onCerrar} disabled={guardando} aria-label="Cerrar">✕</button>
        </header>

        <form className="modal-cuerpo" onSubmit={enviar} noValidate>
          <div className="campo">
            <label htmlFor="campo-nombre">Nombre del dispositivo</label>
            <input id="campo-nombre" ref={primerCampo} type="text" maxLength={60} value={nombre}
              placeholder="Ej. Lámpara de estudio" onChange={e => cambiarNombre(e.target.value)} />
          </div>

          <div className="campo">
            <label htmlFor="campo-id">Identificador en el lenguaje</label>
            <div className="entrada-prefijo">
              <span aria-hidden="true">ID_</span>
              <input id="campo-id" type="text" maxLength={40} value={identificador} spellCheck={false}
                placeholder="luz_estudio" aria-describedby="ayuda-id"
                onChange={e => { setIdManual(true); setIdentificador(e.target.value.trim()); }} />
            </div>
            <p id="ayuda-id" className="ayuda">
              Úsalo en las instrucciones, por ejemplo <code>ENCENDER {identificador || 'luz_estudio'}</code>.
            </p>
          </div>

          <div className="campo">
            <label htmlFor="campo-tipo">Categoría</label>
            <select id="campo-tipo" value={tipo} onChange={e => setTipo(e.target.value as TipoDispositivo)}>
              {tipos.map(t => <option key={t.valor} value={t.valor}>{t.texto}</option>)}
            </select>
          </div>

          {error && <p className="campo-error" role="alert">{error}</p>}

          <footer className="modal-acciones">
            <button type="button" className="boton-secundario" onClick={onCerrar} disabled={guardando}>Cancelar</button>
            <button type="submit" className="boton-primario" disabled={guardando}>
              {guardando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Registrar'}
            </button>
          </footer>
        </form>
      </div>
    </div>
  );
}
