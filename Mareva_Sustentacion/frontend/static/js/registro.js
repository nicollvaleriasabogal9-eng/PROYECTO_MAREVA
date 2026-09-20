document.addEventListener("DOMContentLoaded", () => {

    const formulario = document.querySelector("form");

    const nombre = document.querySelector('input[name="nombre"]');
    const apellido = document.querySelector('input[name="apellido"]');
    const tipo = document.querySelector('select[name="tipo"]');
    const documento = document.querySelector('input[name="numero"]');
    const correo = document.querySelector('input[name="correo"]');
    const password = document.querySelector('input[name="password"]');
    const telefono = document.querySelector("#telefono");
    const telefonoCompleto = document.querySelector("#telefono_completo");


    function mostrarError(input, mensaje) {

        let error = input.parentElement.querySelector(".mensaje-error");

        if (!error) {

            error = document.createElement("small");
            error.className = "mensaje-error";
            error.style.color = "red";
            error.style.display = "block";
            error.style.marginTop = "5px";

            input.parentElement.appendChild(error);

        }

        error.textContent = mensaje;

    }


    function limpiarError(input) {

        let error = input.parentElement.querySelector(".mensaje-error");

        if (error) {
            error.remove();
        }

    }


    // NOMBRE

    nombre.addEventListener("input", () => {

        if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$/.test(nombre.value))
            mostrarError(nombre, "El nombre solo puede contener letras.");
        else
            limpiarError(nombre);

    });


    // APELLIDO

    apellido.addEventListener("input", () => {

        if (!/^[A-Za-zÁÉÍÓÚáéíóúÑñ ]+$/.test(apellido.value))
            mostrarError(apellido, "El apellido solo puede contener letras.");
        else
            limpiarError(apellido);

    });


    // DOCUMENTO SEGÚN TIPO (debe coincidir con las reglas del backend)

    const reglasDocumento = {
        CC: { regex: /^\d{6,10}$/, mensaje: "La cédula debe tener entre 6 y 10 números." },
        TI: { regex: /^\d{10}$/, mensaje: "La tarjeta de identidad debe tener 10 números." },
        CE: { regex: /^\d{6,7}$/, mensaje: "La cédula de extranjería debe tener entre 6 y 7 números." },
        PA: { regex: /^[A-Za-z0-9]{6,12}$/, mensaje: "El pasaporte debe tener entre 6 y 12 caracteres alfanuméricos." }
    };

    function validarDocumento() {

        const regla = reglasDocumento[tipo.value];

        // PEP, PPT y RC no tienen regla estricta en el backend
        if (!regla) {
            limpiarError(documento);
            return;
        }

        if (!regla.regex.test(documento.value)) {
            mostrarError(documento, regla.mensaje);
        } else {
            limpiarError(documento);
        }

    }

    documento.addEventListener("input", validarDocumento);
    tipo.addEventListener("change", validarDocumento);


    // Validaciones del correo

  correo.addEventListener("input", () => {

    const formato = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    if (!formato.test(correo.value.trim())) {
        mostrarError(
            correo,
            "Ingrese un correo electrónico válido."
        );
    } else {
        limpiarError(correo);
    }

});


    // Validaciones para la contraseña

    password.addEventListener("input", () => {

        if (password.value.length < 8) {
            mostrarError(password, "La contraseña debe tener mínimo 8 caracteres.");
        } else {
            limpiarError(password);
        }

    });


    // validaciones para el telefono

    const iti = window.intlTelInput(telefono, {

        initialCountry: "co",
        separateDialCode: true,
        nationalMode: false,

        loadUtils: () => import(
            "https://cdn.jsdelivr.net/npm/intl-tel-input@25.3.1/build/js/utils.js"
        )

    });

    let itiListo = false;

    iti.promise.then(() => {
        itiListo = true;

        validarTelefono();
    });


    function validarTelefono() {

        if (!itiListo) return;

        if (telefono.value.trim() === "") {
            limpiarError(telefono);
            return;
        }

        if (!iti.isValidNumber()) {
            mostrarError(telefono, "El número de teléfono no es válido para el país seleccionado.");
        } else {
            limpiarError(telefono);
        }

    }


    telefono.addEventListener("input", validarTelefono);
    telefono.addEventListener("countrychange", validarTelefono);


    formulario.addEventListener("submit", (e) => {

        if (!itiListo) {

            e.preventDefault();

            mostrarError(
                telefono,
                "Espera un momento, cargando la validación del teléfono..."
            );

            return;
        }

        let numeroCompleto = iti.getNumber();

        telefonoCompleto.value = numeroCompleto;

        if (!iti.isValidNumber()) {

            e.preventDefault();

            mostrarError(
                telefono,
                "El número de teléfono no es válido para el país seleccionado."
            );

            return;
        }

        limpiarError(telefono);

    });

});