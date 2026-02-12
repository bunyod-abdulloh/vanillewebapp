// Telegram WebApp core init
window.tg = window.Telegram?.WebApp || null;

if (window.tg) {
    window.tg.expand();
}

// Global telegram user id
window.telegram_id = window.tg?.initDataUnsafe?.user?.id || null;

if (!window.telegram_id) {
    console.warn("Telegram ID topilmadi (WebApp Telegram ichida ochilmagan)");
}
