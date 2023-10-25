import asyncio
import os

from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.types import ContentType

from BD.Mongo.monog_db import MongoDataBaseRepository

from chat_bot.services.srvice_functions import make_text_to_speach, get_user_voice_massage_from_telegram_to_local_disk
from gpt_request import chat_with_chatgpt
from speach_to_text import voice_to_text
from aiogram import F

router = Router()


@router.message(F.content_type.in_({ContentType.VOICE,
                                    ContentType.VIDEO}))
async def processed_voice_dialog(message: Message, data_base: MongoDataBaseRepository, bot: Bot):
    # Запускаем функцию которая показывает что бот записывает голосове

    data_base.client_repository.check_user_in_database(message.chat.id)
    # Сохраняем голосовое от пользователя на диске
    file_on_disk = await get_user_voice_massage_from_telegram_to_local_disk(message,
                                                                            bot=bot)
    recognized_text = voice_to_text(file_on_disk)
    data_base.client_repository.update_user_conversation_by_chat_id(user_telegram_id=message.chat.id,
                                                                    answer={"role": "user",
                                                                            "content": str(recognized_text)}
                                                                    )
    conversation = data_base.client_repository.get_conversation_by_user_chat_id_for_GPT_request(
        user_telegram_id=message.chat.id)
    response_from_gpt = chat_with_chatgpt(conversation)
    data_base.client_repository.update_user_conversation_by_chat_id(user_telegram_id=message.chat.id,
                                                                    answer={"role": "assistant",
                                                                            "content": str(response_from_gpt)}
                                                                    )
    ai_generated_voice, path_to_generated_file = make_text_to_speach(response_from_gpt=response_from_gpt,
                                                                     data_from_income_message=message)
    await message.answer_voice(ai_generated_voice, caption=response_from_gpt)
    os.remove(path_to_generated_file)
    os.remove(file_on_disk)


@router.message(F.content_type.in_({ContentType.TEXT}))
async def processed_text_dialog(message: Message, data_base: MongoDataBaseRepository):
    data_base.client_repository.check_user_in_database(message.chat.id)
    data_base.client_repository.update_user_conversation_by_chat_id(user_telegram_id=message.chat.id,
                                                                    answer={"role": "user",
                                                                            "content": str(message.text)}
                                                                    )
    conversation = data_base.client_repository.get_conversation_by_user_chat_id_for_GPT_request(
        user_telegram_id=message.chat.id)
    response_from_gpt = chat_with_chatgpt(conversation)
    data_base.client_repository.update_user_conversation_by_chat_id(user_telegram_id=message.chat.id,
                                                                    answer={"role": "assistant",
                                                                            "content": str(response_from_gpt)}
                                                                    )
    ai_generated_voice, path_to_generated_file = make_text_to_speach(response_from_gpt=response_from_gpt,
                                                                     data_from_income_message=message)
    await message.answer_voice(ai_generated_voice, caption=response_from_gpt)
    os.remove(path_to_generated_file)
