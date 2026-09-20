document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("formReserva");
    const adultos = document.getElementById("inputAdultos");
    const menores = document.getElementById("inputMenores");
    const viajerosContainer = document.getElementById("viajerosContainer");
    const reservaData = document.getElementById("reservaData");
    const idSalidaInput = document.getElementById("idSalidaInput");
    const fechaViajeInput = document.getElementById("fechaViajeInput");
    const fechaSeleccionadaTexto = document.getElementById("fechaSeleccionadaTexto");
    const checkoutDate = document.getElementById("checkoutDate");
    const calendario = document.getElementById("calendario");
    const calendarMonth = document.getElementById("calendarMonth");
    const calendarHint = document.getElementById("calendarHint");
    const prevMonth = document.getElementById("prevMonth");
    const nextMonth = document.getElementById("nextMonth");

    if (!form || !reservaData) return;

    const botonesSalida = Array.from(
        reservaData.querySelectorAll(".departure-option")
    );

    const salidas = botonesSalida.map(elemento => ({
        id_salida: elemento.dataset.idSalida,
        fecha_salida: elemento.dataset.fecha,
        fecha_regreso: elemento.dataset.regreso,
        elemento
    }));

    function fechaLocal(fecha) {
        const [anio, mes, dia] = fecha.split("-").map(Number);
        return new Date(anio, mes - 1, dia);
    }

    function fechaISO(fecha) {
        const anio = fecha.getFullYear();
        const mes = String(fecha.getMonth() + 1).padStart(2, "0");
        const dia = String(fecha.getDate()).padStart(2, "0");
        return `${anio}-${mes}-${dia}`;
    }

    function formatearFecha(fechaTexto) {
        if (!fechaTexto) return "";

        const partes = fechaTexto.split("-");

        if (partes.length !== 3) return fechaTexto;

        return `${partes[2]}/${partes[1]}/${partes[0]}`;
    }

    function formatearMes(fecha) {
        return fecha.toLocaleDateString("es-CO", {
            month: "long",
            year: "numeric"
        }).replace(/^./, letra => letra.toUpperCase());
    }

    function seleccionarSalida(salida) {
        if (!salida) return;

        if (idSalidaInput) {
            idSalidaInput.value = salida.id_salida;
        }

        if (fechaViajeInput) {
            fechaViajeInput.value = salida.fecha_salida;
        }

        salidas.forEach(item => {
            item.elemento.classList.remove("is-selected", "selected");
        });

        salida.elemento.classList.add("is-selected");

        const fechaSalida = formatearFecha(salida.fecha_salida);
        const fechaRegreso = formatearFecha(salida.fecha_regreso);
        const rango = `${fechaSalida} → ${fechaRegreso}`;

        if (fechaSeleccionadaTexto) {
            fechaSeleccionadaTexto.textContent = rango;
        }

        if (checkoutDate) {
            checkoutDate.textContent = rango;
        }

        if (calendarHint) {
            calendarHint.textContent = `Salida: ${fechaSalida}`;
        }
    }

    botonesSalida.forEach((boton, indice) => {
        boton.addEventListener("click", () => {
            seleccionarSalida(salidas[indice]);
        });
    });

    function salidasDelMes(anio, mes) {
        return salidas.filter(salida => {
            const fecha = fechaLocal(salida.fecha_salida);
            return fecha.getFullYear() === anio && fecha.getMonth() === mes;
        });
    }

    function buscarSalidaPorFecha(fecha) {
        return salidas.find(
            salida => salida.fecha_salida === fecha
        );
    }

    function renderCalendario() {
        if (!calendario || !calendarMonth) return;

        if (!window.marevaCalendario) {
            const primera = salidas[0]
                ? fechaLocal(salidas[0].fecha_salida)
                : new Date();

            window.marevaCalendario = new Date(
                primera.getFullYear(),
                primera.getMonth(),
                1
            );
        }

        const fechaActual = window.marevaCalendario;
        const anio = fechaActual.getFullYear();
        const mes = fechaActual.getMonth();

        calendarMonth.textContent = formatearMes(fechaActual);
        calendario.innerHTML = "";

        const primerDia = new Date(anio, mes, 1);
        let diaSemana = primerDia.getDay();

        diaSemana = diaSemana === 0 ? 6 : diaSemana - 1;

        const diasMes = new Date(anio, mes + 1, 0).getDate();

        for (let i = 0; i < diaSemana; i++) {
            const espacio = document.createElement("span");
            espacio.className = "calendar-day calendar-day--empty";
            calendario.appendChild(espacio);
        }

        for (let dia = 1; dia <= diasMes; dia++) {
            const fecha = new Date(anio, mes, dia);
            const fechaTexto = fechaISO(fecha);
            const salida = buscarSalidaPorFecha(fechaTexto);

            const boton = document.createElement("button");
            boton.type = "button";
            boton.className = "calendar-day";
            boton.textContent = dia;

            if (!salida) {
                boton.disabled = true;
                boton.classList.add("is-disabled");
            } else {
                boton.classList.add("is-available");

                if (
                    idSalidaInput &&
                    String(idSalidaInput.value) === String(salida.id_salida)
                ) {
                    boton.classList.add("is-selected");
                }

                boton.addEventListener("click", () => {
                    seleccionarSalida(salida);
                    renderCalendario();
                });
            }

            calendario.appendChild(boton);
        }
    }

    function cambiarMes(cantidad) {
        if (!window.marevaCalendario) {
            window.marevaCalendario = salidas[0]
                ? fechaLocal(salidas[0].fecha_salida)
                : new Date();
        }

        window.marevaCalendario = new Date(
            window.marevaCalendario.getFullYear(),
            window.marevaCalendario.getMonth() + cantidad,
            1
        );

        renderCalendario();
    }

    prevMonth?.addEventListener("click", () => {
        cambiarMes(-1);
    });

    nextMonth?.addEventListener("click", () => {
        cambiarMes(1);
    });

    function obtenerCantidadPersonas() {
        const cantidadAdultos = Number(adultos?.value || 1);
        const cantidadMenores = Number(menores?.value || 0);

        return cantidadAdultos + cantidadMenores;
    }

    function renderTravelers() {
        if (!viajerosContainer) return;

        const cantidadAdultos = Number(adultos?.value || 1);
        const cantidadMenores = Number(menores?.value || 0);
        const totalPersonas = cantidadAdultos + cantidadMenores;

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
                        <input
                            class="form-input traveler-name"
                            name="viajero_nombre[]"
                            required>
                    </div>

                    <div>
                        <label class="form-label">Apellido</label>
                        <input
                            class="form-input traveler-lastname"
                            name="viajero_apellido[]"
                            required>
                    </div>

                    <div>
                        <label class="form-label">
                            Tipo de documento
                        </label>

                        <select
                            class="form-select"
                            name="viajero_tipo_documento[]"
                            required>

                            <option value="">
                                Selecciona
                            </option>

                            <option value="CC">
                                Cédula
                            </option>

                            <option value="TI">
                                Tarjeta de identidad
                            </option>

                            <option value="CE">
                                Cédula extranjería
                            </option>

                            <option value="Pasaporte">
                                Pasaporte
                            </option>
                        </select>
                    </div>

                    <div>
                        <label class="form-label">
                            Número de documento
                        </label>

                        <input
                            class="form-input traveler-document"
                            name="viajero_documento[]"
                            required>
                    </div>

                    <div>
                        <label class="form-label">
                            Idioma preferido
                        </label>

                        <select
                            class="form-select"
                            name="viajero_idioma[]"
                            required>

                            <option value="Español">
                                Español
                            </option>

                            <option value="Inglés">
                                Inglés
                            </option>

                            <option value="Francés">
                                Francés
                            </option>

                            <option value="Portugués">
                                Portugués
                            </option>

                            <option value="Alemán">
                                Alemán
                            </option>

                            <option value="Italiano">
                                Italiano
                            </option>
                        </select>
                    </div>
                </div>
            `;

            viajerosContainer.appendChild(box);
        }
    }

    document
        .querySelectorAll("[data-counter]")
        .forEach(button => {
            button.addEventListener("click", () => {
                const campo = button.dataset.counter;
                const accion = button.dataset.action;

                const input =
                    campo === "adultos"
                        ? adultos
                        : menores;

                if (!input) return;

                let valor = Number(input.value || 0);

                valor =
                    accion === "plus"
                        ? valor + 1
                        : valor - 1;

                if (campo === "adultos") {
                    valor = Math.max(1, Math.min(valor, 20));
                } else {
                    valor = Math.max(0, Math.min(valor, 20));
                }

                input.value = valor;
                renderTravelers();
            });
        });

    adultos?.addEventListener("change", renderTravelers);
    menores?.addEventListener("change", renderTravelers);

    form.addEventListener("submit", event => {
        const idSalida = idSalidaInput?.value;
        const fechaViaje = fechaViajeInput?.value;
        const personas = obtenerCantidadPersonas();

        if (!idSalida || !fechaViaje) {
            event.preventDefault();

            alert("Debes seleccionar una fecha de salida.");
            return;
        }

        if (personas < 1) {
            event.preventDefault();

            alert("Debes ingresar al menos un viajero.");
        }
    });

    renderTravelers();

    if (salidas.length > 0) {
        const primeraFecha = fechaLocal(salidas[0].fecha_salida);

        window.marevaCalendario = new Date(
            primeraFecha.getFullYear(),
            primeraFecha.getMonth(),
            1
        );

        renderCalendario();
    } else {
        if (calendario) {
            calendario.innerHTML = `
                <div class="alert alert-error">
                    No hay fechas disponibles para este paquete actualmente.
                </div>
            `;
        }

        const boton = form.querySelector(".booking-submit");

        if (boton) {
            boton.disabled = true;
            boton.textContent = "Sin fechas disponibles";
        }
    }
});