document.addEventListener("DOMContentLoaded", () => {

    const metodos = document.querySelectorAll(
        'input[name="metodo"]'
    );

    const campos = {
        nequi: document.getElementById("nequiFields"),
        pse: document.getElementById("pseFields"),
        tarjeta: document.getElementById("tarjetaFields")
    };

    const error = document.getElementById("paymentError");
    const boton = document.getElementById("btnPagar");
    const loading = document.getElementById("paymentLoading");

    function ocultarCampos() {

        Object.values(campos).forEach((campo) => {

            if (campo) {
                campo.classList.remove("active");
            }

        });

    }

    metodos.forEach((radio) => {

        radio.addEventListener("change", () => {

            ocultarCampos();

            const seleccionado = radio.value;

            if (campos[seleccionado]) {
                campos[seleccionado].classList.add("active");
            }

            error.textContent = "";

        });

    });

    function mostrarError(mensaje) {

        error.textContent = mensaje;
        error.classList.add("show");

    }

    function limpiarError() {

        error.textContent = "";
        error.classList.remove("show");

    }

    function validarNequi() {

        const numero = document
            .getElementById("nequiNumero")
            .value
            .replace(/\D/g, "");

        if (numero.length !== 10) {

            mostrarError(
                "El número de Nequi debe tener exactamente 10 dígitos."
            );

            return false;
        }

        return true;
    }

    function validarPSE() {

        const banco =
            document.getElementById("pseBanco").value;

        const tipo =
            document.getElementById("pseTipoDocumento").value;

        const documento =
            document
                .getElementById("pseDocumento")
                .value
                .replace(/\D/g, "");

        if (!banco || !tipo || !documento) {

            mostrarError(
                "Debes completar todos los campos de PSE."
            );

            return false;
        }

        if (documento.length < 5) {

            mostrarError(
                "El número de documento no es válido."
            );

            return false;
        }

        return true;
    }

    function validarTarjeta() {

        const numero =
            document
                .getElementById("tarjetaNumero")
                .value
                .replace(/\D/g, "");

        const titular =
            document
                .getElementById("tarjetaTitular")
                .value
                .trim();

        const fecha =
            document
                .getElementById("tarjetaFecha")
                .value
                .trim();

        const cvv =
            document
                .getElementById("tarjetaCvv")
                .value
                .replace(/\D/g, "");

        if (numero.length < 13 || numero.length > 19) {

            mostrarError(
                "El número de tarjeta no es válido."
            );

            return false;
        }

        if (!titular) {

            mostrarError(
                "Debes ingresar el nombre del titular."
            );

            return false;
        }

        if (!/^(0[1-9]|1[0-2])\/\d{2}$/.test(fecha)) {

            mostrarError(
                "La fecha debe tener el formato MM/AA."
            );

            return false;
        }

        if (cvv.length < 3 || cvv.length > 4) {

            mostrarError(
                "El CVV debe tener entre 3 y 4 dígitos."
            );

            return false;
        }

        return true;
    }

    boton.addEventListener("click", () => {

        limpiarError();

        const seleccionado =
            document.querySelector(
                'input[name="metodo"]:checked'
            );

        if (!seleccionado) {

            mostrarError(
                "Debes seleccionar un método de pago."
            );

            return;
        }

        let valido = false;

        if (seleccionado.value === "nequi") {
            valido = validarNequi();
        }

        if (seleccionado.value === "pse") {
            valido = validarPSE();
        }

        if (seleccionado.value === "tarjeta") {
            valido = validarTarjeta();
        }

        if (!valido) {
            return;
        }

        boton.disabled = true;

        loading.classList.add("show");

        setTimeout(() => {

            window.location.href =
                "/reserva/pago/exitoso";

        }, 2500);

    });

});