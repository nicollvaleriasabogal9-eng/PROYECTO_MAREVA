document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formConfirmarReserva");
    const adultos = document.getElementById("inputAdultos");
    const menores = document.getElementById("inputMenores");
    const viajerosContainer = document.getElementById("viajerosContainer");
    const resumenViajeros = document.getElementById("resumenViajeros");

    if (!form) return;

    // ---------- Constructor de viajeros ----------

    function renderTravelers() {
        if (!viajerosContainer) return;

        const cantidadAdultos = Number(adultos?.value || 1);
        const cantidadMenores = Number(menores?.value || 0);
        const totalPersonas = cantidadAdultos + cantidadMenores;

        if (resumenViajeros) {
            resumenViajeros.textContent = totalPersonas;
        }

        viajerosContainer.innerHTML = "";

        for (let i = 1; i <= totalPersonas; i++) {
            const tipo = i <= cantidadAdultos ? "Adulto" : "Menor";

            const box = document.createElement("div");
            box.className = "traveler-form";

            box.innerHTML = `
                <div class="traveler-form__title">
                    <strong>Viajero ${i}</strong>
                    <span>${tipo}</span>
                </div>

                <div class="form-grid">
                    <div>
                        <label class="form-label">Nombre</label>
                        <input class="form-input" name="viajero_nombre[]" required>
                    </div>
                    <div>
                        <label class="form-label">Apellido</label>
                        <input class="form-input" name="viajero_apellido[]" required>
                    </div>
                    <div>
                        <label class="form-label">Tipo de documento</label>
                        <select class="form-select" name="viajero_tipo_documento[]" required>
                            <option value="">Selecciona</option>
                            <option value="CC">Cédula</option>
                            <option value="TI">Tarjeta de identidad</option>
                            <option value="CE">Cédula extranjería</option>
                            <option value="Pasaporte">Pasaporte</option>
                        </select>
                    </div>
                    <div>
                        <label class="form-label">Número de documento</label>
                        <input class="form-input" name="viajero_documento[]" required>
                    </div>
                    <div>
                        <label class="form-label">Idioma preferido</label>
                        <select class="form-select" name="viajero_idioma[]" required>
                            <option value="Español">Español</option>
                            <option value="Inglés">Inglés</option>
                            <option value="Francés">Francés</option>
                            <option value="Portugués">Portugués</option>
                            <option value="Alemán">Alemán</option>
                            <option value="Italiano">Italiano</option>
                        </select>
                    </div>
                </div>
            `;

            viajerosContainer.appendChild(box);
        }
    }

    adultos?.addEventListener("change", renderTravelers);
    menores?.addEventListener("change", renderTravelers);

    // ---------- Cambio de fecha ----------

    const cambiaFechaPanel = document.getElementById("cambiarFecha");
    const botonCambiaFecha = document.querySelector("[onclick='toggleFecha(this)']");

    window.toggleFecha = function (boton) {
        if (!cambiaFechaPanel) return;
        cambiaFechaPanel.hidden = !cambiaFechaPanel.hidden;
        if (!cambiaFechaPanel.hidden) {
            cambiaFechaPanel.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    };

    window.aplicarFecha = function () {
        if (!cambiaFechaPanel) return;

        const elegida = cambiaFechaPanel.querySelector('input[name="id_salida_alt"]:checked');
        if (!elegida) return;

        const oculto = form.querySelector('input[name="id_salida"]');
        if (oculto) oculto.value = elegida.value;

        const rotulo = elegida.closest(".pick-date");
        const texto = rotulo ? rotulo.querySelector("strong").textContent : "Actualizada";

        const itemFecha = form.querySelector(".confirm-card .sel-item");
        if (itemFecha) {
            const strong = itemFecha.querySelector(".sel-item__body strong");
            if (strong) strong.textContent = texto;
        }

        cambiaFechaPanel.hidden = true;
    };

    // ---------- Validación al enviar ----------

    form.addEventListener("submit", event => {
        const idSalida = form.querySelector('input[name="id_salida"]')?.value;
        const alojamiento = form.querySelector('input[name="alojamiento"]:checked');

        if (!idSalida) {
            event.preventDefault();
            alert("Debes elegir una fecha de salida.");
            return;
        }

        if (!alojamiento) {
            event.preventDefault();
            alert("Debes elegir un alojamiento.");
            return;
        }

        const personas = Number(adultos?.value || 1) + Number(menores?.value || 0);
        if (personas < 1) {
            event.preventDefault();
            alert("Debes ingresar al menos un viajero.");
        }
    });

    renderTravelers();
});