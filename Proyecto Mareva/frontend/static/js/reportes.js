
  function mostrarTab(tabId) {
   
    document.querySelectorAll('.tab-content').forEach(tab => {
      tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });

   
    document.getElementById(tabId).classList.add('active');
    event.target.classList.add('active');

    if (tabId === 'reporte-reservas') {
      cargarReservas();
    } else if (tabId === 'reporte-paquetes') {
      cargarPaquetes();
    } else if (tabId === 'reporte-canceladas') {
      cargarCanceladas();
    } else if (tabId === 'reporte-ingresos') {
      cargarIngresos();
    } else if (tabId === 'reporte-destinos') {
      cargarDestinos();
    }
  }

  function obtenerFechas() {
    return {
      inicio: document.getElementById('fecha-inicio').value,
      fin: document.getElementById('fecha-fin').value
    };
  }

  function mostrarError(seccion, mensaje) {
    const elemento = document.getElementById(`error-${seccion}`);
    elemento.textContent = mensaje;
    elemento.classList.add('active');
  }

  function ocultarError(seccion) {
    const elemento = document.getElementById(`error-${seccion}`);
    elemento.classList.remove('active');
  }

  function mostrarCargando(seccion) {
    document.getElementById(`loading-${seccion}`).classList.add('active');
  }

  function ocultarCargando(seccion) {
    document.getElementById(`loading-${seccion}`).classList.remove('active');
  }

  function formatearMoneda(valor) {
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP'
    }).format(valor);
  }

  function obtenerBadgeEstado(estado) {
    const badges = {
      'completada': 'badge-completed',
      'pendiente a pago': 'badge-pending',
      'cancelada': 'badge-cancelled',
      'solicitada': 'badge-solicitud'
    };
    return badges[estado] || 'badge-solicitud';
  }

  function cargarReservas() {
    const fechas = obtenerFechas();
    const estado = document.getElementById('filtro-estado').value;

    if (!fechas.inicio || !fechas.fin) {
      mostrarError('reservas', 'Por favor selecciona rango de fechas');
      return;
    }

    mostrarCargando('reservas');
    ocultarError('reservas');

    let url = `/api/reportes/reservas?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`;
    if (estado) url += `&estado=${estado}`;

    fetch(url)
      .then(res => res.json())
      .then(data => {
        ocultarCargando('reservas');

        const stats = data.estadisticas;
        const estadisticasHTML = `
          <div class="stat-card">
            <div class="stat-label">Total Reservas</div>
            <div class="stat-value">${stats.total_reservas}</div>
          </div>
          <div class="stat-card secondary">
            <div class="stat-label">Ingresos Totales</div>
            <div class="stat-value">${formatearMoneda(stats.ingresos_totales)}</div>
          </div>
          <div class="stat-card tertiary">
            <div class="stat-label">Total Personas</div>
            <div class="stat-value">${stats.personas_totales}</div>
          </div>
          <div class="stat-card quaternary">
            <div class="stat-label">Promedio/Reserva</div>
            <div class="stat-value">${formatearMoneda(stats.promedio_por_reserva)}</div>
          </div>
        `;
        document.getElementById('estadisticas-reservas').innerHTML = estadisticasHTML;

        const tbody = document.querySelector('#tabla-reservas tbody');
        tbody.innerHTML = data.datos.map(r => `
          <tr>
            <td>${r.id_reserva}</td>
            <td>${r.codigo_unico}</td>
            <td>${r.fecha_viaje}</td>
            <td>${r.fecha_reserva}</td>
            <td><span class="badge ${obtenerBadgeEstado(r.estado)}">${r.estado}</span></td>
            <td>${r.cliente_nombre}</td>
            <td>${r.paquete_nombre}</td>
            <td>${r.cant_adultos}</td>
            <td>${r.cant_menores}</td>
            <td>${formatearMoneda(r.precio)}</td>
          </tr>
        `).join('');
      })
      .catch(err => {
        ocultarCargando('reservas');
        mostrarError('reservas', 'Error cargando reportes');
        console.error(err);
      });
  }

  function cargarPaquetes() {
    const fechas = obtenerFechas();

    if (!fechas.inicio || !fechas.fin) {
      mostrarError('paquetes', 'Por favor selecciona rango de fechas');
      return;
    }

    mostrarCargando('paquetes');
    ocultarError('paquetes');

    fetch(`/api/reportes/paquetes-top?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`)
      .then(res => res.json())
      .then(data => {
        ocultarCargando('paquetes');

        const stats = data.estadisticas;
        const estadisticasHTML = `
          <div class="stat-card">
            <div class="stat-label">Paquetes con Reservas</div>
            <div class="stat-value">${stats.total_paquetes}</div>
          </div>
          <div class="stat-card secondary">
            <div class="stat-label">Total Reservas</div>
            <div class="stat-value">${stats.total_reservas}</div>
          </div>
          <div class="stat-card tertiary">
            <div class="stat-label">Total Personas</div>
            <div class="stat-value">${stats.total_personas}</div>
          </div>
          <div class="stat-card quaternary">
            <div class="stat-label">Ingresos Totales</div>
            <div class="stat-value">${formatearMoneda(stats.ingreso_total)}</div>
          </div>
        `;
        document.getElementById('estadisticas-paquetes').innerHTML = estadisticasHTML;

        const rankingHTML = data.datos.map((p, idx) => `
          <div class="ranking-item">
            <div class="ranking-posicion ${idx === 0 ? 'top1' : idx === 1 ? 'top2' : idx === 2 ? 'top3' : ''}">
              ${idx + 1}
            </div>
            <div class="ranking-info">
              <div class="ranking-nombre">${p.nombre}</div>
              <div class="ranking-destino">${p.destino_nombre || 'Sin destino'}</div>
            </div>
            <div class="ranking-stats">
              <span>📦 ${p.total_reservas} reservas</span>
              <span>👥 ${p.total_personas} personas</span>
              <span>💵 ${formatearMoneda(p.precio_promedio)}</span>
            </div>
          </div>
        `).join('');

        document.getElementById('ranking-paquetes').innerHTML = `
          <div class="table-contenedor" style="border: 1px solid #e0e0e0; border-radius: var(--radius);">
            ${rankingHTML}
          </div>
        `;
      })
      .catch(err => {
        ocultarCargando('paquetes');
        mostrarError('paquetes', 'Error cargando reportes');
        console.error(err);
      });
  }

  function cargarCanceladas() {
    const fechas = obtenerFechas();

    if (!fechas.inicio || !fechas.fin) {
      mostrarError('canceladas', 'Por favor selecciona rango de fechas');
      return;
    }

    mostrarCargando('canceladas');
    ocultarError('canceladas');

    fetch(`/api/reportes/canceladas?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`)
      .then(res => res.json())
      .then(data => {
        ocultarCargando('canceladas');

        const stats = data.estadisticas;
        const estadisticasHTML = `
          <div class="stat-card secondary">
            <div class="stat-label">Total Canceladas</div>
            <div class="stat-value">${stats.total_canceladas}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Valor Cancelado</div>
            <div class="stat-value">${formatearMoneda(stats.valor_cancelado)}</div>
          </div>
          <div class="stat-card tertiary">
            <div class="stat-label">Promedio/Cancelación</div>
            <div class="stat-value">${formatearMoneda(stats.promedio_cancelacion)}</div>
          </div>
        `;
        document.getElementById('estadisticas-canceladas').innerHTML = estadisticasHTML;

        const tbody = document.querySelector('#tabla-canceladas tbody');
        tbody.innerHTML = data.datos.map(c => `
          <tr>
            <td>${c.codigo_unico}</td>
            <td>${c.cliente_nombre}</td>
            <td>${c.cliente_telefono || 'N/A'}</td>
            <td>${c.paquete_nombre}</td>
            <td>${c.fecha_viaje}</td>
            <td>${c.fecha_reserva}</td>
            <td>${c.motivo}</td>
            <td>${formatearMoneda(c.precio)}</td>
          </tr>
        `).join('');
      })
      .catch(err => {
        ocultarCargando('canceladas');
        mostrarError('canceladas', 'Error cargando reportes');
        console.error(err);
      });
  }

  function cargarIngresos() {
    const fechas = obtenerFechas();

    if (!fechas.inicio || !fechas.fin) {
      mostrarError('ingresos', 'Por favor selecciona rango de fechas');
      return;
    }

    mostrarCargando('ingresos');
    ocultarError('ingresos');

    fetch(`/api/reportes/ingresos?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`)
      .then(res => res.json())
      .then(data => {
        ocultarCargando('ingresos');

        const estadisticasHTML = `
          <div class="stat-card">
            <div class="stat-label">Total Reservas</div>
            <div class="stat-value">${data.total_reservas}</div>
          </div>
          <div class="stat-card secondary">
            <div class="stat-label">Ingresos Totales</div>
            <div class="stat-value">${formatearMoneda(data.ingreso_total)}</div>
          </div>
          <div class="stat-card tertiary">
            <div class="stat-label">Ingreso Promedio</div>
            <div class="stat-value">${formatearMoneda(data.ingreso_promedio)}</div>
          </div>
          <div class="stat-card quaternary">
            <div class="stat-label">Clientes Únicos</div>
            <div class="stat-value">${data.clientes_unicos}</div>
          </div>
        `;
        document.getElementById('estadisticas-ingresos').innerHTML = estadisticasHTML;

        const desgloseHTML = `
          <h3 style="margin-bottom: var(--space-2); font-size: 1.1rem;">Desglose por Estado</h3>
          <div class="desglose-estado">
            ${data.desglose_por_estado.map(e => `
              <div class="card-estado ${e.estado.toLowerCase().replace(' ', '')}">
                <div class="card-estado-titulo">${e.estado}</div>
                <div class="card-estado-valor">${e.reservas}</div>
                <div class="card-estado-detalles">
                  <div>Ingreso: ${formatearMoneda(e.ingreso)}</div>
                  <div>Promedio: ${formatearMoneda(e.promedio)}</div>
                  <div>Clientes: ${e.clientes}</div>
                </div>
              </div>
            `).join('')}
          </div>
        `;
        document.getElementById('desglose-estados').innerHTML = desgloseHTML;
      })
      .catch(err => {
        ocultarCargando('ingresos');
        mostrarError('ingresos', 'Error cargando reportes');
        console.error(err);
      });
  }

  function cargarDestinos() {
    const fechas = obtenerFechas();

    if (!fechas.inicio || !fechas.fin) {
      mostrarError('destinos', 'Por favor selecciona rango de fechas');
      return;
    }

    mostrarCargando('destinos');
    ocultarError('destinos');

    fetch(`/api/reportes/destinos-temporada?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`)
      .then(res => res.json())
      .then(data => {
        ocultarCargando('destinos');

        const stats = data.estadisticas;
        const estadisticasHTML = `
          <div class="stat-card">
            <div class="stat-label">Destinos Únicos</div>
            <div class="stat-value">${stats.total_destinos}</div>
          </div>
          <div class="stat-card secondary">
            <div class="stat-label">Total Reservas</div>
            <div class="stat-value">${stats.total_reservas}</div>
          </div>
          <div class="stat-card tertiary">
            <div class="stat-label">Total Personas</div>
            <div class="stat-value">${stats.total_personas}</div>
          </div>
        `;
        document.getElementById('estadisticas-destinos').innerHTML = estadisticasHTML;

        const destinosHTML = data.datos.map(d => `
          <div class="reporte-seccion" style="margin-top: var(--space-2);">
            <div style="font-weight: 600; font-size: 1.1rem; margin-bottom: var(--space-2);">
              🏖️ ${d.nombre}
              <span style="font-size: 0.9rem; color: #666; font-weight: normal;">
                (${d.total_reservas_general} reservas, ${d.total_personas_general} personas)
              </span>
            </div>
            <div class="table-contenedor">
              <table class="tabla-reporte">
                <thead>
                  <tr>
                    <th>Mes</th>
                    <th>Reservas</th>
                    <th>Personas</th>
                    <th>Precio Promedio</th>
                    <th>Rango Precio</th>
                    <th>Paquetes</th>
                    <th>Completadas</th>
                  </tr>
                </thead>
                <tbody>
                  ${d.temporadas.map(t => `
                    <tr>
                      <td>${t.mes}</td>
                      <td>${t.cantidad_reservas}</td>
                      <td>${t.total_personas}</td>
                      <td>${formatearMoneda(t.precio_promedio)}</td>
                      <td>${formatearMoneda(t.precio_minimo)} - ${formatearMoneda(t.precio_maximo)}</td>
                      <td>${t.paquetes_diferentes}</td>
                      <td>${t.reservas_completadas}</td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          </div>
        `).join('');

        document.getElementById('destinos-contenedor').innerHTML = destinosHTML;
      })
      .catch(err => {
        ocultarCargando('destinos');
        mostrarError('destinos', 'Error cargando reportes');
        console.error(err);
      });
  }

  function descargarReservas() {
    const fechas = obtenerFechas();
    const estado = document.getElementById('filtro-estado').value;
    let url = `/descargar/reportes/reservas?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`;
    if (estado) url += `&estado=${estado}`;
    window.location.href = url;
  }

  function descargarPaquetes() {
    const fechas = obtenerFechas();
    window.location.href = `/descargar/reportes/paquetes-top?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`;
  }

  function descargarCanceladas() {
    const fechas = obtenerFechas();
    window.location.href = `/descargar/reportes/canceladas?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`;
  }

  function descargarIngresos() {
    const fechas = obtenerFechas();
    window.location.href = `/descargar/reportes/ingresos?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`;
  }

  function descargarDestinos() {
    const fechas = obtenerFechas();
    window.location.href = `/descargar/reportes/destinos-temporada?fecha_inicio=${fechas.inicio}&fecha_fin=${fechas.fin}`;
  }

  function actualizarReportes() {
    cargarReservas();
  }

  function limpiarFiltros() {
    const hoy = new Date();
    const hace30 = new Date(hoy.setDate(hoy.getDate() - 30));

    document.getElementById('fecha-inicio').value = hace30.toISOString().split('T')[0];
    document.getElementById('fecha-fin').value = new Date().toISOString().split('T')[0];
    document.getElementById('filtro-estado').value = '';

    actualizarReportes();
  }

  window.addEventListener('load', () => {
    cargarReservas();
  });
