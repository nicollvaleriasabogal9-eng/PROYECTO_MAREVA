document.addEventListener("DOMContentLoaded", function () {

    const fechaInicio = document.querySelector('input[name="fecha_inicio"]');
    const diasInput = document.querySelector('input[name="dias"]');
    const fechaRegreso = document.querySelector('input[name="fecha_regreso"]');
    const textoRegreso = document.getElementById("fecha-regreso-texto");

    if (!fechaInicio || !diasInput) {
        return;
    }

    const hoy = new Date();

    const año = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, "0");
    const dia = String(hoy.getDate()).padStart(2, "0");

    const fechaMinima = `${año}-${mes}-${dia}`;

    fechaInicio.min = fechaMinima;

    function formatearFecha(fecha) {
        return fecha.toLocaleDateString("es-CO", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        });
    }

    function calcularFechaRegreso() {

        if (!fechaInicio.value || !diasInput.value) {
            return;
        }

        const dias = parseInt(diasInput.value);

        if (isNaN(dias) || dias < 1) {
            return;
        }

        const inicio = new Date(fechaInicio.value + "T00:00:00");

        const regreso = new Date(inicio);
        regreso.setDate(regreso.getDate() + dias);

        const añoRegreso = regreso.getFullYear();
        const mesRegreso = String(regreso.getMonth() + 1).padStart(2, "0");
        const diaRegreso = String(regreso.getDate()).padStart(2, "0");

        const fechaRegresoCalculada =
            `${añoRegreso}-${mesRegreso}-${diaRegreso}`;

        if (fechaRegreso) {
            fechaRegreso.value = fechaRegresoCalculada;
        }

        if (textoRegreso) {
            textoRegreso.textContent =
                "📅 Regreso: " + formatearFecha(regreso);
        }
    }

    fechaInicio.addEventListener("change", function () {

        if (this.value < fechaMinima) {
            this.value = fechaMinima;
        }

        calcularFechaRegreso();
    });

    diasInput.addEventListener("input", function () {

        if (this.value < 1) {
            this.value = 1;
        }

        calcularFechaRegreso();
    });

    calcularFechaRegreso();
});
