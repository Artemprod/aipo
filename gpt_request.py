import time
from dataclasses import dataclass

import openai
from environs import Env

env: Env = Env()
env.read_env('.env')

API_KEY = env("OPEN_AI_API_KEK")
openai.api_key = API_KEY
model_3 = "gpt-3.5-turbo"
model_4 = "gpt-4-0314"
model_3_16 = "gpt-3.5-turbo-16k-0613"

#TODO сделать это отдельным классом
@dataclass
class GPT_MODELS:
    model_3: str = "gpt-3.5-turbo"
    model_4: str = "gpt-4-0314"
    model_3_16: str = "gpt-3.5-turbo-16k-0613"


def chat_with_chatgpt(messages, model=GPT_MODELS.model_3, max_tokens=300):
    print(messages)
    response = openai.ChatCompletion.create(
        model=model,
        timeout=6000,
        messages=messages,
        n=1,
        stop=None,
        temperature=0.4,
        frequency_penalty=0,
        top_p=0.8,
        presence_penalty=-0,
        max_tokens=max_tokens
    )
    response_message = response['choices'][0]['message']['content'].strip()
    print('ответ от чата: ' + response_message)
    return response_message


if __name__ == '__main__':
    system_content = """
    Ты професилнальный DevOps инжинер который запускает приложение на сервере при помощи Docker и Docker-compose.
    Твоя задача помочь развернуть приложение на сервере AWS и в конеце удаленно подключиться к контейнеру в котором база данных MongoDB который на сервере
    через Mongo compas. Подобно давай рекомендации и команды которые необходимо выполнить.
    """
    a = "Как подключиться к AWS сервера по URI mongodb://35.154.112.249 :27018/Ошибка connect ETIMEDOUT 35.154.112.249:27018"
    data = [{"role": "system", "content": system_content},]
    exit_command = 0
    while True:
        if exit_command == 1:
            break
        time.sleep(5)
        question = input(str("Введи вопрос: "))
        if len(data)>5:
            data.pop(1)

        user_content = {"role": "user",
                        "content":question}
        data.append(user_content)
        response_from_gpt = {"role": "assistant", "content": chat_with_chatgpt(data,model=GPT_MODELS.model_4, max_tokens=5000)}
        data.append(response_from_gpt)
        time.sleep(10)
        print()
