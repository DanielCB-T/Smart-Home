const $ = selector => document.querySelector(selector);
const grid = $('#device-grid');
const historyList = $('#history');
const resultBox = $('#result');
const icons = { luz: '☀', ventilador: '✺', puerta: '▣', alarma: '♢' };
const descriptions = { luz: 'Iluminación inteligente', ventilador: 'Ventilación del hogar', puerta: 'Control de acceso', alarma: 'Sistema de seguridad' };
const names = { luz: ['Encendida','Apagada'], ventilador: ['Encendido','Apagado'], puerta: ['Abierta','Cerrada'], alarma: ['Activada','Desactivada'] };

function render(state) {
  $('#count-total').textContent = state.devices.length;
  $('#count-active').textContent = state.devices.filter(d => d.type === 'puerta' ? d.open : d.on).length;
  $('#temp-value').textContent = state.temperature;
  $('#temperature').value = state.temperature;
  grid.replaceChildren();
  state.devices.forEach(device => {
    const active = device.type === 'puerta' ? device.open : device.on;
    const card = document.createElement('article');
    card.className = `device${active ? ' active' : ''}`;
    card.innerHTML = `<div class="device-top"><span class="device-icon"></span><span class="status"></span></div><h3></h3><small></small>`;
    card.querySelector('.device-icon').textContent = icons[device.type];
    card.querySelector('.status').textContent = names[device.type][active ? 0 : 1];
    card.querySelector('h3').textContent = device.name;
    card.querySelector('small').textContent = `${descriptions[device.type]} · ${device.id}`;
    grid.append(card);
  });
  historyList.replaceChildren();
  if (!state.history.length) { const p = document.createElement('p'); p.className = 'empty'; p.textContent = 'Aún no hay actividad.'; historyList.append(p); }
  state.history.forEach(entry => {
    const item = document.createElement('div');
    item.className = `history-item${!entry.success ? ' failed' : entry.skipped ? ' skipped' : ''}`;
    item.innerHTML = '<span class="history-icon"></span><div class="history-text"><strong></strong><p></p><time></time></div>';
    item.querySelector('.history-icon').textContent = !entry.success ? '✕' : entry.skipped ? '○' : '✓';
    item.querySelector('strong').textContent = entry.command;
    item.querySelector('p').textContent = entry.message;
    item.querySelector('time').textContent = new Date(entry.timestamp).toLocaleString('es-MX');
    historyList.append(item);
  });
}
async function request(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok && !data.result) throw new Error(data.error || 'Error al contactar el servidor.');
  return data;
}
function showError(message) { $('#alert').textContent = message; $('#alert').classList.add('visible'); }
function clearError() { $('#alert').classList.remove('visible'); }
async function command(text) {
  clearError();
  try {
    const data = await request('/api/command', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ command: text }) });
    render(data);
    resultBox.textContent = data.result.message;
    resultBox.classList.toggle('error', !data.result.success);
  } catch (error) { showError(error.message); }
}
$('#command-form').addEventListener('submit', async event => {
  event.preventDefault();
  const input = $('#command');
  await command(input.value);
  input.value = '';
  input.focus();
});
document.querySelectorAll('.example').forEach(button => button.addEventListener('click', () => {
  $('#command').value = button.dataset.command;
  $('#command').focus();
}));
$('#set-temp').addEventListener('click', async () => {
  clearError();
  const raw = $('#temperature').value;
  if (raw.trim() === '') { showError('Ingresa una temperatura.'); return; }
  try {
    const data = await request('/api/temperature', { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ temperature: Number(raw) }) });
    render(data);
    resultBox.textContent = `Temperatura ajustada a ${data.temperature} °C.`;
    resultBox.classList.remove('error');
  } catch (error) { showError(error.message); }
});
request('/api/state').then(render).catch(error => showError(error.message));
