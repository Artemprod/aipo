from environs import Env
from dataclasses import dataclass

from chat_bot.enteties.database import MongoDB
from chat_bot.enteties.telegram_bot import TelegramBot
from chat_bot.enteties.GPT import OpenAI_KEY


@dataclass
class Configs:
    Bot: TelegramBot
    ChatGPT: OpenAI_KEY
    Data_base: MongoDB


def load_bot_config(path) -> Configs:
    env: Env = Env()
    env.read_env(path)
    bot = TelegramBot(
        tg_bot_token=env('TELEGRAM_BOT_TOKEN')
    )
    open_ai_key = OpenAI_KEY(
        key=env('OPEN_AI_API_KEK'),
    )
    data_base = MongoDB(host=env('DB_HOST'),
                        port=int(env('DB_PORT')),
                        bd_name=env('DATABASE'),
                        )

    return Configs(
        Bot=bot,
        ChatGPT=open_ai_key,
        Data_base=data_base,
    )
