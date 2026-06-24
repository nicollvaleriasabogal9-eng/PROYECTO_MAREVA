

/* LIMPIAR EL TEXTO QUITANDO ACENTOS, ESPACIOS EXTRA Y PASANDO A MINÚSCULAS */
function normalizar(str) {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

/* EVALUAR Y MOSTRAR U OCULTAR LAS TARJETAS SEGÚN EL TEXTO, CATEGORÍA Y PRECIO SELECCIONADOS */
function aplicarFiltros() {
  const texto = normalizar(document.getElementById("searchInput")?.value || "");
  const categoria = document.getElementById("categoria")?.value || "todos";
  const precio = parseInt(document.getElementById("precioRange")?.value || 9999999);

  const cards = document.querySelectorAll(".card[data-categoria]");
  let visibles = 0;

  /* ITERAR POR CADA TARJETA PARA VERIFICAR SI CUMPLE CON TODOS LOS REQUISITOS */
  cards.forEach(card => {
    const titulo = normalizar(card.querySelector(".card__title")?.textContent || "");
    const desc = normalizar(card.querySelector(".card__desc")?.textContent || "");
    const cat = card.dataset.categoria;
    const precioCard = parseInt(card.dataset.precio || "0");

    const matchTexto = texto === "" || titulo.includes(texto) || desc.includes(texto);
    const matchCat = categoria === "todos" || cat === categoria;
    const matchPrecio = precioCard <= precio;

    /* LA TARJETA SE MUESTRA SÓLO SI SE CUMPLEN LAS TRES CONDICIONES SIMULTÁNEAMENTE */
    const mostrar = matchTexto && matchCat && matchPrecio;
    card.style.display = mostrar ? "block" : "none";
    if (mostrar) visibles++;
  });

  /* MODIFICAR EL CONTADOR VISIBLE CON EL TOTAL DE RESULTADOS ENCONTRADOS */
  const contador = document.getElementById("totalPaquetes");
  if (contador) contador.textContent = visibles;

  /* MOSTRAR EL MENSAJE DE ADVERTENCIA CUANDO NINGUNA TARJETA COINCIDE CON LOS FILTROS */
  const noResultados = document.getElementById("noResultados");
  if (noResultados) noResultados.hidden = visibles !== 0;
}




/* DETENER EL ENVÍO DEL FORMULARIO Y PROCESAR LA BÚSQUEDA CON EL SISTEMA GENERAL */
function buscarPaquete(event) {
  if (event) event.preventDefault();
  aplicarFiltros();
}

/* LEER LOS PARÁMETROS DE LA URL PARA COPIAR EL TEXTO DE BÚSQUEDA EN EL INPUT */
function filtrarPorQuery() {
  const params = new URLSearchParams(window.location.search);
  const query = params.get("q");

  if (!query) return;

  const input = document.getElementById("searchInput");
  if (input) input.value = query;

  aplicarFiltros();
}

/* ACTUALIZAR EL TEXTO DE PRECIO EN LA INTERFAZ CON FORMATO DE MONEDA LOCAL */
function actualizarPrecio(valor) {
  const label = document.getElementById("precioValor");

  if (label) {
    label.textContent = "$" + Number(valor).toLocaleString("es-CO");
  }

  aplicarFiltros();
}


/* RESERVA (SIMULADO) */

/* ENVIAR AL USUARIO A LA PÁGINA DE COMPRA ADJUNTANDO EL NOMBRE DEL PAQUETE ELEGIDO */
function reservarPaquete(nombre) {
  if (!nombre) return;

  alert(`🧳 Reserva iniciada para: ${nombre}`);

  window.location.href = `/reserva?paquete=${encodeURIComponent(nombre)}`;
}


/* REDIRIGIR A LA PÁGINA ESPECÍFICA DE DETALLES USANDO EL NOMBRE COMO IDENTIFICADOR */
function verDetalle(nombre) {
  if (!nombre) return;

  window.location.href = `/detalle?nombre=${encodeURIComponent(nombre)}`;
}


/*  INIT (CARGA AUTOMÁTICA)*/

/* CONFIGURAR LAS CONDICIONES INICIALES DE LA PÁGINA CUANDO EL CONTENIDO ESTÁ LISTO */
document.addEventListener("DOMContentLoaded", () => {
  /* REVISAR SI EXISTE UNA BÚSQUEDA PREVIA EN LA URL PARA LLENAR EL CUADRO DE TEXTO */
  const params = new URLSearchParams(window.location.search);
  const q = params.get("q");
  if (q) {
    const input = document.getElementById("searchInput");
    if (input) input.value = q;
  }

  /* EJECUTAR EL FILTRADO INICIAL PARA ORGANIZAR LAS TARJETAS DESDE EL PRINCIPIO */
  aplicarFiltros();
});