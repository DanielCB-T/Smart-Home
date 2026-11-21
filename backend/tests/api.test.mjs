import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';

const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'smarthome-test-'));
process.env.SMART_HOME_DB = path.join(tempDir, 'test.sqlite');
const backendDir = path.resolve(import.meta.dirname, '..');
for (const script of ['migrate.mjs', 'seed.mjs']) {
  const result = spawnSync(process.execPath, [path.join(backendDir, 'src', script)], { env: process.env, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
}
const { makeServer } = await import('../src/server.mjs');
const server = makeServer();
let base;
before(async () => { await new Promise(resolve => server.listen(0, '127.0.0.1', resolve)); base = `http://127.0.0.1:${server.address().port}`; });
after(async () => { await new Promise(resolve => server.close(resolve)); fs.rmSync(tempDir, { recursive: true, force: true }); });
async function send(route, method = 'GET', payload) {
  const response = await fetch(base + route, { method, headers: { 'Content-Type': 'application/json' }, body: payload === undefined ? undefined : JSON.stringify(payload) });
  return { status: response.status, data: await response.json() };
}
test('5 dispositivos semilla y temperatura inicial', async () => {
  const { status, data } = await send('/api/state');
  assert.equal(status, 200); assert.equal(data.devices.length, 5); assert.equal(data.temperature, 28);
});
test('encender dispositivo y consultar por id', async () => {
  const action = await send('/api/command', 'POST', { command: 'ENCENDER luz_sala' });
  assert.equal(action.status, 200); assert.equal(action.data.result.success, true);
  const device = await send('/api/devices/luz_sala'); assert.equal(device.data.on, true);
});
test('acción incompatible y dispositivo inexistente', async () => {
  assert.equal((await send('/api/command', 'POST', { command: 'ABRIR luz_sala' })).status, 422);
  assert.equal((await send('/api/devices/desconocido')).status, 404);
});
test('temperatura y condicional verdadera', async () => {
  assert.equal((await send('/api/temperature', 'PUT', { temperature: 35 })).status, 200);
  const run = await send('/api/command', 'POST', { command: 'SI temperatura > 30 ENTONCES ENCENDER ventilador1' });
  assert.equal(run.data.result.success, true); assert.equal(run.data.devices.find(d => d.id === 'ventilador1').on, true);
});
test('condición falsa se omite y registra', async () => {
  const run = await send('/api/command', 'POST', { command: 'SI temperatura < 20 ENTONCES APAGAR ventilador1' });
  assert.equal(run.data.result.skipped, true);
  assert.equal((await send('/api/history')).data[0].skipped, true);
});
test('PATCH dispositivo, validación de temperatura', async () => {
  assert.equal((await send('/api/devices/puerta_principal', 'PATCH', { action: 'ABRIR' })).status, 200);
  assert.equal((await send('/api/temperature', 'PUT', { temperature: 100 })).status, 400);
});
