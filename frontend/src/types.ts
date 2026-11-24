export type TipoDispositivo = 'luz' | 'ventilador' | 'puerta' | 'alarma';

export interface Dispositivo {
  id: string;
  name: string;
  type: TipoDispositivo;
  estado: string;
  on?: boolean;
  open?: boolean;
}

export interface DispositivoEntrada {
  id: string;
  name: string;
  type: TipoDispositivo;
}

export interface Registro {
  id: number;
  timestamp: string;
  command: string;
  message: string;
  success: boolean;
  skipped: boolean;
}

export interface ErrorLenguaje {
  tipo: string;
  mensaje: string;
  linea: number;
  columna: number;
}

export interface Analisis {
  ok: boolean;
  ast?: unknown;
  ir?: { version?: string; instrucciones: Record<string, unknown>[] };
  ir_tac?: string[];
  error?: ErrorLenguaje;
}

export interface Estado {
  devices: Dispositivo[];
  temperature: number;
  history: Registro[];
}

export interface RespuestaComando extends Estado {
  result: Registro;
  analysis: Analisis;
}
