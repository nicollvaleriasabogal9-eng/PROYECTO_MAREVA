const ID_PAQUETE = document.getElementById('reservaData').dataset.idPaquete;

// ---------- Generación dinámica de campos por viajero ----------
function actualizarViajeros() {
  const adultos = parseInt(document.getElementById('inputAdultos').value) || 0;
  const menores = parseInt(document.getElementById('inputMenores').value) || 0;
  const total = adultos + menores;
  const contenedor = document.getElementById('viajerosContainer');
  contenedor.innerHTML = '<h2 style="margin-bottom:var(--space-4);font-size:var(--text-xl)">🪪 Datos de cada viajero</h2>';

  for (let i = 0; i < total; i++) {
    contenedor.innerHTML += `
      <div class="grid-3" style="margin-bottom:var(--space-3)">
        <div class="form-group">
          <label class="form-label">Nombre viajero ${i + 1}</label>
          <input type="text" name="viajero_nombre_${i}" class="form-input" required>
        </div>
        <div class="form-group">
          <label class="form-label">Apellido</label>
          <input type="text" name="viajero_apellido_${i}" class="form-input" required>
        </div>
        <div class="form-group">
          <label class="form-label">N° Documento</label>
          <input type="text" name="viajero_num_doc_${i}" class="form-input" required>
        </div>
      </div>`;
  }
}
document.getElementById('inputAdultos').addEventListener('input', actualizarViajeros);
document.getElementById('inputMenores').addEventListener('input', actualizarViajeros);
actualizarViajeros();

// ---------- Calendario verde/rojo ----------
async function cargarCalendario() {
  console.log("Cargando calendario...");
  const resp = await fetch(`/api/paquetes/${ID_PAQUETE}/disponibilidad`);
  const data = await resp.json();

  const inicio = data.fecha_inicio ? new Date(data.fecha_inicio + 'T00:00:00') : null;
  const fin = data.fecha_fin ? new Date(data.fecha_fin + 'T00:00:00') : null;
  const hayCupos = data.cupos_disponibles > 0;

  if (!inicio || !fin) {
    document.getElementById('calendario').innerHTML = '<p class="text-muted">Este paquete no tiene fechas fijas, contacta a tu asesor.</p>';
    return;
  }

  const cont = document.getElementById('calendario');
  cont.style.display = 'grid';
  cont.style.gridTemplateColumns = 'repeat(7, 1fr)';
  cont.style.gap = '4px';
  cont.style.maxWidth = '420px';

  const cursor = new Date(inicio);
  while (cursor <= fin) {
    const fechaStr = cursor.toISOString().slice(0, 10);
    const disponible = hayCupos;

    const dia = document.createElement('button');
    dia.type = 'button';
    dia.textContent = cursor.getDate();
    dia.style.padding = '10px';
    dia.style.borderRadius = 'var(--radius-sm)';
    dia.style.border = 'none';
    dia.style.fontSize = 'var(--text-xs)';
    dia.style.cursor = disponible ? 'pointer' : 'not-allowed';
    dia.style.background = disponible ? '#10B981' : '#EF4444';
    dia.style.color = '#fff';
    dia.disabled = !disponible;

    dia.addEventListener('click', () => {
      document.querySelectorAll('#calendario button').forEach(b => b.style.outline = 'none');
      dia.style.outline = '3px solid var(--blue)';
      document.getElementById('fechaInicioInput').value = fechaStr;
      document.getElementById('fechaSeleccionadaTexto').textContent = 'Fecha seleccionada: ' + fechaStr;
    });

    cont.appendChild(dia);
    cursor.setDate(cursor.getDate() + 1);
  }

  if (!hayCupos) {
    document.getElementById('fechaSeleccionadaTexto').textContent = '⚠️ Este paquete está agotado para las fechas mostradas.';
  }
}
cargarCalendario();

document.getElementById('formReserva').addEventListener('submit', (e) => {
  if (!document.getElementById('fechaInicioInput').value) {
    e.preventDefault();
    alert('Por favor selecciona una fecha de viaje en el calendario.');
  }
});