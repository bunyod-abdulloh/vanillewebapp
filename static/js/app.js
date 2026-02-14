const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();


let products = [];
let cart = JSON.parse(localStorage.getItem('cart')) || {};

function initializeApp() {
    console.log("Dastur ishga tushmoqda...");
    const dataElement = document.getElementById('products-data');

    // Tekshirish alerti
    if (tg?.initDataUnsafe?.user) {
        alert("Bot orqali ochildi: " + tg.initDataUnsafe.user.first_name);
    } else {
        alert("Bot orqali ochilmagan yoki user ma'lumot yo'q");
    }

    if (dataElement) {
        try {
            // Ma'lumotni o'qiymiz
            const rawData = JSON.parse(dataElement.textContent);

            // AGAR rawData massiv bo'lmasa, uni massivga aylantiramiz yoki o'qiymiz
            products = Array.isArray(rawData) ? rawData : [];

            console.log("Tozalangan mahsulotlar massivi:", products);

            if (products.length > 0) {
                renderHome(products);
                updateBadge();
            } else {
                console.warn("Mahsulotlar massivi bo'sh!");
                renderHome([]); // "Mavjud emas" yozuvini chiqarish uchun
            }
        } catch (e) {
            console.error("JSON o'qishda xato:", e);
        }
    } else {
        setTimeout(initializeApp, 100);
    }

    if (tg.initDataUnsafe?.user) {
        const userEl = document.getElementById('user-name');
        if (userEl) userEl.innerText = tg.initDataUnsafe.user.first_name;
    }
}

function renderHome(items) {
    const grid = document.getElementById('food-grid');
    if (!grid) return;

    // XATONI OLDINI OLISH: items har doim massiv bo'lishini ta'minlaymiz
    const safeItems = Array.isArray(items) ? items : [];

    if (safeItems.length === 0) {
        grid.innerHTML = `
            <div class="col-span-2 text-center py-20 text-gray-400 font-medium italic">
                Hozircha mahsulotlar mavjud emas...
            </div>`;
        return;
    }

    // Endi .map() aniq ishlaydi
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

// Qolgan funksiyalar o'zgarishsiz qoladi...
function filterItems(cat, btn) {
    document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active-category'));
    if (btn) btn.classList.add('active-category');
    const filtered = (cat === 'all') ? products : products.filter(p => p.cat === cat);
    renderHome(filtered);
}

function addToCart(id) {
    cart[id] = (cart[id] || 0) + 1;
    localStorage.setItem('cart', JSON.stringify(cart));
    updateBadge();
    if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
}

function updateBadge() {
    const count = Object.values(cart).reduce((a, b) => a + b, 0);
    const badge = document.getElementById('cart-badge');
    if (badge) {
        count > 0 ? (badge.innerText = count, badge.classList.remove('hidden')) : badge.classList.add('hidden');
    }
}

// 1. showPage funksiyasini yangilaymiz
function showPage(pageId, btn) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    const target = document.getElementById(pageId + '-page');
    if (target) target.classList.add('active');

    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');

    // AGAR savat tugmasi bosilsa, savatni chizishni boshlaymiz
    if (pageId === 'cart') {
        renderCart();
    }

    if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');
}

// 2. Savatni chizish funksiyasi
function renderCart() {
    const container = document.getElementById('cart-items');
    const summary = document.getElementById('cart-summary');

    if (!container) return;

    const ids = Object.keys(cart);

    // Savat bo'sh bo'lsa
    if (ids.length === 0) {
        container.innerHTML = `
            <div class="text-center py-20 text-gray-400 italic font-medium">
                Savat hozircha bo'sh...
            </div>`;
        if (summary) summary.classList.add('hidden');
        return;
    }

    // Savatda narsa bo'lsa, xulosani ko'rsatish
    if (summary) summary.classList.remove('hidden');
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
                <div class="flex items-center space-x-2 bg-gray-50 rounded-xl p-1.5">
                    <button onclick="changeQty(${id}, -1)" class="w-6 h-6 bg-white rounded-lg shadow-sm flex items-center justify-center font-bold text-gray-500">-</button>
                    <span class="font-bold text-xs w-4 text-center">${cart[id]}</span>
                    <button onclick="changeQty(${id}, 1)" class="w-6 h-6 bg-[#a8000b] text-white rounded-lg flex items-center justify-center font-bold text-white">+</button>
                </div>
            </div>`;
    }).join('');

    // Summalarni yangilash
    const subtotalEl = document.getElementById('subtotal-val');
    const totalEl = document.getElementById('total-val');

    if (subtotalEl) subtotalEl.innerText = total.toLocaleString() + " so'm";
    if (totalEl) totalEl.innerText = total.toLocaleString() + " so'm";
}

// 3. Savatda miqdorni o'zgartirish funksiyasi
function changeQty(id, delta) {
    if (!cart[id]) return;

    cart[id] += delta;

    if (cart[id] <= 0) {
        delete cart[id];
    }

    localStorage.setItem('cart', JSON.stringify(cart));
    renderCart(); // Ekranni qayta chizish
    updateBadge(); // Ikonkadagi raqamni yangilash
}

async function checkout(event) {
    const tg = window.Telegram?.WebApp;
    const user = tg?.initDataUnsafe?.user;

    if (!tg || !user || !user.id) {
        alert("Xatolik: Iltimos, faqat bot orqali kiring!");
        return;
    }

    const ids = Object.keys(cart);
    if (ids.length === 0) return;

    const orderData = {
        telegram_id: user.id,
        items: ids.map(id => {
            const product = products.find(p => p.id == id);
            return { product_id: product?.id, quantity: cart[id] };
        }),
        total_price: ids.reduce((sum, id) => {
            const p = products.find(prod => prod.id == id);
            return sum + (p.price * cart[id]);
        }, 0)
    };

    // Tugmani yuklanish holati
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
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
}

// CSRF tokenni olish uchun yordamchi funksiya
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

// Dasturni ishga tushirish
document.addEventListener('DOMContentLoaded', initializeApp);