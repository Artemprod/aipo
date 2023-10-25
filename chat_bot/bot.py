from chat_bot.configs.bot_config import load_bot_config
import asyncio
from aiogram import Bot, Dispatcher

from container import data_base_controller
from chat_bot.handlers import command_handlers, user_handlers


async def main() -> None:
    config = load_bot_config('.env')
    bot: Bot = Bot(token=config.Bot.tg_bot_token, parse_mode='HTML')

    data_base = data_base_controller

    # Добовляем хэгдлеры в диспечтер через роутеры
    dp: Dispatcher = Dispatcher(data_base=data_base)
    dp.include_router(command_handlers.router)
    dp.include_router(user_handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем прослушку бота
    await dp.start_polling(bot)


if __name__ == '__main__':
    # Запускаем бота
    asyncio.run(main())
