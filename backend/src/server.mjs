import http from 'node:http';
import { URL, fileURLToPath } from 'node:url';
import path from 'node:path';
import { db, snapshot, record, assertMigrated } from './database.mjs';
import { executeCommand, changeDevice } from './commands.mjs';
import { analyzeWithPython, executableCommand } from './python_bridge.mjs';

const port = Number(process.env.PORT || 3001);
const corsHeaders = { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' };
function json(res, status, payload) { res.writeHead(status, corsHeaders); res.end(JSON.stringify(payload)); }
async function body(req) {
  let text = '';
  for await (const chunk of req) {
    text += chunk;
    if (text.length > 10000) { const e = new Error('Solicitud demasiado grande.'); e.status = 413; throw e; }
  }
  try { return JSON.parse(text || '{}'); }
  catch { const e = new Error('JSON no válido.'); e.status = 400; throw e; }
}
function deviceToJSON(row) {
  return row.type === 'puerta' ? { id: row.id, name: row.name, type: row.type, open: Boolean(row.enabled) }
    : { id: row.id, name: row.name, type: row.type, on: Boolean(row.enabled) };
}
function getDevice(id) {
  const row = db.prepare('SELECT * FROM devices WHERE id = ?').get(id);
  return row ? deviceToJSON(row) : null;
}
export function makeServer() {
  assertMigrated();
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const route = url.pathname;
    try {
      if (req.method === 'GET' && route === '/api/health') return json(res, 200, { status: 'ok' });
      if (req.method === 'GET' && route === '/api/state') return json(res, 200, snapshot());
      if (req.method === 'GET' && route === '/api/devices') return json(res, 200, snapshot().devices);
      if (req.method === 'GET' && route === '/api/history') {
        const limit = Number(url.searchParams.get('limit') || 100);
        if (!Number.isInteger(limit) || limit < 1 || limit > 100) return json(res, 400, { error: 'limit debe estar entre 1 y 100.' });
        return json(res, 200, snapshot().history.slice(0, limit));
      }
      if (req.method === 'GET' && route === '/api/temperature') return json(res, 200, { temperature: snapshot().temperature });
      const deviceMatch = /^\/api\/devices\/([a-zA-Z0-9_]+)$/.exec(route);
      if (deviceMatch) {
        const id = deviceMatch[1];
        const device = getDevice(id);
        if (!device) return json(res, 404, { error: 'Dispositivo no encontrado.' });
        if (req.method === 'GET') return json(res, 200, device);
        if (req.method === 'PATCH') {
          const input = await body(req);
          if (typeof input.action !== 'string' || !/^[A-Za-z]+$/.test(input.action)) return json(res, 400, { error: 'Envía una acción válida.' });
          const result = changeDevice(id, input.action.toUpperCase());
          return json(res, result.success ? 200 : 422, { result, ...snapshot() });
        }
      }
      if (req.method === 'POST' && (route === '/api/command' || route === '/api/analyze')) {
        const input = await body(req);
        if (typeof input.command !== 'string' || !input.command.trim() || input.command.length > 300)
          return json(res, 400, { error: 'El comando debe ser texto de 1 a 300 caracteres.' });
        let analysis;
        try { analysis = await analyzeWithPython(input.command); }
        catch (error) { return json(res, 503, { error: error.message }); }
        if (route === '/api/analyze') return json(res, analysis.ok ? 200 : 422, analysis);
        if (!analysis.ok) {
          const message = analysis.error?.mensaje || 'Instrucción inválida.';
          const result = record(input.command, message, false);
          return json(res, 422, { result, analysis, ...snapshot() });
        }
        const executable = executableCommand(analysis.ast);
        if (executable.error) {
          const result = record(input.command, executable.error, false);
          return json(res, 422, { result, analysis, ...snapshot() });
        }
        const result = executeCommand(executable.command);
        return json(res, result.success ? 200 : 422, { result, analysis, ...snapshot() });
      }
      if (req.method === 'PUT' && route === '/api/temperature') {
        const input = await body(req);
        if (typeof input.temperature !== 'number' || !Number.isFinite(input.temperature) || input.temperature < -20 || input.temperature > 60)
          return json(res, 400, { error: 'La temperatura debe estar entre -20 y 60 °C.' });
        db.prepare("UPDATE settings SET value = ? WHERE key = 'temperature'").run(input.temperature);
        record(`TEMPERATURA ${input.temperature}`, `Temperatura ajustada a ${input.temperature} °C.`, true);
        return json(res, 200, snapshot());
      }
      return json(res, 404, { error: 'Ruta no encontrada.' });
    } catch (err) { return json(res, err.status || 500, { error: err.status ? err.message : 'Error interno del servidor.' }); }
  });
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  makeServer().listen(port, () => console.log(`API SmartHome: http://localhost:${port}`));
}
