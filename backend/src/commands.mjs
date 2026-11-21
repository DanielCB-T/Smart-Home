import { db, record } from './database.mjs';
const allowed = {
  luz: ['ENCENDER', 'APAGAR'], ventilador: ['ENCENDER', 'APAGAR'],
  puerta: ['ABRIR', 'CERRAR'], alarma: ['ACTIVAR', 'DESACTIVAR']
};
const positive = new Set(['ENCENDER', 'ABRIR', 'ACTIVAR']);
function normalize(value) {
  return value.trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase();
}
function executePlain(text) {
  const match = /^([A-Z]+)\s+([A-Z0-9_]+)$/.exec(normalize(text));
  if (!match) throw new Error('Sintaxis incorrecta. Ejemplo: ENCENDER luz_sala');
  const [, action, id] = match;
  const device = db.prepare('SELECT * FROM devices WHERE UPPER(id) = ?').get(id);
  if (!device) throw new Error(`El dispositivo "${id.toLowerCase()}" no existe.`);
  if (!allowed[device.type].includes(action)) throw new Error(`La acción ${action} no es compatible con ${device.type}.`);
  const next = Number(positive.has(action));
  if (device.enabled === next) throw new Error(`El dispositivo "${device.id}" ya está en ese estado.`);
  db.prepare('UPDATE devices SET enabled = ? WHERE id = ?').run(next, device.id);
  return `${action} ${device.id}: operación realizada.`;
}
function evaluateCondition(text) {
  const match = /^TEMPERATURA\s*(>=|<=|>|<|==|=|!=)\s*(-?\d+(?:\.\d+)?)$/.exec(normalize(text));
  if (!match) throw new Error('Condición no válida. Ejemplo: SI temperatura > 30 ENTONCES ENCENDER ventilador1');
  const [, operator, raw] = match;
  const temperature = db.prepare("SELECT value FROM settings WHERE key = 'temperature'").get().value;
  const number = Number(raw);
  switch (operator) {
    case '>': return temperature > number;
    case '<': return temperature < number;
    case '>=': return temperature >= number;
    case '<=': return temperature <= number;
    case '=': case '==': return temperature === number;
    case '!=': return temperature !== number;
  }
}
export function executeCommand(raw) {
  const command = typeof raw === 'string' ? raw.trim() : '';
  if (!command) return record('', 'Escribe una instrucción.', false);
  try {
    const conditional = /^SI\s+(.+?)\s+ENTONCES\s+(.+)$/i.exec(command);
    let message, skipped = false;
    if (conditional) {
      if (evaluateCondition(conditional[1])) message = `Condición verdadera. ${executePlain(conditional[2])}`;
      else { message = 'Condición falsa. No se ejecutó ninguna acción.'; skipped = true; }
    } else if (/^SI\b/i.test(command)) {
      throw new Error('Sintaxis condicional incorrecta. Usa SI temperatura > 30 ENTONCES ENCENDER ventilador1');
    } else message = executePlain(command);
    return record(command, message, true, skipped);
  } catch (error) { return record(command, error.message, false); }
}
export function changeDevice(id, action) {
  return executeCommand(`${action} ${id}`);
}
