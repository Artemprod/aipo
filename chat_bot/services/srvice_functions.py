from datetime import datetime
from pathlib import Path
from time import sleep
from aiogram import Bot
from aiogram.types import Message, FSInputFile, ContentType

from BD.Mongo.mongo_enteties import Client
from BD.Mongo.monog_db import MongoDataBaseRepository
from text_to_speach import make_tts_audiofile


def save_new_user_if_not_exist(database: MongoDataBaseRepository,
                               data_from_income_message: Message) -> None:
    is_user_in_base = database.client_repository.check_user_in_database(data_from_income_message.chat.id)
    if not is_user_in_base:
        new_user = Client(
            telegram_id=data_from_income_message.chat.id,
            name=data_from_income_message.from_user.first_name,
            date_of_first_using=datetime.now(),
            job=None,
            date_of_review=datetime.now(),
            conversation=[],
        )
        database.client_repository.save_user_to_base(new_user)


def delete_conversation_if_exist(database: MongoDataBaseRepository,
                                 data_from_income_message: Message) -> None:
    is_user_in_base = database.client_repository.check_user_in_database(data_from_income_message.chat.id)
    if not is_user_in_base:
        return
    is_conversation_in_base = database.client_repository.check_conversation_in_user(data_from_income_message.chat.id)
    if is_conversation_in_base:
        try:
            database.client_repository.delete_user_conversation_by_chat_id(data_from_income_message.chat.id)
            print()
        except Exception as e:
            print(e)
    return None


def make_text_to_speach(response_from_gpt: str, data_from_income_message: Message):
    file = make_tts_audiofile(text=response_from_gpt,
                              chat_id=data_from_income_message.chat.id,
                              message_id=data_from_income_message.message_id)
    print()
    return FSInputFile(file), file


async def get_user_voice_massage_from_telegram_to_local_disk(data_from_income_message: Message, bot: Bot):
    """
    Функция сохраняет голосовое сообщение на локальный диск в папку "user_answers"
    :param data_from_income_message:
    :return: path yo file
    """
    if data_from_income_message.content_type == ContentType.VOICE:
        file_id = data_from_income_message.voice.file_id
    elif data_from_income_message.content_type == ContentType.AUDIO:
        file_id = data_from_income_message.audio.file_id
    elif data_from_income_message.content_type == ContentType.DOCUMENT:
        file_id = data_from_income_message.document.file_id
    else:
        await data_from_income_message.reply("Формат документа не поддерживается")
        return

    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path(r'.\user_answers', f"{file_id}.mp3")
    await bot.download_file(file_path, destination=file_on_disk.as_posix())

    return file_on_disk
