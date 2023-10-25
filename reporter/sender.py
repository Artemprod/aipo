import datetime
import json
from abc import ABC, abstractmethod
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from platform import python_version
from time import sleep

from BD.Mongo.mongo_enteties import Client
from BD.Mongo.monog_db import MongoDataBaseRepository
from gpt_request import GPT_MODELS, chat_with_chatgpt
from reporter.PDF_creater import PDFGenerator
from reporter.google_sheets.google_sheets import GoogleSheetWorker
from reporter.report_generator import GenerateGPTReport


class Sender(ABC):

    @abstractmethod
    def send_report(self):
        pass


class EmailSender(Sender):
    server = 'smtp.mail.ru'

    def __init__(self, user: str = 'productreport@mail.ru', password: str = 'HwwYSePjFLCCDc5Tb8xY', **content):
        self._user = user
        self._password = password
        self._file_path: str = str()
        self.sender = self._user
        self._recipients = []
        self.content = content
        self._additional_file_name: str = str()

    @property
    def additional_file_name(self):
        return self._additional_file_name

    @additional_file_name.setter
    def additional_file_name(self, file_name: str):
        self._additional_file_name = file_name

    @property
    def recipients(self):
        if len(self._recipients) == 0:
            raise ValueError("адресвтов нету ввкдите хотя бы 1 email")
        return self._recipients

    @recipients.setter
    def recipients(self, *to_emails):
        if len(to_emails) == 0:
            raise ValueError("адресвтов не введено")
        self._recipients = list(*to_emails)

    def extend_to_emails(self, *to_emails):
        self._recipients.extend(to_emails)

    def append_to_email(self, to_email):
        self._recipients.append(to_email)

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, path):
        self._file_path = path

    @property
    def password(self):
        return self._password

    @property
    def user(self):
        return self._user

    @password.setter
    def password(self, value: str):
        self._password = value

    @user.setter
    def user(self, value: str):
        self._user = value

    def send_report(self):
        if isinstance(self.file_path, str):
            if not os.path.exists(self.file_path):
                print(f"Файл {self.file_path} не существует.")
                return
        basename = os.path.basename(self.additional_file_name)
        if not basename.lower().endswith('.pdf'):
            print(f"Неверное имя файла {basename}. Ожидался файл с расширением .pdf.")
            return

        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.content['subject']
        msg['From'] = self.sender
        msg['To'] = ', '.join(self._recipients)
        msg['Reply-To'] = self.sender
        msg['Return-Path'] = self.sender
        msg['X-Mailer'] = 'Python/' + (python_version())

        part_text = MIMEText(self.content['text'], 'plain')
        part_html = MIMEText(self.content['html'], 'html')

        if isinstance(self.file_path, list):
            for count, path in enumerate(self.file_path):
                part_file = MIMEBase('application', 'pdf; name="{}"'.format(str(count) + "_" + basename))
                part_file.set_payload(open(path, "rb").read())
                if len(part_file.get_payload(decode=True)) == 0:
                    print("Вложение пустое или не удалось прикрепить файл.")
                    continue
                part_file.add_header('Content-Description', str(count) + "_" + basename)
                filesize = os.path.getsize(path)
                part_file.add_header('Content-Disposition',
                                     'attachment; filename="{}"; size={}'.format(str(count) + "_" + basename, filesize))
                encoders.encode_base64(part_file)
                msg.attach(part_file)
        else:
            part_file = MIMEBase('application', 'pdf; name="{}"'.format(basename))
            part_file.set_payload(open(self.file_path, "rb").read())
            if len(part_file.get_payload(decode=True)) == 0:
                print("Вложение пустое или не удалось прикрепить файл.")
            else:
                part_file.add_header('Content-Description', basename)
                filesize = os.path.getsize(self.file_path)
                part_file.add_header('Content-Disposition',
                                     'attachment; filename="{}"; size={}'.format(basename, filesize))
                encoders.encode_base64(part_file)
                msg.attach(part_file)

        msg.attach(part_text)
        msg.attach(part_html)
        mail = smtplib.SMTP_SSL(EmailSender.server)

        mail.login(self.user, self.password)
        mail.sendmail(self.sender, self.recipients, msg.as_string())
        mail.quit()


class TelegramBotSender(Sender):

    def __init__(self, telegram_token):
        self.telegram_token = telegram_token

    def send_report(self):
        pass


class SendDispatcher:
    """
    Класс SendDispatcher (Отправитель) отвечает за отправку отчетов и обработку различных режимов обработки данных.

    Важно учесть, что класс использует внешние модели (SendDispatcher.gpt_models), определенные в GPT_MODELS, и в зависимости
    от заданного режима "match regim", выполняются соответствующие действия, такие как добавление вопросов и ответов,
    объединение диалога в одну ячейку, добавление вопрос-ответ, обработка строк с ответами, а также обработка
    категоризированных ответов с использованием GPT-3 и GPT-4.

    Данный класс позволяет эффективно отправлять и структурировать данные для клиента в зависимости от заданных правил и
    режимов обработки данных.
    """
    gpt_models = GPT_MODELS

    # FIXME возможные проблемы с гугл шит передачей айди странице для прототипа пока так но потом нужно проверить работоспособность
    def __init__(self,
                 pdf_generator: PDFGenerator,
                 gpt_reporter: GenerateGPTReport,
                 email_sender: EmailSender | None = None,
                 data_base: MongoDataBaseRepository = None,
                 google_sheet_worker: GoogleSheetWorker | None = None,

                 ):
        self.email_sender = email_sender
        self.data_base_controller = data_base
        self.google_sheet_worker = google_sheet_worker
        self.pdf_generator = pdf_generator
        self.gpt_reporter = gpt_reporter


    def send_report_on_demand(self):
        """
        Функция отправляет отчеты по требованию
        :return:
        """
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        print()
        clients_objects = self.data_base_controller.client_repository.retrieve_all_data_from_all_users()
        for client in clients_objects:
            # TODO: переделать пути к файлу. Вынести название каталога
            if not os.path.exists(f'reports/{today}'):
                # Если папки нет, то создаем её
                os.makedirs(f'reports/{today}')
            output_filename_for_report = Path(f'reports/{today}',
                                              f'{client.name}_{client.telegram_id}_{client.date_of_review.strftime("%d_%B_%Y_%A")}_report.pdf').resolve().as_posix()
            self.pdf_generator.create_pdf_from_text(
                text=self.gpt_reporter.get_report_by_user_id_dinymic(client.telegram_id),
                output_filename=output_filename_for_report, font_size=10)
        files_paths = os.listdir(f'reports/{today}')
        files_pathies = [Path(f'reports/{today}', path).resolve().as_posix() for path in files_paths]
        self.email_sender.file_path = files_pathies
        # TODO: Вынести создания названий для файлов выше
        self.email_sender.additional_file_name = 'report.pdf'
        self.email_sender.send_report()

    def send_report_by_time(self, delay=24 * 3600, frequency: int = 60 * 10):
        """
        Функция проверяте каждые N минут отчеты
        :return:
        """

        while True:
            today = datetime.datetime.today().strftime("%Y-%m-%d")
            clients_objects = [client for client in
                               self.data_base_controller.client_repository.retrieve_all_data_from_all_users() if
                               not self.data_base_controller.client_repository.check_report_send(client.telegram_id)]
            if len(clients_objects) == 0:
                continue
            for client in clients_objects:
                if self._check_time(client.date_of_review,
                                    delay=delay):
                    # TODO: переделать пути к файлу. Вынести название каталога
                    if not os.path.exists(f'reports/{today}'):
                        # Если папки нет, то создаем её
                        os.makedirs(f'reports/{today}')
                    output_filename_for_report = Path(f'reports/{today}',
                                                      f'{client.name}_{client.telegram_id}_{client.date_of_review.strftime("%d_%B_%Y_%A")}_report.pdf').resolve().as_posix()

                    self.pdf_generator.create_pdf_from_text(
                        text=self.gpt_reporter.get_report_by_user_id_dinymic(client.telegram_id),
                        output_filename=output_filename_for_report, font_size=10)
                    self.email_sender.file_path = output_filename_for_report
                    # TODO: Вынести создания названий для файлов выше
                    self.email_sender.additional_file_name = 'report.pdf'
                    self.email_sender.send_report()
                    self.data_base_controller.client_repository.set_report_send(client.telegram_id)
            sleep(frequency)

    @staticmethod
    def _check_time(data: datetime.datetime, delay) -> bool:
        period = datetime.datetime.now() - data

        return period.total_seconds() >= delay

    def send_data_to_goggle_sheet(self, regim='gpt_3_categorized', delay=24 * 3600, frequency: int = 2):
        """
        Метод создает новую строку с данными каждый новый раз спустя 24 часа после завершщения диалога с пользоватиелм
        :return:
        """

        def add_ful_dialog_in_one_cell(client: Client):
            self.google_sheet_worker.append_data_in_row(client.name, client.telegram_id,
                                                        client.date_of_review.strftime("%Y-%m-%d %H:%M:%S"),
                                                        self._format_dialogue(client.conversation))

        # TODO: доделать
        def add_question_answer(client: Client):
            for i in list(client._fields):
                print(client[i])

        def add_qa_rows(client: Client):
            ...

        def add_only_answers(client: Client):
            data = [client[i] for i in list(client._fields) if
                    not isinstance(client[i], list) and i != 'id' and client[i]]
            answers = [i['content'] for i in client.conversation if i['role'] != 'system' and i['role'] != 'assistant']
            data = data + answers
            for index, date_time in enumerate(data):
                if isinstance(date_time, datetime.datetime):
                    data[index] = date_time.strftime("%Y-%m-%d %H:%M:%S")
            print()
            self.google_sheet_worker.append_data_in_row(*data)

        def add_categorized_answer(client: Client, model):
            """
                Метод send_data_to_goggle_sheet отвечает за отправку данных в Google Sheets в зависимости от заданного режима.

                Параметры:
                - regim: Режим обработки данных (по умолчанию "gpt_3_categorized").
                - delay: Задержка между отправками данных (по умолчанию 24 часа).
                - frequency: Частота проверки и отправки данных (по умолчанию каждые 10 минут).

                Описание:
                Метод создает новую строку с данными каждый новый раз спустя 24 часа после завершения диалога с пользователем.

                В зависимости от заданного режима обработки данных (regim), метод добавляет данные в Google Sheets. Поддерживаются
                следующие режимы:
                - "column": Добавление вопросов и ответов клиента в виде столбцов.
                - "cell": Объединение всего диалога клиента в одну ячейку.
                - "qa": Добавление данных в определенные ячейки.
                - "row": Добавление только ответов клиента в виде строки.
                - "gpt_3_categorized": Обработка данных с использованием модели GPT-3 (модель указывается в параметрах).
                - "gpt_4_categorized": Обработка данных с использованием модели GPT-4 (модель указывается в параметрах).

                Метод также обновляет статус отправки отчета и выполняет проверку для всех клиентов, указанных в базе данных. Если
                задержка (delay) прошла после завершения диалога клиента, данные добавляются в Google Sheets в соответствии с выбранным
                режимом.

                По окончанию обработки, метод ожидает указанный интервал (frequency) перед следующей проверкой и отправкой данных.
                """
            gpt_system_prompt = self.data_base_controller.prompt_repository.get_category_system_prompts()
            user_dialog = client.conversation
            dialog_without_system_prompt = [i for i in user_dialog if i['role'] != 'system']
            dialog = self.gpt_reporter.form_text_dialog(dialog_without_system_prompt)
            message_to_gpt = [gpt_system_prompt, {'role': 'user', 'content': f'{dialog}'}]
            response = chat_with_chatgpt(message_to_gpt, model=model, max_tokens=500)
            serialized = dict()
            try:
                serialized = json.loads(response)
            except Exception as e:
                print(e)
            data_to_list = [value for value in serialized.values()]
            data = [client[i] for i in list(client._fields) if
                    not isinstance(client[i], list) and i != 'id' and client[i]]
            data = data + data_to_list
            for index, date_time in enumerate(data):
                if isinstance(date_time, datetime.datetime):
                    data[index] = date_time.strftime("%Y-%m-%d %H:%M:%S")
            self.google_sheet_worker.append_data_in_row(*data)
            print()

        while True:
            clients_objects = [client for client in
                               self.data_base_controller.client_repository.retrieve_all_data_from_all_users() if
                               not self.data_base_controller.client_repository.check_report_send(client.telegram_id)]
            if len(clients_objects) == 0:
                continue
            # Извлекаем данные с базы двнных
            for client in clients_objects:
                if self._check_time(client.date_of_review, delay=delay):
                    match regim:
                        case "column":
                            add_question_answer(client)
                        case "cell":
                            add_ful_dialog_in_one_cell(client)
                        case "qa":
                            add_qa_rows(client)
                        case "row":
                            add_only_answers(client)
                        case "gpt_3_categorized":
                            print()
                            add_categorized_answer(client, model=SendDispatcher.gpt_models.model_3)
                        case "gpt_4_categorized":
                            print()
                            add_categorized_answer(client, model=SendDispatcher.gpt_models.model_4)

                    # Стаим что отчет послан
                    self.data_base_controller.client_repository.set_report_send(client.telegram_id)
            sleep(frequency)

    def form_dataset_from_client(self, client: Client):
        """
        на выходе
        :param client:
        :return:
        """
        for i in list(client._fields):
            print(client[i])

    @staticmethod
    def _format_dialogue(dialogue: list[dict]):
        formatted_text = ""
        for message in dialogue:
            if message['role'] == 'system':
                # Пропускаем сообщения роли 'system'
                continue
            elif message['role'] == 'user':
                user_name = message.get('user_name', 'Пользователь')
                content = message['content']
                formatted_text += f'{user_name}: {content}\n'
            elif message['role'] == 'assistant':
                assistant_name = message.get('assistant_name', 'Система')
                content = message['content']
                formatted_text += f'{assistant_name}: {content}\n'
        print()
        return formatted_text


if __name__ == '__main__':
    ...
    # subject = 'Проверка отправки отчета на почту'
    # text = 'Текст сообщения <h1>Здравствуйте Александр, вот ваш отчет по иследованию продукта</h1> бла бла тут еще что то '
    # html = '<html><head></head><body><p>' + text + '</p></body></html>'
    # a = EmailSender(subject=subject, text=text, html=html)
    # print(a.user)
    # a.recipients = 'artemprod1@gmail.com',
    # print(a.recipients)
    # print(a.content)
    #

    # # # dispatcer.send_report_by_time()
    # # dispatcer.send_report_on_demand()
