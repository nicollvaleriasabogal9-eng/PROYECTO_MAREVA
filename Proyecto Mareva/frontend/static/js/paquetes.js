const precioRange = document.getElementById("precioRange");
const precioValor = document.getElementById("precioValor");

precioRange.addEventListener("input", () => {
    precioValor.textContent =
        "$" + Number(precioRange.value).toLocaleString("es-CO");
});