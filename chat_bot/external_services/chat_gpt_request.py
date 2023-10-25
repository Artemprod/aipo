import openai

from chat_bot.configs.bot_config import load_bot_config

config= load_bot_config('.env')
API_KEY = config.ChatGPT.key

openai.api_key = API_KEY
model_3 = "gpt-3.5-turbo"
model_4 = "gpt-4-0314"


def chat_with_chatgpt(messages, model=model_3,):
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
    )
    response_message = response['choices'][0]['message']['content'].strip()
    print('ответ от чата: ' + response_message)
    return response_message