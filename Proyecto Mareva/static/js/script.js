const categories = [
    { name: 'Fotografía',        avail: '8 disponibles',  emoji: '📷', color: '#1a1a2e' },
    { name: 'Chefs',             avail: '1 disponible',   emoji: '🍽️', color: '#2d1b00' },
    { name: 'Entrenamiento',     avail: '1 disponible',   emoji: '🏋️', color: '#1a2d00' },
    { name: 'Masaje',            avail: 'Próximamente',   emoji: '💆', color: '#2d001a' },
    { name: 'Comidas preparadas',avail: 'Próximamente',   emoji: '🥘', color: '#1a2200' },
    { name: 'Maquillaje',        avail: 'Próximamente',   emoji: '💄', color: '#2d1520' },
    { name: 'Cabello',           avail: 'Próximamente',   emoji: '💇', color: '#0d1a2d' },
    { name: 'Tratam. de spa',    avail: 'Próximamente',   emoji: '🧖', color: '#1a0d2d' },
    { name: 'Catering',          avail: 'Próximamente',   emoji: '🍱', color: '#2d1a00' },
  ];

  const fotos = [
    { name: 'Sesión de fotografía profesional por Jairo', price: 'Desde $199,999 COP por participante', rating: '★ 4,93', bg: '#3a2a1a' },
    { name: 'Candelaria Photo Experience',                price: 'Desde $500,000 COP por participante', rating: '',        bg: '#1a2a3a' },
    { name: 'Recorrido panorámico y fotos en La Calera',  price: 'Desde $650,000 COP por grupo',        rating: '',        bg: '#1a3a2a' },
    { name: 'Experiencia fotográfica en el Jardín Botánico', price: 'Desde $480,000 COP por grupo',     rating: '',        bg: '#2a1a3a' }
  ];

  const chefs = [
    { name: 'Chef Alejandro – Cocina Fusión Colombiana',  price: 'Desde $280,000 COP por persona',      rating: '★ 4,8',   bg: '#2a1a00' },
    { name: 'Experiencia Gastronómica en Casa',           price: 'Desde $350,000 COP por persona',      rating: '★ 4,9',   bg: '#1a0d00' },
    { name: 'Taller de Cocina Tradicional Bogotana',      price: 'Desde $190,000 COP por persona',      rating: '',        bg: '#3a2500' },
    { name: 'Menú Degustación Privado 5 Tiempos',        price: 'Desde $420,000 COP por persona',      rating: '★ 5,0',   bg: '#200a00' }
  ];

  // ── RENDER CATEGORIES ──
  const catGrid = document.getElementById('categories');
  categories.forEach(c => {
    const div = document.createElement('div');
    div.className = 'category-card';
    div.innerHTML = `
      <div class="category-img" style="background:${c.color};display:flex;align-items:center;justify-content:center;font-size:48px;">
        ${c.emoji}
      </div>
      <span class="category-name">${c.name}</span>
      <span class="category-avail">${c.avail}</span>
    `;
    catGrid.appendChild(div);
  });

  // ── RENDER LISTINGS ──
  function renderListings(data, containerId) {
    const wrap = document.getElementById(containerId);
    data.forEach((item, i) => {
      const card = document.createElement('div');
      card.className = 'listing-card';
      card.innerHTML = `
        <div class="listing-img" style="background:${item.bg};display:flex;align-items:center;justify-content:center;font-size:52px;">
          <button class="heart-btn" onclick="toggleHeart(this)">♥</button>
          📷
        </div>
        <div class="listing-info">
          <div class="listing-meta">
            <span class="listing-name">${item.name}</span>
            ${item.rating ? `<span class="listing-rating">${item.rating}</span>` : ''}
          </div>
          <span class="listing-price">${item.price}</span>
        </div>
      `;
      wrap.appendChild(card);
    });
  }

  renderListings(fotos, 'fotos');
  renderListings(chefs,  'chefs');


  function toggleHeart(btn) {
    btn.classList.toggle('liked');
  }

 
  function scroll(id, dir) {
    const el = document.getElementById(id);
    el.scrollBy({ left: dir * 440, behavior: 'smooth' });
  }