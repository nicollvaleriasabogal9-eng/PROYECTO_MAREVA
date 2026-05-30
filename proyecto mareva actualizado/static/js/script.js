const categories = [
  { name: 'Paquetes de Playa', avail: '12 disponibles', emoji: '🏖️', color: '#1a4b6b' },
  { name: 'Aventura',          avail: '8 disponibles',  emoji: '🏕️', color: '#2d4a1f' },
  { name: 'Turismo Cultural',  avail: '10 disponibles', emoji: '🏛️', color: '#4a2d1f' },
  { name: 'Montaña',           avail: '7 disponibles',  emoji: '⛰️', color: '#2d3a4a' },
  { name: 'Gastronomía',       avail: '5 disponibles',  emoji: '🍽️', color: '#4a331f' },
  { name: 'Tours Guiados',     avail: '9 disponibles',  emoji: '🧭', color: '#2d1f4a' },
  { name: 'Transporte',        avail: '6 disponibles',  emoji: '🚌', color: '#1f2d4a' },
  { name: 'Todo Incluido',     avail: '4 disponibles',  emoji: '✨', color: '#4a1f2d' },
  { name: 'Experiencias VIP',  avail: '3 disponibles',  emoji: '👑', color: '#3a1f1f' }
];

const fotos = [
  { name: 'Cartagena Todo Incluido 5 días',  price: 'Desde $1.850.000 COP por persona', rating: '★ 4,9', bg: '#1a4b6b' },
  { name: 'San Andrés Paradise 4 días',      price: 'Desde $1.450.000 COP por persona', rating: '★ 4,8', bg: '#0f5d75' },
  { name: 'Santa Marta y Tayrona',           price: 'Desde $1.200.000 COP por persona', rating: '★ 4,7', bg: '#1d6b5f' },
  { name: 'Islas del Rosario Premium',       price: 'Desde $2.100.000 COP por persona', rating: '★ 5,0', bg: '#0d728a' }
];

const chefs = [
  { name: 'Tour Eje Cafetero 6 días',       price: 'Desde $1.980.000 COP por persona', rating: '★ 4,9', bg: '#4a331f' },
  { name: 'Aventura en Caño Cristales',     price: 'Desde $2.450.000 COP por persona', rating: '★ 4,8', bg: '#3d2918' },
  { name: 'Villa de Leyva Cultural',        price: 'Desde $850.000 COP por persona',  rating: '★ 4,7', bg: '#5c3c22' },
  { name: 'Guatapé y Piedra del Peñol',    price: 'Desde $990.000 COP por persona',  rating: '★ 4,9', bg: '#6b4725' }
];

// ── CATEGORÍAS ──

const catGrid = document.getElementById('categories');

categories.forEach(c => {
  const div = document.createElement('div');
  div.className = 'category-card';
  div.innerHTML = `
    <div class="category-img" style="background:${c.color}">
      ${c.emoji}
    </div>
    <span class="category-name">${c.name}</span>
    <span class="category-avail">${c.avail}</span>
  `;
  catGrid.appendChild(div);
});

// ── PAQUETES ──

function renderListings(data, containerId, icono) {
  const wrap = document.getElementById(containerId);
  data.forEach(item => {
    const card = document.createElement('div');
    card.className = 'listing-card';
    card.innerHTML = `
      <div class="listing-img" style="background:${item.bg}">
        <button class="heart-btn" onclick="toggleHeart(this)">♥</button>
        ${icono}
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

renderListings(fotos,  'fotos', '🏖️');
renderListings(chefs,  'chefs', '✈️');

// ── FAVORITOS ──

function toggleHeart(btn) {
  btn.classList.toggle('liked');
}

// ── SCROLL ──

function scroll(id, dir) {
  const el = document.getElementById(id);
  el.scrollBy({ left: dir * 440, behavior: 'smooth' });
}

console.log('Mareva cargado correctamente');
