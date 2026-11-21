CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  type TEXT NOT NULL CHECK(type IN ('luz', 'ventilador', 'puerta', 'alarma')),
  enabled INTEGER NOT NULL DEFAULT 0 CHECK(enabled IN (0, 1))
);
CREATE TABLE IF NOT EXISTS settings (
  key TEXT PRIMARY KEY,
  value REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  command TEXT NOT NULL,
  message TEXT NOT NULL,
  success INTEGER NOT NULL CHECK(success IN (0, 1)),
  skipped INTEGER NOT NULL DEFAULT 0 CHECK(skipped IN (0, 1))
);
CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp DESC);
