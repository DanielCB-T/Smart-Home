import Swal from 'sweetalert2';

// Colores tomados de las variables CSS del tema activo, para que las alertas
// combinen con la interfaz en modo claro y oscuro.
function base() {
  const estilo = getComputedStyle(document.documentElement);
  const variable = (nombre: string) => estilo.getPropertyValue(nombre).trim();
  return {
    background: variable('--superficie'),
    color: variable('--texto'),
    confirmButtonColor: variable('--primario'),
    cancelButtonColor: variable('--texto-suave'),
    denyButtonColor: variable('--error'),
    error: variable('--error'),
    buttonsStyling: true,
    customClass: { popup: 'alerta-smarthome' }
  };
}

export function notificarExito(titulo: string, texto?: string): void {
  void Swal.fire({
    ...base(),
    toast: true,
    position: 'top-end',
    icon: 'success',
    title: titulo,
    text: texto,
    showConfirmButton: false,
    timer: 2600,
    timerProgressBar: true
  });
}

export function notificarError(texto: string): void {
  void Swal.fire({ ...base(), icon: 'error', title: 'No se pudo completar', text: texto, confirmButtonText: 'Entendido' });
}

export async function confirmarEliminacion(nombre: string, id: string): Promise<boolean> {
  const colores = base();
  const resultado = await Swal.fire({
    ...colores,
    icon: 'warning',
    title: '¿Eliminar dispositivo?',
    html: `<p>Se eliminará <strong>${escapar(nombre)}</strong> (<code>${escapar(id)}</code>) de la tabla de símbolos.</p>
           <p class="alerta-nota">Las condiciones que lo usen dejarán de funcionar.</p>`,
    showCancelButton: true,
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
    confirmButtonColor: colores.error,
    focusCancel: true
  });
  return resultado.isConfirmed;
}

function escapar(texto: string): string {
  return texto.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] ?? c);
}
