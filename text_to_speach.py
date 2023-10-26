import io
import os
from datetime import datetime

import torchaudio
from gtts import gTTS
import torch
import sounddevice as sd
import time
from pydub import AudioSegment
from functools import wraps
from pathlib import Path as path

from elevenlabs import generate, save, set_api_key
from environs import Env

from container import parent_dir

env: Env = Env()
env.read_env('.env')
set_api_key(env("ELEVEN_API_KEY"))

language = 'ru'
model_id = 'v4_ru'
sample_rate = 24000  # 48000
speaker = 'kseniya'  # aidar, baya, kseniya, xenia, random, eugene
put_accent = True
put_yo = True
device = torch.device('cpu')  # cpu или gpu
text = "да я часто пользуются этим продуктам и могу сказать что он отвратительной"

model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language=language,
                          speaker=model_id)
model.to(device)


def timer(func):
    @wraps(func)
    def wraper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        estimation = end_time - start_time
        print(f"Время синтеза речи: {round(estimation)} сек.")
        return result

    return wraper


# воспроизводим
def va_speak(what: str):
    audio = model.apply_tts(text=what + "..",
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo)

    sd.play(audio, sample_rate * 1.05)


def make_tts_audiofile(text, chat_id, message_id, voice_generator='elevenlabs'):
    """

    :param text:
    :param chat_id:
    :param message_id:
    :param voice_generator: elevenlabs, silero
    :return:
    """
    match voice_generator:
        case 'elevenlabs':
            return text_to_speach_elevenlabs(text, chat_id, message_id)

        case 'silero':
            return text_to_speach_silero(text, chat_id, message_id)


def text_to_speach_silero(text, chat_id, message_id):
    make_path_wav = os.path.normpath(
        os.path.join(parent_dir, 'ai_answers', f'{chat_id}_{message_id}_{datetime.now().strftime("%Y%H%M%S")}.wav'))
    make_path_mp3 = os.path.normpath(
        os.path.join(parent_dir, 'ai_answers', f'{chat_id}_{message_id}_{datetime.now().strftime("%Y%H%M%S")}.mp3'))
    # Переаодим текст в речь с имользованием модели и настроек
    audio = model.apply_tts(text=text + "..",
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo)

    print(f'Текст переведен в рчеь')
    # сохраняем аудиофайл
    torchaudio.save(make_path_wav,
                    audio.unsqueeze(0),
                    sample_rate=sample_rate,

                    )
    audio = AudioSegment.from_wav(make_path_wav)
    # Сохранение аудиофайл в формате mp3

    audio.export(make_path_mp3, format="mp3")
    # Удаляем WAV файл c диска
    os.remove(make_path_wav)
    if not path(make_path_wav).exists():
        print(f'файл wav по пути {make_path_wav} удален')
        return make_path_mp3


def text_to_speach_elevenlabs(text, chat_id, message_id, voice="Michael"):
    audio = generate(
        text=text,
        voice=voice,
        model="eleven_multilingual_v2"
    )

    filename = os.path.normpath(
        os.path.join(parent_dir,"ai_answers",
                            f'{chat_id}_{message_id}_{datetime.now().strftime("%Y%H%M%S")}.mp3'))
    save(audio, filename=filename)
    return os.path.normpath(filename)


def tts_to_ogg(text, ):
    # Переаодим текст в речь с имользованием модели и настроек
    audio = model.apply_tts(text=text + "..",
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo)

    # Преобразуем аудио в формат AudioSegment (нужно установить pydub)
    audio_np = audio.squeeze().detach().cpu().numpy()  # Преобразование в NumPy массив
    audio_segment = AudioSegment(
        audio_np.tobytes(),
        frame_rate=sample_rate,
        sample_width=audio_np.dtype.itemsize,
        channels=1  # Моно звук
    )

    # Преобразуем аудио в формат ogg и возвращаем как поток данных (bytes)
    ogg_audio_stream = io.BytesIO()
    audio_segment.export(ogg_audio_stream, format="ogg")
    ogg_audio_stream.seek(0)
    print()
    return ogg_audio_stream


def text_to_speach_via_api(text: str, file_name, lang: str = 'ru'):
    tts = gTTS(text, lang=lang, slow=False)
    tts.save(file_name)


if __name__ == '__main__':
    print()
