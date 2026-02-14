const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

let products = [];
let cart = JSON.parse(localStorage.getItem('cart')) || {};
let retryCount = 0;

// ========================
// Telegram User ID Setup
// ========================
function setupTelegramUser() {
    const user = tg?.initDataUnsafe?.user;
    if (user?.id) {
        localStorage.setItem('telegram_id', user.id);
        const userEl = document.getElementById('user-name');
        if (userEl) userEl.innerText = user.first_name || "";
    } else if (!localStorage.getItem('telegram_id')) {
        alert(
            "Shaxsiy ma'lumotlaringiz yetarli emas.\n" +
            "Iltimos botga /start buyrug'ini kiritib qayta ishga tushiring!"
        );
        tg.close();
    }
}

// ========================
// Initialize App
// ========================
function initializeApp() {
    setupTelegramUser();

    const dataElement = document.getElementById('products-data');
    if (!dataElement) {
        if (retryCount < 10) {
            retryCount++;
            setTimeout(initializeApp, 100);
        } else {
            console.error("products-data topilmadi");
        }
        return;
    }

    try {
        const rawData = JSON.parse(dataElement.textContent);
        products = Array.isArray(rawData) ? rawData : [];
        renderHome(products);
        updateBadge();
    } catch (e) {
        console.error("JSON o‘qishda xato:", e);
    }
}

let currentCategory = 'all'; // Dastlabki holat

// Yangi funksiya: filterItems
function filterItems(category, btn) {
    // Filtrlangan mahsulotlar
    const filtered = category === 'all'
        ? products
        : products.filter(p => p.cat?.toLowerCase() === category.toLowerCase());

    // Sahifani yangilash
    renderHome(filtered);

    // Active class ni o'zgartirish
    document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active-category'));
    btn.classList.add('active-category');

    // Haptic feedback (ixtiyoriy)
    tg.HapticFeedback?.impactOccurred('light');

    console.log(`Filtrlandi: ${category}, natijalar: ${filtered.length}`); // Debug uchun
}

// ========================
// Render Home / Grid
// ========================
function renderHome(items) {
    const grid = document.getElementById('food-grid');
    if (!grid) return;

    const safeItems = Array.isArray(items) ? items : [];

    if (!safeItems.length) {
        grid.innerHTML = `
            <div class="col-span-2 text-center py-20 text-gray-400 font-medium italic">
                Hozircha mahsulotlar mavjud emas...
            </div>`;
        return;
    }

    grid.innerHTML = safeItems.map(p => `
        <div class="bg-white rounded-[2.2rem] p-3 shadow-sm border border-gray-50 flex flex-col">
            <div class="relative overflow-hidden rounded-[1.8rem] mb-3 h-32 bg-gray-50">
                <img src="${p.img}" class="w-full h-full object-cover"
                     onerror="this.src='https://via.placeholder.com/150?text=Le+Vanille'">
            </div>
            <h4 class="font-bold text-[13px] text-gray-800 px-1 leading-tight h-8 overflow-hidden">${p.name}</h4>
            <div class="flex justify-between items-center mt-3 px-1 pb-1">
                <span class="text-[#a8000b] font-black text-xs">${Number(p.price).toLocaleString()} s.</span>
                <button onclick="addToCart(${p.id})" class="bg-[#a8000b] text-white p-2.5 rounded-xl active:scale-90 transition-transform">
                    <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3.5">
                        <path d="M12 4v16m8-8H4"/>
                    </svg>
                </button>
            </div>
        </div>
    `).join('');

    console.log("Render yakunlandi, grid to'ldirildi.");
}

// ========================
// Cart Functions
// ========================
function addToCart(id) {
    cart[id] = (cart[id] || 0) + 1;
    localStorage.setItem('cart', JSON.stringify(cart));
    updateBadge();
    tg.HapticFeedback?.notificationOccurred('success');
}

function updateBadge() {
    const count = Object.values(cart).reduce((a, b) => a + b, 0);
    const badge = document.getElementById('cart-badge');
    if (badge) {
        count > 0 ? (badge.innerText = count, badge.classList.remove('hidden')) : badge.classList.add('hidden');
    }
}

function renderCart() {
    const container = document.getElementById('cart-items');
    const summary = document.getElementById('cart-summary');
    if (!container) return;

    const ids = Object.keys(cart);
    if (!ids.length) {
        container.innerHTML = `<div class="text-center py-20 text-gray-400 italic font-medium">
            Savat hozircha bo'sh...
        </div>`;
        summary?.classList.add('hidden');
        return;
    }

    summary?.classList.remove('hidden');
    let total = 0;

    container.innerHTML = ids.map(id => {
        const item = products.find(p => p.id == id);
        if (!item) return '';
        const lineTotal = item.price * cart[id];
        total += lineTotal;

        return `
            <div class="flex items-center bg-white p-3 rounded-[1.8rem] shadow-sm border border-gray-50 mb-3">
                <img src="${item.img}" class="w-16 h-16 rounded-2xl object-cover">
                <div class="flex-1 ml-4">
                    <h4 class="font-bold text-xs text-gray-800">${item.name}</h4>
                    <p class="text-[#a8000b] font-black text-xs mt-1">${Number(item.price).toLocaleString()} s.</p>
                </div>
                <div class="flex items-center bg-gray-50 rounded-xl p-1 w-fit">
                    <button onclick="changeQty(${id}, -1)"
                            class="count-btn minus-btn bg-white shadow-sm text-gray-400 active:scale-90">
                        <span>−</span>
                    </button>

                    <span class="font-bold text-base w-6 text-center select-none text-gray-800 inline-block">
                        ${cart[id]}
                    </span>

                    <button onclick="changeQty(${id}, 1)"
                            class="count-btn plus-btn bg-[#a8000b] text-white active:scale-90">
                        <span>+</span>
                    </button>
                </div>
            </div>`;
    }).join('');

    const subtotalEl = document.getElementById('subtotal-val');
    const totalEl = document.getElementById('total-val');
    if (subtotalEl) subtotalEl.innerText = total.toLocaleString() + " so'm";
    if (totalEl) totalEl.innerText = total.toLocaleString() + " so'm";
}

function changeQty(id, delta) {
    if (!cart[id]) return;
    cart[id] += delta;
    if (cart[id] <= 0) delete cart[id];
    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart();
    updateBadge();
}

// ========================
// Checkout / Send Order
// ========================
async function checkout(event) {
    const telegramId = localStorage.getItem('telegram_id');
    if (!telegramId) {
        alert(
            "Xatolik: Shaxsiy ma'lumotlaringiz topilmadi.\n" +
            "Iltimos botga /start buyrug'ini kiritib qayta ishga tushiring"
        );
        tg.close();
        return;
    }

    const ids = Object.keys(cart);
    if (!ids.length) return;

    const orderData = {
        telegram_id: telegramId,
        items: ids.map(id => {
            const product = products.find(p => p.id == id);
            return { product_id: product?.id, quantity: cart[id] };
        }),
        total_price: ids.reduce((sum, id) => {
            const p = products.find(prod => prod.id == id);
            return sum + (p.price * cart[id]);
        }, 0)
    };

    const btn = event.target;
    const originalText = btn.innerText;
    btn.disabled = true;
    btn.innerText = "Yuborilmoqda...";

    try {
        const response = await fetch('/order/create-order/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(orderData)
        });

        if (response.ok) {
            tg.showAlert("Buyurtmangiz qabul qilindi!");
            cart = {};
            localStorage.removeItem('cart');
            updateBadge();
            showPage('home');
        } else {
            throw new Error();
        }
    } catch (error) {
        alert("Xatolik: Buyurtmani yuborib bo'lmadi.");
        console.error("Checkout xatolik:", error);
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
}

// ========================
// Page Navigation
// ========================
function showPage(pageId, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(pageId + '-page');
    if (target) target.classList.add('active');

    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    if (pageId === 'cart') renderCart();
    tg.HapticFeedback?.impactOccurred('medium');
}

// ========================
// Helpers
// ========================
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ========================
// Start App
// ========================
document.addEventListener('DOMContentLoaded', initializeApp);
