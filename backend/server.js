const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { URL } = require('node:url');

const PORT = Number(process.env.PORT || 3001);
const FRONTEND = path.resolve(__dirname, '../frontend');

const devices = [
  { id: 'luz_sala', name: 'Luz de sala', type: 'luz', on: false },
  { id: 'luz_cocina', name: 'Luz de cocina', type: 'luz', on: false },
  { id: 'ventilador1', name: 'Ventilador 1', type: 'ventilador', on: false },
];
let temperature = 28;
let nextId = 1;
const history = [];

const allowedActions = {
  luz: { ENCENDER: 'on', APAGAR: 'on' },
  ventilador: { ENCENDER: 'on', APAGAR: 'on' },
  puerta: { ABRIR: 'open', CERRAR: 'open' },
  alarma: { ACTIVAR: 'on', DESACTIVAR: 'on' },
};
const truthyActions = new Set(['ENCENDER', 'ABRIR', 'ACTIVAR']);

function snapshot() { return { devices: devices.map(d => ({ ...d })), temperature, history: [...history] }; }
function record(command, message, success, skipped = false) {
  const entry = { id: nextId++, timestamp: new Date().toISOString(), command, message, success, skipped };
  history.unshift(entry);
  if (history.length > 100) history.pop();
  return entry;
}
function normalize(text) { return text.trim().normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase(); }

function executePlain(command) {
  const match = /^([A-Z]+)\s+([A-Z0-9_]+)$/.exec(normalize(command));
  if (!match) throw new Error('Sintaxis incorrecta. Ejemplo: ENCENDER luz_sala');
  const [, action, id] = match;
  const device = devices.find(d => d.id.toUpperCase() === id);
  if (!device) throw new Error(`El dispositivo "${id.toLowerCase()}" no existe.`);
  const property = allowedActions[device.type][action];
  if (!property) throw new Error(`La acción ${action} no es compatible con ${device.type}.`);
  const nextValue = truthyActions.has(action);
  if (device[property] === nextValue) throw new Error(`El dispositivo "${device.id}" ya está en ese estado.`);
  device[property] = nextValue;
  return `${action} ${device.id}: operación realizada.`;
}
function evaluateCondition(raw) {
  const match = /^TEMPERATURA\s*(>=|<=|>|<|==|=|!=)\s*(-?\d+(?:\.\d+)?)$/.exec(normalize(raw));
  if (!match) throw new Error('Condición no válida. Ejemplo: SI temperatura > 30 ENTONCES ENCENDER ventilador1');
  const [, op, number] = match;
  const value = Number(number);
  return ({ '>': () => temperature > value, '<': () => temperature < value,
    '>=': () => temperature >= value, '<=': () => temperature <= value,
    '=': () => temperature === value, '==': () => temperature === value,
    '!=': () => temperature !== value })[op]();
}
function executeCommand(raw) {
  const command = String(raw || '').trim();
  if (!command) return record('', 'Escribe una instrucción.', false);
  try {
    const conditional = /^SI\s+(.+?)\s+ENTONCES\s+(.+)$/i.exec(command);
    let message;
    let skipped = false;
    if (conditional) {
      if (evaluateCondition(conditional[1])) message = `Condición verdadera. ${executePlain(conditional[2])}`;
      else { message = 'Condición falsa. No se ejecutó ninguna acción.'; skipped = true; }
    } else if (/^SI\b/i.test(command)) {
      throw new Error('Sintaxis condicional incorrecta. Usa SI temperatura > 30 ENTONCES ENCENDER ventilador1');
    } else message = executePlain(command);
    return record(command, message, true, skipped);
  } catch (error) { return record(command, error.message, false); }
}
function json(res, status, body) {
  res.writeHead(status, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(JSON.stringify(body));
}
function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => { data += chunk; if (data.length > 10000) { reject(new Error('Solicitud demasiado grande.')); req.destroy(); } });
    req.on('end', () => { try { resolve(JSON.parse(data || '{}')); } catch { reject(new Error('JSON no válido.')); } });
    req.on('error', reject);
  });
}
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.ico': 'image/x-icon' };
const server = http.createServer(async (req, res) => {
  const route = new URL(req.url, 'http://localhost').pathname;
  try {
    if (req.method === 'GET' && route === '/api/state') return json(res, 200, snapshot());
    if (req.method === 'POST' && route === '/api/command') {
      const body = await readBody(req);
      if (typeof body.command !== 'string' || body.command.length > 300) return json(res, 400, { error: 'El comando debe ser un texto de hasta 300 caracteres.' });
      const result = executeCommand(body.command);
      return json(res, result.success ? 200 : 422, { result, ...snapshot() });
    }
    if (req.method === 'PUT' && route === '/api/temperature') {
      const body = await readBody(req);
      if (typeof body.temperature !== 'number' || !Number.isFinite(body.temperature) || body.temperature < -20 || body.temperature > 60)
        return json(res, 400, { error: 'La temperatura debe estar entre -20 y 60 °C.' });
      temperature = body.temperature;
      record(`TEMPERATURA ${temperature}`, `Temperatura ajustada a ${temperature} °C.`, true);
      return json(res, 200, snapshot());
    }
    if (route.startsWith('/api/')) return json(res, 404, { error: 'Ruta no encontrada.' });
    if (req.method !== 'GET') return json(res, 405, { error: 'Método no permitido.' });
    const requestPath = route === '/' ? '/index.html' : route;
    const filename = path.resolve(FRONTEND, '.' + decodeURIComponent(requestPath));
    if (!filename.startsWith(FRONTEND + path.sep)) return json(res, 403, { error: 'Acceso denegado.' });
    fs.readFile(filename, (err, data) => {
      if (err) return json(res, 404, { error: 'Archivo no encontrado.' });
      res.writeHead(200, { 'Content-Type': MIME[path.extname(filename)] || 'application/octet-stream' });
      res.end(data);
    });
  } catch (err) { if (!res.writableEnded) json(res, 400, { error: err.message || 'Error interno.' }); }
});
server.listen(PORT, () => console.log(`SmartHome disponible en http://localhost:${PORT}`));
