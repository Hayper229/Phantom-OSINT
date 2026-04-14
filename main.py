import asyncio
import random
import logging
from telethon import TelegramClient, events, functions, types, connection

# --- [КОНФИГУРАЦИЯ] ---
API_ID = 1234567 
API_HASH = 'ваш_api_hash'
ADMIN_ID = 987654321  # Твой ID (Бот будет "фанатеть" от тебя)
TARGET_ID = 'username_target' # Цель для зеркалирования

PROXY = ('oneproxys.best', 443, 'eed68360458af63073bac1394e8c7a48da6f6e6570726f7879732e62657374')

DEVICE = {
    'device_model': 'iPhone 15 Pro',
    'system_version': 'iOS 17.4',
    'app_version': '10.5.0',
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("Fan-Mirror")

client = TelegramClient('fan_mirror_session', API_ID, API_HASH, 
                        proxy=PROXY, 
                        connection=connection.ConnectionTcpMTProxyIntermediate,
                        **DEVICE)

# --- [МОДУЛЬ АКТИВНОСТИ НА АДМИНА] ---

async def admin_fan_behavior():
    """Бот смотрит и лайкает твои сторисы"""
    while True:
        try:
            # 1. Запрашиваем сторисы админа
            peer = await client.get_input_entity(ADMIN_ID)
            stories = await client(functions.stories.GetPeerStoriesRequest(peer=peer))
            
            if stories.stories.stories:
                for story in stories.stories.stories:
                    # Проверяем, не пустая ли это сторис
                    if isinstance(story, types.StoryItem):
                        # Читаем (просматриваем) сторис
                        await client(functions.stories.ReadStoriesRequest(peer=peer, max_id=story.id))
                        logger.info(f"👀 Посмотрел твою сторис (ID: {story.id})")
                        
                        # С шансом 70% лайкаем сторис
                        if random.random() < 0.7:
                            await client(functions.stories.SendReactionRequest(
                                peer=peer,
                                story_id=story.id,
                                reaction=types.ReactionEmoji(emoticon='❤️')
                            ))
                            logger.info(f"❤️ Поставил лайк на твою сторис!")
                        
                        await asyncio.sleep(random.randint(5, 15)) # Пауза между сторисами

            # 2. Имитируем "зависание" в чате с тобой
            async with client.action(ADMIN_ID, 'typing'):
                await asyncio.sleep(random.randint(2, 5))
            
            # Ждем следующей проверки (раз в 30-60 минут)
            await asyncio.sleep(random.randint(1800, 3600))
            
        except Exception as e:
            logger.error(f"Ошибка в фанатском модуле: {e}")
            await asyncio.sleep(600)

# --- [ОСНОВНАЯ ЛОГИКА] ---

@client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
async def handle_messages(event):
    # Бот пишет ТОЛЬКО тебе (админу)
    if event.sender_id != ADMIN_ID:
        # Если пишет кто-то чужой - пересылаем тебе
        await client.forward_messages(ADMIN_ID, event.message)
    else:
        # Если пишешь ТЫ боту
        if event.message.text.lower() == 'статус':
            await event.reply("✅ Я в сети, смотрю твои обновления!")

@client.on(events.UserUpdate)
async def on_target_update(event):
    """Зеркалирование цели (внешне бот копия цели, но ведет себя как твой фанат)"""
    t_id = await client.get_peer_id(TARGET_ID)
    if event.user_id == t_id:
        await asyncio.sleep(random.randint(300, 600))
        await sync_profile()

async def sync_profile():
    try:
        full = await client(functions.users.GetFullUserRequest(id=TARGET_ID))
        u = full.users
        await client(functions.account.UpdateProfileRequest(
            first_name=u.first_name or "", last_name=u.last_name or "", about=full.full_user.about or ""
        ))
        logger.info("🎭 Профиль цели синхронизирован")
    except: pass

async def main():
    await client.start()
    logger.info("🚀 Бот запущен. Режим: 'Твой личный фанат'.")
    
    # Запускаем модуль слежки за твоими сторисами
    asyncio.create_task(admin_fan_behavior())
    
    await sync_profile()
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
