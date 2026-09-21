
document.addEventListener("DOMContentLoaded", function () {

    const boton = document.getElementById("compareSelectedBtn");

    if (!boton) return;

    boton.addEventListener("click", function () {

        const seleccionados = Array.from(
            document.querySelectorAll(".compare-package:checked")
        ).map(input => input.value);

        if (seleccionados.length < 2) {
            alert("Selecciona al menos 2 paquetes para comparar.");
            return;
        }

        const params = new URLSearchParams();

        seleccionados.forEach(id => {
            params.append("ids", id);
        });

        window.location.href =
            "{{ url_for('paquetes.comparar') }}?" + params.toString();
    });

});

