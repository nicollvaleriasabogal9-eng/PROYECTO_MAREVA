async function cargarPanelDashboard() {

  try {

    const res = await fetch(
      "{{ url_for('dashboard.obtener_panel_completo') }}"
    );

    if (!res.ok) {
      throw new Error("Error cargando el panel");
    }

    const data = await res.json();


    const m = data.metricas;

    document.getElementById(
      "m-reservas-dia"
    ).textContent = m.reservas_del_dia;

    document.getElementById(
      "m-reservas-pendientes"
    ).textContent = m.reservas_pendientes_confirmar;

    document.getElementById(
      "m-paquetes-proximos"
    ).textContent = m.paquetes_salida_proxima;

    document.getElementById(
      "m-cupos-criticos"
    ).textContent = m.cupos_criticos;

    document.getElementById(
      "m-ingresos-mes"
    ).textContent =
      "$" +
      Number(
        m.ingresos_esperados_mes
      ).toLocaleString(
        "es-CO",
        {
          minimumFractionDigits: 2
        }
      );


    const contReservas =
      document.getElementById(
        "alerta-reservas-contenido"
      );

    if (data.alertas_reservas.hay_alertas) {

      contReservas.innerHTML =
        data.alertas_reservas.datos
          .map(r => `

            <div class="dashboard-item">

              <div class="dashboard-item__main">

                <div class="dashboard-item__title">
                  ${r.cliente_nombre}
                  — ${r.paquete_nombre}
                </div>

                <div class="dashboard-item__info">
                  Código ${r.codigo_unico}
                  · ${r.cliente_correo}
                </div>

              </div>

              <span class="badge badge-yellow">
                ${r.dias_sin_gestion} días
              </span>

            </div>

          `)
          .join("");

    } else {

      contReservas.innerHTML = `

        <div class="dashboard-empty">
          No hay reservas sin gestionar. 🎉
        </div>

      `;

    }


    const contPaquetes =
      document.getElementById(
        "alerta-paquetes-contenido"
      );

    if (data.alertas_paquetes.hay_alertas) {

      contPaquetes.innerHTML =
        data.alertas_paquetes.datos
          .map(p => `

            <div class="dashboard-item">

              <div class="dashboard-item__main">

                <div class="dashboard-item__title">
                  ${p.nombre}
                </div>

                <div class="dashboard-item__info">
                  Sale en ${p.dias_para_salida} día(s)
                  · ${p.fecha_inicio}
                </div>

              </div>

              <span class="badge badge-blue">
                ${p.cupos_disponibles}/${p.cupos_totales}
                cupos
              </span>

            </div>

          `)
          .join("");

    } else {

      contPaquetes.innerHTML = `

        <div class="dashboard-empty">
          No hay salidas próximas con cupos libres.
        </div>

      `;

    }


    const contNiveles =
      document.getElementById(
        "niveles-contenido"
      );

    if (
      data.niveles.datos &&
      data.niveles.datos.length > 0
    ) {

      contNiveles.innerHTML = `

        <div class="dashboard-levels">

          ${
            data.niveles.datos
              .map(n => `

                <div class="dashboard-level">

                  <span class="dashboard-level__name">
                    ${n.nivel_nombre}
                  </span>

                  <div class="dashboard-level__bar-background">

                    <div
                      class="dashboard-level__bar"
                      style="width:${n.porcentaje_del_total}%">
                    </div>

                  </div>

                  <span class="dashboard-level__value">
                    ${n.cantidad_clientes}
                    (${n.porcentaje_del_total}%)
                  </span>

                </div>

              `)
              .join("")
          }

        </div>

      `;

    } else {

      contNiveles.innerHTML = `

        <div class="dashboard-empty">
          Aún no hay clientes registrados.
        </div>

      `;

    }

  } catch (err) {

    console.error(
      "Error cargando dashboard:",
      err
    );

    document.getElementById(
      "alerta-reservas-contenido"
    ).innerHTML = `

      <div class="dashboard-empty">
        No fue posible cargar la información.
      </div>

    `;

    document.getElementById(
      "alerta-paquetes-contenido"
    ).innerHTML = `

      <div class="dashboard-empty">
        No fue posible cargar la información.
      </div>

    `;

    document.getElementById(
      "niveles-contenido"
    ).innerHTML = `

      <div class="dashboard-empty">
        No fue posible cargar la información.
      </div>

    `;

  }

}


cargarPanelDashboard();


setInterval(
  cargarPanelDashboard,
  60000
);

