import asyncio
import os

from BD.Mongo.monog_db import MongoDataBaseRepository

from aiogram.filters import CommandStart
from aiogram import Router, Bot
from aiogram.types import Message

from chat_bot.lexicon.lexicon_ru import LEXICON_RU
from chat_bot.services.srvice_functions import save_new_user_if_not_exist, make_text_to_speach, \
    delete_conversation_if_exist
from gpt_request import chat_with_chatgpt

router = Router()


@router.message(CommandStart(), )
async def process_start_command(message: Message, data_base: MongoDataBaseRepository):
    # Если у пользователя уже есть разговор то удаляем. Потом нужно дедлать эту логику
    delete_conversation_if_exist(database=data_base,data_from_income_message=message)
    # Сохраняем нового пользователя в базе данных
    save_new_user_if_not_exist(database=data_base,

                               data_from_income_message=message)
    user_name = data_base.client_repository.retrieve_all_data_from_special_user_by_chat_id(
        user_telegram_id=message.chat.id).name
    # Записывааем первый запрос к ИИ в разговор с пользователем
    # first_system_prompt_list = data_base.prompt_repository.get_initial_conversation_prompts()
    # for start_prompt in first_system_prompt_list:

    data_base.client_repository.update_user_conversation_by_chat_id(user_telegram_id=message.chat.id,
                                                                    answer={"role": "system",
                                                                            "content": LEXICON_RU['system_content']}
                                                                    )
    # Извлекаем  разговор с пользователем из базу c индексом
    # TODO: проверить разгор при нажатии start. Если при запуске нового сценария разговор имеется, удалить разговор и начать новый
    conversation = data_base.client_repository.get_conversation_by_user_chat_id_for_GPT_request(
        user_telegram_id=message.chat.id)
    # Получаю ответ от чат бота по API
    print()
    response_from_gpt = chat_with_chatgpt(conversation)
    # Сохраняю ответ от ИИ в разговор с пользователем
    data_base.client_repository.update_user_conversation_by_chat_id(user_telegram_id=message.chat.id,
                                                                    answer={"role": "assistant",
                                                                            "content": response_from_gpt}
                                                                    )
    ai_generated_voice, path_to_generated_file = make_text_to_speach(response_from_gpt=response_from_gpt,
                                                                     data_from_income_message=message)

    await message.answer_voice(ai_generated_voice, caption=response_from_gpt)
    os.remove(path_to_generated_file)
