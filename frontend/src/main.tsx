import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { aplicarTema, temaInicial } from './tema';
import './styles.css';

// Aplica el tema antes de pintar para evitar un destello del modo contrario.
aplicarTema(temaInicial());

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><App /></React.StrictMode>
);
