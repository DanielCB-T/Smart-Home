import { DatabaseSync } from 'node:sqlite';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const filename = path.resolve(process.env.SMART_HOME_DB || path.join(root, 'data', 'smarthome.sqlite'));
fs.mkdirSync(path.dirname(filename), { recursive: true });
export const db = new DatabaseSync(filename);
db.exec('PRAGMA foreign_keys = ON; PRAGMA busy_timeout = 5000;');

export function snapshot() {
  const devices = db.prepare('SELECT id, name, type, enabled FROM devices ORDER BY rowid').all()
    .map(({ id, name, type, enabled }) => type === 'puerta'
      ? ({ id, name, type, open: Boolean(enabled) })
      : ({ id, name, type, on: Boolean(enabled) }));
  const temperature = db.prepare("SELECT value FROM settings WHERE key = 'temperature'").get()?.value ?? 28;
  const history = db.prepare('SELECT * FROM history ORDER BY id DESC LIMIT 100').all()
    .map(row => ({ ...row, success: Boolean(row.success), skipped: Boolean(row.skipped) }));
  return { devices, temperature, history };
}
export function record(command, message, success, skipped = false) {
  const timestamp = new Date().toISOString();
  const info = db.prepare('INSERT INTO history(timestamp, command, message, success, skipped) VALUES (?, ?, ?, ?, ?)')
    .run(timestamp, command, message, Number(success), Number(skipped));
  const id = Number(info.lastInsertRowid);
  return { id, timestamp, command, message, success, skipped };
}
export function assertMigrated() {
  const table = db.prepare("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'devices'").get();
  if (!table) throw new Error('Base de datos sin migraciones. Ejecuta npm run db:setup.');
}
