import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path as path

@dataclass
class Message:
    id: int
    text: str | None
    datetime: datetime
    telegarm_message_id: int | None

@dataclass
class AudioMessage(Message):
    file_on_disk: str | None

    def delete_file_from_disc(self):
        if self.check_file_existence():
            os.remove(self.file_on_disk)
            if not self.check_file_existence():
                print(f'Файл по пути {self.file_on_disk} успешно удален')
                return True
            print(f'Файл по пути {self.file_on_disk} еще существует')
            return False

    def check_file_existence(self) -> bool:
        return path(self.file_on_disk).exists()


class IncomeAudioMessage(AudioMessage):
    telegram_file_path: str | None
    file_id: str | int | None



@dataclass
class OutcomeAudioMessage(Message):
    output_audio_path_mp3:str

