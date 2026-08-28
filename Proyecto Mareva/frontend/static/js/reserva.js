document.addEventListener("DOMContentLoaded", function () {

    const fechaInicio = document.getElementById("fecha_inicio");
    const fechaRegreso = document.getElementById("fecha_regreso");
    const fechaRegresoTexto = document.getElementById("fecha-regreso-texto");
    const dias = document.getElementById("dias");

    const adultos = document.getElementById("adultos");
    const menores = document.getElementById("menores");
    const bebes = document.getElementById("bebes");

    const precioPaqueteElement = document.getElementById("precio-paquete");
    const cantidadViajerosElement = document.getElementById("cantidad-viajeros");
    const precioExtrasElement = document.getElementById("precio-extras");
    const valorTotalElement = document.getElementById("valor-total");

    const extras = document.querySelectorAll(".extra-checkbox");
    const formulario = document.getElementById("form-reserva");

    function formatearPrecio(valor) {
        return "$" + Math.round(valor).toLocaleString("es-CO");
    }

    function obtenerFechaRegreso() {

        if (!fechaInicio.value) {
            return null;
        }

        const fecha = new Date(
            fechaInicio.value + "T00:00:00"
        );

        fecha.setDate(
            fecha.getDate() + duracionPaquete - 1
        );

        return fecha;
    }

    function formatearFecha(fecha) {

        const año = fecha.getFullYear();

        const mes = String(
            fecha.getMonth() + 1
        ).padStart(2, "0");

        const dia = String(
            fecha.getDate()
        ).padStart(2, "0");

        return {
            fechaISO: `${año}-${mes}-${dia}`,
            fechaTexto: `${dia}/${mes}/${año}`
        };
    }

    function calcularFechaRegreso() {

        if (!fechaInicio.value) {

            fechaRegreso.value = "";

            fechaRegresoTexto.textContent =
                "📅 Selecciona tu fecha de inicio";

            return true;
        }

        const fecha = obtenerFechaRegreso();

        if (!fecha) {
            return false;
        }

        const resultado = formatearFecha(fecha);

        fechaRegreso.value = resultado.fechaISO;

        fechaRegresoTexto.textContent =
            `📅 Regreso: ${resultado.fechaTexto}`;

        if (
            fechaInicio.max &&
            resultado.fechaISO > fechaInicio.max
        ) {

            fechaRegresoTexto.textContent =
                "⚠️ La fecha de regreso supera el periodo disponible.";

            fechaRegreso.value = "";

            return false;
        }

        return true;
    }

    function calcularTotal() {

        const cantidadAdultos =
            Math.max(parseInt(adultos.value) || 0, 0);

        const cantidadMenores =
            Math.max(parseInt(menores.value) || 0, 0);

        const cantidadBebes =
            Math.max(parseInt(bebes.value) || 0, 0);

        const viajeros =
            cantidadAdultos +
            cantidadMenores +
            cantidadBebes;

        let totalExtras = 0;

        extras.forEach(function (extra) {

            if (extra.checked) {

                totalExtras +=
                    Number(extra.dataset.precio) || 0;
            }

        });

        const valorPaquete =
            precioPaquete * viajeros;

        const valorTotal =
            valorPaquete + totalExtras;

        precioPaqueteElement.textContent =
            formatearPrecio(valorPaquete);

        cantidadViajerosElement.textContent =
            viajeros;

        precioExtrasElement.textContent =
            formatearPrecio(totalExtras);

        valorTotalElement.textContent =
            formatearPrecio(valorTotal);

        if (viajeros > cuposDisponibles) {

            cantidadViajerosElement.style.color = "red";
            valorTotalElement.style.color = "red";

        } else {

            cantidadViajerosElement.style.color = "";
            valorTotalElement.style.color = "";
        }
    }

    function validarViajeros() {

        let valorAdultos =
            parseInt(adultos.value);

        let valorMenores =
            parseInt(menores.value);

        let valorBebes =
            parseInt(bebes.value);

        if (
            isNaN(valorAdultos) ||
            valorAdultos < 1
        ) {
            adultos.value = 1;
        }

        if (
            isNaN(valorMenores) ||
            valorMenores < 0
        ) {
            menores.value = 0;
        }

        if (
            isNaN(valorBebes) ||
            valorBebes < 0
        ) {
            bebes.value = 0;
        }

        calcularTotal();
    }

    function configurarFechaMaxima() {

        if (!fechaInicio.max) {
            return;
        }

        const fechaMaxima = new Date(
            fechaInicio.max + "T00:00:00"
        );

        fechaMaxima.setDate(
            fechaMaxima.getDate() -
            duracionPaquete +
            1
        );

        const resultado =
            formatearFecha(fechaMaxima);

        fechaInicio.max =
            resultado.fechaISO;
    }

    fechaInicio.addEventListener(
        "change",
        calcularFechaRegreso
    );

    adultos.addEventListener(
        "input",
        validarViajeros
    );

    menores.addEventListener(
        "input",
        validarViajeros
    );

    bebes.addEventListener(
        "input",
        validarViajeros
    );

    extras.forEach(function (extra) {

        extra.addEventListener(
            "change",
            calcularTotal
        );

    });

    formulario.addEventListener(
        "submit",
        function (evento) {

            const cantidadAdultos =
                parseInt(adultos.value) || 0;

            const cantidadMenores =
                parseInt(menores.value) || 0;

            const cantidadBebes =
                parseInt(bebes.value) || 0;

            const viajeros =
                cantidadAdultos +
                cantidadMenores +
                cantidadBebes;

            if (cantidadAdultos < 1) {

                evento.preventDefault();

                alert(
                    "Debe haber al menos 1 adulto."
                );

                adultos.value = 1;

                calcularTotal();

                return;
            }

            if (
                cantidadMenores < 0 ||
                cantidadBebes < 0
            ) {

                evento.preventDefault();

                alert(
                    "Las cantidades no pueden ser negativas."
                );

                validarViajeros();

                return;
            }

            if (viajeros > cuposDisponibles) {

                evento.preventDefault();

                alert(
                    "No puedes reservar " +
                    viajeros +
                    " viajeros. Solo hay " +
                    cuposDisponibles +
                    " cupos disponibles."
                );

                return;
            }

            if (!fechaInicio.value) {

                evento.preventDefault();

                alert(
                    "Selecciona una fecha de viaje."
                );

                return;
            }

            if (!calcularFechaRegreso()) {

                evento.preventDefault();

                alert(
                    "La fecha de regreso está fuera del periodo permitido."
                );

                return;
            }

            dias.value = duracionPaquete;
        }
    );

    dias.value = duracionPaquete;
    dias.readOnly = true;

    configurarFechaMaxima();

    calcularFechaRegreso();
    calcularTotal();

});
