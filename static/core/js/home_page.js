

const tg = window.Telegram.WebApp;
tg.expand();

const products = [
    { id: 1, name: 'Truffle Burger',       price: 45000, cat: 'burger', img: 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600' },
    { id: 2, name: 'Pepperoni Pizza',      price: 65000, cat: 'pizza',  img: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600' },
    { id: 3, name: 'Classic Cola',         price: 12000, cat: 'drink',  img: 'https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=600' },
    { id: 4, name: 'Double Cheese Burger', price: 55000, cat: 'burger', img: 'https://images.unsplash.com/photo-1594212699903-ec8a3eca50f5?w=600' },
    { id: 5, name: 'Margarita XL',         price: 58000, cat: 'pizza',  img: 'https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=600' },
    { id: 6, name: 'Fresh Fanta',          price: 12000, cat: 'drink',  img: 'https://images.unsplash.com/photo-1624552184280-9e9631bbeee9?w=600' }
];

let cart = {};

function renderHome(items) {
    document.getElementById('food-grid').innerHTML = items.map(p => `
        <div class="card p-3.5">
            <img src="${p.img}" class="w-full h-40 object-cover rounded-2xl mb-4 shadow-md">
            <h4 class="font-semibold text-base leading-tight h-10 line-clamp-2">${p.name}</h4>
            <div class="flex justify-between items-center mt-4">
                <span class="text-xl font-black text-red-400">${p.price.toLocaleString()} s</span>
                <button onclick="addToCart(${p.id})" class="btn-add text-white p-3.5 rounded-xl shadow-lg">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                        <path d="M12 4v16m8-8H4"/>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');
}

function filterItems(cat, btn) {
    document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active-category'));
    btn.classList.add('active-category');
    renderHome(cat === 'all' ? products : products.filter(p => p.cat === cat));
    tg.HapticFeedback.selectionChanged();
}

function addToCart(id) {
    cart[id] = (cart[id] || 0) + 1;
    updateBadge();
    tg.HapticFeedback.notificationOccurred('success');
}

function updateBadge() {
    const count = Object.values(cart).reduce((a,b)=>a+b,0);
    document.querySelectorAll('#cart-badge').forEach(el => {
        if (count > 0) {
            el.textContent = count;
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
        }
    });
}

function showPage(pageId, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(pageId + '-page').classList.add('active');

    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    if (pageId === 'cart') renderCart();
}

function renderCart() {
    const container = document.getElementById('cart-items');
    const summary = document.getElementById('cart-summary');
    const ids = Object.keys(cart);

    if (ids.length === 0) {
        container.innerHTML = `<div class="text-center py-24 text-gray-500 text-lg italic">Savat bo‘sh...</div>`;
        summary.classList.add('hidden');
        return;
    }

    summary.classList.remove('hidden');
    let total = 0;

    container.innerHTML = ids.map(id => {
        const item = products.find(p => p.id == id);
        total += item.price * cart[id];
        return `
        <div class="glass flex items-center p-4 rounded-2xl">
            <img src="${item.img}" class="w-20 h-20 rounded-2xl object-cover mr-4 shadow">
            <div class="flex-1">
                <h4 class="font-semibold text-base">${item.name}</h4>
                <p class="text-red-400 font-bold mt-1">${item.price.toLocaleString()} s</p>
            </div>
            <div class="flex items-center bg-black/30 rounded-xl p-2">
                <button onclick="changeQty(${id}, -1)" class="w-9 h-9 flex items-center justify-center text-xl font-bold text-gray-300">-</button>
                <span class="w-10 text-center font-bold text-lg">${cart[id]}</span>
                <button onclick="changeQty(${id}, 1)"  class="w-9 h-9 flex items-center justify-center text-xl font-bold text-white">+</button>
            </div>
        </div>`;
    }).join('');

    document.getElementById('subtotal-val').innerText = total.toLocaleString() + " so'm";
    document.getElementById('total-val').innerText   = total.toLocaleString() + " so'm";
}

function changeQty(id, delta) {
    cart[id] += delta;
    if (cart[id] <= 0) delete cart[id];
    renderCart();
    updateBadge();
    tg.HapticFeedback.impactOccurred('light');
}

function checkout() {
    tg.showConfirm("Buyurtmani tasdiqlaysizmi?", ok => {
        if (ok) {
            tg.showAlert("Rahmat! Buyurtmangiz qabul qilindi.");
            cart = {};
            updateBadge();
            showPage('home', document.querySelector('.nav-item.active'));
        }
    });
}

renderHome(products);
updateBadge();
