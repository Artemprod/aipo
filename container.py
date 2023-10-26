# Контейнер для Dependency Injection. В этом контейнере инициализируются все классы
# _________________________________
import logging
from os import path

from BD.Mongo.monog_db import MongoPromptRepositoryORM, MongoORMConnection, MongoClientUserRepositoryORM, \
    MongoDataBaseRepository
from chat_bot.configs.bot_config import load_bot_config, Configs
from reporter.PDF_creater import PDFGenerator
from reporter.google_sheets.google_sheets import GoogleSheetWorker
from reporter.report_generator import GenerateGPTReport
from reporter.sender import SendDispatcher

# Инициализируем logger
logger = logging.getLogger(__name__)
# Конфиги из .env
config: Configs = load_bot_config(".env")
# создаем Коннект к базе данных
MongoORMConnection(config.Data_base)
# создаем клиентский репозиторий
client_repo = MongoClientUserRepositoryORM()
# создаем проблемный репозиторий
prompt_repo = MongoPromptRepositoryORM()
# Создаем общий репозиторий
data_base_controller = MongoDataBaseRepository(client_repository=client_repo,
                                               prompt_repository=prompt_repo)

# Создаем отправитель
google_sheet = GoogleSheetWorker()
# Создаем репортер
gpt_reporter= GenerateGPTReport(data_base=data_base_controller)
# создаем генератор pdf
pdf_generator = PDFGenerator()
send_dispatcher = SendDispatcher(pdf_generator=pdf_generator,
                                 gpt_reporter=gpt_reporter,
                                 data_base=data_base_controller,
                                 google_sheet_worker=google_sheet)
#Корневая директория
parent_dir = path.dirname(path.abspath(__file__))
print()
#TODO: Добавить сюда чат гпт класс
if __name__ == '__main__':
    send_dispatcher.send_data_to_goggle_sheet(delay=1, frequency=2, regim='gpt_4_categorized')

