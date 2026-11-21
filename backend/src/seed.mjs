import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { db, assertMigrated } from './database.mjs';
assertMigrated();
const dir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../db/seeders');
for (const file of fs.readdirSync(dir).filter(x => x.endsWith('.sql')).sort()) {
  db.exec(fs.readFileSync(path.join(dir, file), 'utf8'));
  console.log(`Seeder ejecutado: ${file}`);
}
db.close();
