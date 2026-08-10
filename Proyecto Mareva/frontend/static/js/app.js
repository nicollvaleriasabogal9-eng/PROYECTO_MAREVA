
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
/* MOSTRAR U OCULTAR LA CONTRASEÑA AL HACER CLIC EN EL ÍCONO DEL OJO */
function togglePassword(inputId, btnEl) {
  const input = document.getElementById(inputId);
  if (!input) return;

  const esPassword = input.type === "password";
  input.type = esPassword ? "text" : "password";

  btnEl.setAttribute("aria-pressed", esPassword ? "true" : "false");

  const iconoAbierto = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8Z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  </svg>`;

  const iconoTachado = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="18" height="18">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
  </svg>`;

  btnEl.innerHTML = esPassword ? iconoTachado : iconoAbierto;
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