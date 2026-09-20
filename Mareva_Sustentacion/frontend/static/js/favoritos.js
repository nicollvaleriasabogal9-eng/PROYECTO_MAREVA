document.addEventListener('DOMContentLoaded', () => {
  const SELECCION = '.favorite-button, .package-favorite-btn';

  document.querySelectorAll(SELECCION).forEach((boton) => {
    boton.addEventListener('click', async () => {
      boton.disabled = true;
      try {
        const respuesta = await fetch(boton.dataset.url, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const datos = await respuesta.json();
        if (!respuesta.ok || !datos.ok) throw new Error(datos.error || 'No se pudo actualizar');

        document.querySelectorAll(`${SELECCION}[data-paquete-id="${boton.dataset.paqueteId}"]`)
          .forEach((item) => {
            const agregado = datos.agregado;
            item.classList.toggle('is-favorite', agregado);
            item.classList.toggle('is-active', agregado);
            item.setAttribute('aria-pressed', agregado ? 'true' : 'false');
            item.title = agregado ? 'Quitar de favoritos' : 'Agregar a favoritos';

            if (item.classList.contains('favorite-button')) {
              item.innerHTML = agregado ? '♥ Favorito' : '♡ Favorito';
            } else {
              item.textContent = agregado ? '♥' : '♡';
            }
          });

        document.querySelectorAll('[data-favoritos-total]').forEach((contador) => {
          contador.textContent = datos.total;
        });

        if (!datos.agregado) {
          const tarjeta = boton.closest('[data-favorite-card]');
          if (tarjeta) {
            tarjeta.remove();
            if (!document.querySelector('[data-favorite-card]')) window.location.reload();
          }
        }
      } catch (error) {
        window.alert(error.message);
      } finally {
        boton.disabled = false;
      }
    });
  });
});