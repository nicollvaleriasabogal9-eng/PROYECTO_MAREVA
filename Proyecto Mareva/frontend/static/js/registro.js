
// Esta función es global porque el HTML la invoca mediante onclick.
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    if (!input) return;

    const mostrar = input.type === "password";
    input.type = mostrar ? "text" : "password";

    if (button) {
        button.setAttribute(
            "aria-label",
            mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
        );
        button.textContent = mostrar ? "🙈" : "👁";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    /* =========================
       VENTANAS LEGALES
       ========================= */
    let ultimoElementoActivo = null;

    document.querySelectorAll("[data-open-dialog]").forEach((boton) => {
        boton.addEventListener("click", () => {
            const dialogId = boton.dataset.openDialog;
            const dialogo = document.getElementById(dialogId);

            if (!dialogo || typeof dialogo.showModal !== "function") return;

            // Evita que queden dos ventanas legales abiertas al mismo tiempo.
            document.querySelectorAll(".legal-dialog[open]").forEach((abierto) => {
                if (abierto !== dialogo) abierto.close();
            });

            ultimoElementoActivo = boton;
            if (!dialogo.open) dialogo.showModal();
        });
    });

    document.querySelectorAll(".legal-dialog").forEach((dialogo) => {
        dialogo.querySelectorAll("[data-close-dialog]").forEach((boton) => {
            boton.addEventListener("click", () => {
                if (dialogo.open) dialogo.close();
            });
        });

        // Cierra si se hace clic en el fondo, no dentro del contenido.
        dialogo.addEventListener("click", (evento) => {
            if (evento.target === dialogo && dialogo.open) dialogo.close();
        });

        // Devuelve el foco al botón que abrió el diálogo.
        dialogo.addEventListener("close", () => {
            if (ultimoElementoActivo && ultimoElementoActivo.isConnected) {
                ultimoElementoActivo.focus();
            }
        });
    });

    /* =========================
       FORMULARIO Y VALIDACIONES
       ========================= */
    const form = document.getElementById("registroForm");
    if (!form) return;

    function obtenerCampo(id) {
        return document.getElementById(id);
    }

    function mostrarError(campo, mensaje) {
        if (!campo) return;

        campo.classList.add("invalid");
        campo.setAttribute("aria-invalid", "true");

        const error = obtenerCampo("error-" + campo.id);
        if (error) error.textContent = mensaje;
    }

    function limpiarError(campo) {
        if (!campo) return;

        campo.classList.remove("invalid");
        campo.removeAttribute("aria-invalid");

        const error = obtenerCampo("error-" + campo.id);
        if (error) error.textContent = "";
    }

    function validarObligatorio(id, nombreVisible) {
        const campo = obtenerCampo(id);
        if (!campo) return true;

        if (!campo.value.trim()) {
            mostrarError(campo, `El campo ${nombreVisible} es obligatorio.`);
            return false;
        }

        limpiarError(campo);
        return true;
    }

    const camposTexto = [
        ["nombre", "nombre"],
        ["apellido", "apellido"],
        ["tipo", "tipo de documento"],
        ["numero", "número de documento"],
        ["telefono", "teléfono"],
        ["correo", "correo electrónico"]
    ];

    camposTexto.forEach(([id]) => {
        const campo = obtenerCampo(id);
        if (!campo) return;

        const limpiarSiTieneValor = () => {
            if (campo.value.trim()) limpiarError(campo);
        };

        campo.addEventListener("input", limpiarSiTieneValor);
        campo.addEventListener("change", limpiarSiTieneValor);
    });

    const password = obtenerCampo("registroPassword");
    const confirmarPassword = obtenerCampo("confirmPassword");
    const correo = obtenerCampo("correo");
    const telefono = obtenerCampo("telefono");
    const telefonoCompleto = obtenerCampo("telefono_completo");
    const terminos = obtenerCampo("terminos");
    const politica = obtenerCampo("politica_no_reembolso");

    const correoValido = (valor) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor.trim());

    if (password) {
        password.addEventListener("input", () => {
            if (password.value.length < 8) {
                mostrarError(password, "La contraseña debe tener mínimo 8 caracteres.");
            } else {
                limpiarError(password);
            }

            if (confirmarPassword && confirmarPassword.value) {
                if (password.value !== confirmarPassword.value) {
                    mostrarError(confirmarPassword, "Las contraseñas no coinciden.");
                } else {
                    limpiarError(confirmarPassword);
                }
            }
        });
    }

    if (confirmarPassword) {
        confirmarPassword.addEventListener("input", () => {
            if (!password || confirmarPassword.value !== password.value) {
                mostrarError(confirmarPassword, "Las contraseñas no coinciden.");
            } else {
                limpiarError(confirmarPassword);
            }
        });
    }

    if (correo) {
        correo.addEventListener("blur", () => {
            if (!correo.value.trim()) {
                mostrarError(correo, "Ingresa tu correo electrónico.");
            } else if (!correoValido(correo.value)) {
                mostrarError(correo, "Ingresa un correo electrónico válido.");
            } else {
                limpiarError(correo);
            }
        });
    }

    function validarConsentimiento(campo, mensaje) {
        if (!campo) return true;

        const error = obtenerCampo("error-" + campo.id);
        if (!campo.checked) {
            if (error) error.textContent = mensaje;
            campo.setAttribute("aria-invalid", "true");
            return false;
        }

        if (error) error.textContent = "";
        campo.removeAttribute("aria-invalid");
        return true;
    }

    if (terminos) {
        terminos.addEventListener("change", () => {
            validarConsentimiento(
                terminos,
                "Debes aceptar los Términos y Condiciones para continuar."
            );
        });
    }

    if (politica) {
        politica.addEventListener("change", () => {
            validarConsentimiento(
                politica,
                "Debes aceptar la Política de No Reembolso para continuar."
            );
        });
    }

    /* =========================
       ENVÍO DEL FORMULARIO
       ========================= */
    form.addEventListener("submit", (evento) => {
        let formularioValido = true;

        camposTexto.forEach(([id, nombreVisible]) => {
            if (!validarObligatorio(id, nombreVisible)) formularioValido = false;
        });

        if (correo && !correoValido(correo.value)) {
            mostrarError(correo, "Ingresa un correo electrónico válido.");
            formularioValido = false;
        }

        if (password && password.value.length < 8) {
            mostrarError(password, "La contraseña debe tener mínimo 8 caracteres.");
            formularioValido = false;
        }

        if (confirmarPassword && password && password.value !== confirmarPassword.value) {
            mostrarError(confirmarPassword, "Las contraseñas no coinciden.");
            formularioValido = false;
        }

        if (!validarConsentimiento(terminos, "Debes aceptar los Términos y Condiciones.")) {
            formularioValido = false;
        }

        if (!validarConsentimiento(politica, "Debes aceptar la Política de No Reembolso.")) {
            formularioValido = false;
        }

        // Copia el teléfono al campo oculto que recibe el backend.
        if (telefono && telefonoCompleto) {
            telefonoCompleto.value = telefono.value.trim();
        }

        if (!formularioValido) {
            evento.preventDefault();

            const primerError = form.querySelector(
                ".invalid, input:invalid, select:invalid"
            );

            if (primerError) {
                primerError.focus();
                primerError.scrollIntoView({ behavior: "smooth", block: "center" });
            } else {
                const primerConsentimientoPendiente =
                    terminos && !terminos.checked ? terminos :
                    politica && !politica.checked ? politica : null;

                if (primerConsentimientoPendiente) primerConsentimientoPendiente.focus();
            }
        }
    });
});