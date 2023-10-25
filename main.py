# from speach_to_text import transctibe_speach_to_text
# from gpt_request import chat_with_chatgpt
# from text_to_speach import text_to_speach
from functools import wraps
import time

from gpt_request import chating_with_gpt, chat_with_chatgpt
from speach_to_text import voice_to_text

system_content="""
Ты продакт менеджер который проводит интервью по 
продукту. Не выходи из роли заставь пользвоателя рассказать о проблемах.
Представься и начни опрашивать полььзователя
"""


def timer(func):

    @wraps(func)
    def wraper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f'скорость процесса от транскрибации до сохранения аудио = {round(execution_time)} сек.')
        return result

    return wraper




#v1
# @timer
# def main(voice_message_path):
#     income_user_voice_message = transctibe_speach_to_text(voice_message_path)
#     print(f'транскрибация аудиофайла {income_user_voice_message}')
#     request_to_gpt = chat_with_chatgpt(prompt=income_user_voice_message,
#                                        system_content="Ты продакт менеджер который проводит проблемное интервью")
#     print(f'Ответ от chat ЖПТ:   {request_to_gpt}')
#     text_to_speach(request_to_gpt)
#     print('файл с аудио отвтетом от гпт сохранен')

#v2
def main():
    messages = [
        {"role": "system", "content": system_content},
    ]
    while True:
        response_from_chat = chat_with_chatgpt(messages=messages)
        user_response = {"role": "user", "content": str(input('введи ответ'))}
        assistant = {"role": "assistant", "content": response_from_chat}
        messages.append(assistant)
        messages.append(user_response)

if __name__ == '__main__':
    # voice_message_path = r'D:\python projects\non_comertial\auto_cust_dev\audio_samples\audio_2023-09-13_16-03-42.ogg'
    # main(voice_message_path)
    ...

