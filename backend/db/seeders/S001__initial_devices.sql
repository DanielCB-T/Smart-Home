INSERT OR IGNORE INTO devices(id, name, type, enabled) VALUES
  ('luz_sala', 'Luz de sala', 'luz', 0),
  ('luz_cocina', 'Luz de cocina', 'luz', 0),
  ('ventilador1', 'Ventilador 1', 'ventilador', 0),
  ('puerta_principal', 'Puerta principal', 'puerta', 0),
  ('alarma1', 'Alarma principal', 'alarma', 0);
INSERT OR IGNORE INTO settings(key, value) VALUES ('temperature', 28);
