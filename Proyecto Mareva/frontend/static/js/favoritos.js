document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.favorite-button').forEach((boton) => {
    boton.addEventListener('click', async () => {
      boton.disabled = true;
      try {
        const respuesta = await fetch(boton.dataset.url, {
          method: 'POST',
          headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });
        const datos = await respuesta.json();
        if (!respuesta.ok || !datos.ok) throw new Error(datos.error || 'No se pudo actualizar');

        document.querySelectorAll(`.favorite-button[data-paquete-id="${boton.dataset.paqueteId}"]`)
          .forEach((item) => {
            item.classList.toggle('is-favorite', datos.agregado);
            item.setAttribute('aria-pressed', datos.agregado ? 'true' : 'false');
            item.textContent = datos.agregado ? '♥ Favorito' : '♡ Favorito';
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
