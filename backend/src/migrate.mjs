import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { db } from './database.mjs';
const dir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../db/migrations');
db.exec('CREATE TABLE IF NOT EXISTS schema_migrations (name TEXT PRIMARY KEY, applied_at TEXT NOT NULL)');
for (const file of fs.readdirSync(dir).filter(x => x.endsWith('.sql')).sort()) {
  if (db.prepare('SELECT 1 FROM schema_migrations WHERE name = ?').get(file)) continue;
  db.exec('BEGIN IMMEDIATE');
  try {
    db.exec(fs.readFileSync(path.join(dir, file), 'utf8'));
    db.prepare('INSERT INTO schema_migrations VALUES (?, ?)').run(file, new Date().toISOString());
    db.exec('COMMIT');
    console.log(`Migración aplicada: ${file}`);
  } catch (error) { db.exec('ROLLBACK'); throw error; }
}
db.close();
