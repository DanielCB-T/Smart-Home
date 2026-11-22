import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const backendDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

export async function analyzeWithPython(command) {
  const executable = process.env.PYTHON || (process.platform === 'win32' ? 'py' : 'python3');
  const args = [
    ...(process.platform === 'win32' && !process.env.PYTHON ? ['-3'] : []),
    '-m', 'app.language.api_bridge'
  ];
  return new Promise((resolve, reject) => {
    const child = spawn(executable, args, { cwd: backendDir, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true });
    let stdout = '';
    let stderr = '';
    let settled = false;
    const finish = (error, data) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      if (error) reject(error);
      else resolve(data);
    };
    const timer = setTimeout(() => {
      child.kill();
      finish(new Error('El analizador Python excedió el tiempo de respuesta.'));
    }, 5000);
    child.on('error', err => finish(new Error(`No se pudo iniciar Python: ${err.message}`)));
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', part => {
      stdout += part;
      if (stdout.length > 100000) {
        child.kill();
        finish(new Error('Respuesta excesiva del analizador.'));
      }
    });
    child.stderr.on('data', part => { stderr = (stderr + part).slice(-1500); });
    child.on('close', code => {
      if (settled) return;
      if (code !== 0) return finish(new Error(`Falló el analizador Python: ${stderr || `código ${code}`}`));
      try { finish(null, JSON.parse(stdout)); }
      catch { finish(new Error('El analizador Python no devolvió JSON válido.')); }
    });
    child.stdin.on('error', () => {});
    child.stdin.end(JSON.stringify({ command }));
  });
}

// El parser produce ASTs; la ejecución actual de Node.js solo soporta
// control de dispositivos y condiciones numéricas de temperatura.
export function executableCommand(ast) {
  if (ast?.tipo !== 'Programa' || ast.instrucciones?.length !== 1)
    return { error: 'Ejecuta una instrucción a la vez.' };
  const node = ast.instrucciones[0];
  if (node.tipo === 'Control')
    return { command: `${node.operacion} ${node.dispositivo}` };
  if (node.tipo === 'Condicional' &&
      node.condicion?.izquierda?.toLowerCase() === 'temperatura' &&
      node.condicion?.derecha?.tipo === 'Numero' &&
      node.accion?.tipo === 'Control') {
    const { izquierda, operador, derecha } = node.condicion;
    const { operacion, dispositivo } = node.accion;
    return { command: `SI ${izquierda} ${operador} ${derecha.valor} ENTONCES ${operacion} ${dispositivo}` };
  }
  return { error: 'La sintaxis es válida, pero esta instrucción aún no tiene ejecución implementada.' };
}
