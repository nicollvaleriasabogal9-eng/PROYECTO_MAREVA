/* OBTENER TODAS LAS TARJETAS DE PAQUETES DISPONIBLES EN LA PÁGINA */
function getCards() {
  return document.querySelectorAll(".card");
}

/* FILTRAR LAS TARJETAS POR CATEGORÍA Y ACTUALIZAR LOS BOTONES ACTIVOS */
function filtrarPaquetes(categoria) {
  const cards = getCards();
  const botones = document.querySelectorAll(".filtro-btn");

  /* QUITAR LA CLASE ACTIVA DE TODOS LOS BOTONES DE FILTRO */
  botones.forEach(btn => btn.classList.remove("active"));

  /* MARCAR COMO ACTIVO EL BOTÓN QUE CORRESPONDE A LA CATEGORÍA SELECCIONADA */
  document
    .querySelector(`[onclick="filtrarPaquetes('${categoria}')"]`)
    ?.classList.add("active");

  /* MOSTRAR U OCULTAR LAS TARJETAS SEGÚN LA CATEGORÍA SELECCIONADA */
  cards.forEach(card => {
    const cat = card.dataset.categoria;

    card.style.display =
      categoria === "todos" || cat === categoria ? "block" : "none";
  });

  /* RENOVAR EL NÚMERO TOTAL DE PAQUETES VISIBLES */
  actualizarContador();
}

/* LIMPIAR EL TEXTO QUITANDO ACENTOS, ESPACIOS EXTRA Y PASANDO A MINÚSCULAS */
function normalizar(str) {
  return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase().trim();
}

/* CONTROLAR LA BÚSQUEDA DE PAQUETES POR TEXTO DESDE EL FORMULARIO */
function buscarPaquete(event) {
  event.preventDefault();

  const text = normalizar(document.getElementById("searchInput")?.value || "");

  /* COMPROBAR SI EL USUARIO ESTÁ EN EL INICIO PARA REDIRIGIRLO A LA PÁGINA DE PAQUETES */
  const enIndex = !document.getElementById("paquetesGrid");
  if (enIndex) {
    window.location.href = `/paquetes?q=${encodeURIComponent(text)}`;
    return;
  }

  /* FILTRAR LAS TARJETAS EN TIEMPO REAL SI YA SE ENCUENTRA EN LA PÁGINA DE PAQUETES */
  const cards = getCards();
  cards.forEach(card => {
    const title = card.querySelector(".card__title")?.innerText.toLowerCase() || "";
    card.style.display = title.includes(text) ? "block" : "none";
  });

  /* RENOVAR EL NÚMERO TOTAL DE PAQUETES VISIBLES */
  actualizarContador();
}

/* MODIFICAR EL CONTADOR DE PAQUETES Y MOSTRAR EL MENSAJE DE ERROR SI NO HAY RESULTADOS */
function actualizarContador(valor) {
  /* OBTENER EL NÚMERO DE TARJETAS VISIBLES SI NO SE ENVÍA UN VALOR FIJO */
  if (valor === undefined) {
    const cards = getCards();
    valor = Array.from(cards).filter(
      c => c.style.display !== "none"
    ).length;
  }

  /* REEMPLAZAR EL TEXTO EN EL ELEMENTO DEL CONTADOR TOTAL */
  const el = document.getElementById("totalPaquetes");
  if (el) el.textContent = valor;

  /* MOSTRAR U OCULTAR EL MENSAJE DE SIN RESULTADOS SEGÚN LAS TARJETAS VISIBLES */
  const noResultados = document.getElementById("noResultados");
  if (noResultados) {
    noResultados.hidden = valor !== 0;
  }
}

/* EJECUTAR LAS FUNCIONES E INICIALIZAR EL CONTENIDO CUANDO LA PÁGINA YA CARGÓ */
document.addEventListener("DOMContentLoaded", () => {
});