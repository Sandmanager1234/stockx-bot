#!/usr/bin/env python
import logging
import asyncio
from aiogram import Bot, Dispatcher

import chat.parsing_chat as parsing_chat
from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)


async def main():
    dp = Dispatcher()
    dp.include_router(parsing_chat.parse)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
