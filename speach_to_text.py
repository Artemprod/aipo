from io import BytesIO
import vosk
import json
from pydub import AudioSegment
from os import path

from container import parent_dir

model_path = path.normpath(path.join(parent_dir, 'model', 'vosk-model-small-ru-0.22'))
model = vosk.Model(model_path)
samplerate = 16000


def ogg_to_mp3_in_memory(ogg_data):
    try:
        # Преобразовываем данные OGG в BytesIO объект
        ogg_bytes = BytesIO(ogg_data)

        # Загружаем аудио из BytesIO
        audio = AudioSegment.from_file(ogg_bytes, format="ogg")

        # Создаем BytesIO для хранения MP3 данных
        mp3_bytes = BytesIO()

        # Экспортируем аудио в формате MP3 в BytesIO
        audio.export(mp3_bytes, format="mp3")

        # Получаем MP3 данные из BytesIO
        mp3_data = mp3_bytes.getvalue()

        return mp3_data
    except Exception as e:
        print(f"Ошибка при конвертации: {str(e)}")
        return None


def voice_message_recognition(voice_message_path):
    audio_segment = AudioSegment.from_file(voice_message_path, format='ogg',
                                           )

    # Конвертируем OGG данные в MP3 в памяти
    mp3_bytes = BytesIO()
    # Экспортируем аудио в формате MP3 в BytesIO
    audio_segment.export(mp3_bytes, format="mp3")
    # Получаем MP3 данные из BytesIO
    mp3_data = mp3_bytes.getvalue()
    try:
        # Загружаем аудиофайл из MP3 данных
        audio = AudioSegment.from_mp3(BytesIO(mp3_data))
    except Exception as e:
        print("Ошибка загрузки аудиофайла:", str(e))
        return

    # Преобразуем аудиофайл в WAV формат
    audio = audio.set_channels(1)  # Преобразовываем в моно для Vosk
    audio = audio.set_frame_rate(samplerate)
    audio_data = audio.raw_data
    # Инициализируем KaldiRecognizer с моделью
    rec = vosk.KaldiRecognizer(model, samplerate)
    # Производим распознавание аудио
    rec.AcceptWaveform(audio_data)
    # Получаем результат в виде JSON
    result = json.loads(rec.Result())
    recognized_text = result["text"]
    return recognized_text


def voice_to_text(voice_message_path):
    transcribed_text = voice_message_recognition(voice_message_path)
    if transcribed_text:
        print("Распознанный текст:", transcribed_text)
        return transcribed_text


if __name__ == '__main__':
    print()
