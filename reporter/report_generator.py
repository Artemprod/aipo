from BD.Mongo.monog_db import MongoDataBaseRepository

from gpt_request import chat_with_chatgpt


class GenerateReport:

    def __init__(self, data_base: MongoDataBaseRepository):
        self.data_base_controller = data_base

    def _form_dialog(self, user_id: int) -> str:
        user_dialog = self.data_base_controller.client_repository.get_user_conversation_by_chat_id(user_telegram_id=user_id)
        dialog_without_system_prompt = [i for i in user_dialog if i['role'] != 'system']
        dialog = self.form_text_dialog(dialog_without_system_prompt)
        return dialog

    @staticmethod
    def _form_full_text_from_list_of_text(text_list: list) -> str:
        """
        Функция формирует текстовый отчет из списка сфоримрована динамически
        под индексом 0 диалог пользвателя
        под остиальными отчет
        :param text_list:
        :return:
        """
        full_text = str()
        for chunk in text_list[1:]:
            full_text += chunk + "\n"
        report = f'История диалога: \n{text_list[0]}\n\nОтчет по диалогу:\n{full_text}'
        print()
        return report

    @staticmethod
    def form_text_dialog(dialog: list[dict]) -> str:
        """
        Функция формирует текст из диалога для анализа
        :param dialog:
        :return:
        """
        message = ''
        for response in dialog:
            role = response['role']
            text = response['content']
            message += f" {role} {text}"
        return message


class GenerateGPTReport(GenerateReport):
    model_3 = "gpt-3.5-turbo"
    model_4 = "gpt-4-0314"
    model_3_16 = "gpt-3.5-turbo-16k-0613"

    def __init__(self, data_base: MongoDataBaseRepository):
        super().__init__(data_base)
        self.model = GenerateGPTReport.model_3

    def get_report_by_user_id(self, user_id: int):
        """
        Получает готовый отчет от chat gpt для конкретного пользователя по его id
        :return:
        """
        system_prompt = self.data_base_controller.prompt_repository.get_report_prompts()
        dialog = self._form_dialog(user_id)
        message_to_send = [*system_prompt,
                           {'role': 'user', 'content': f'{dialog}'}]

        answer_from_gpt = chat_with_chatgpt(message_to_send,
                                            model=self.model)
        report = f'История диалога: \n{dialog}\n\nОтчет по диалогу:\n{answer_from_gpt}'

        return report

    def get_report_by_user_id_dinymic(self, user_id: int):
        """
        Функция генереирует отчет от чтат GPT используя алгоритм  динамическое програмированя
        :param user_id:
        :return:
        """
        # Получаем весь диалог пользователя
        dialog = self._form_dialog(user_id)
        # получаем системные промпты
        system_prompt = self.data_base_controller.prompt_repository.get_report_prompts()
        # Определю базовый случай
        message_to_send_base = [system_prompt[0],
                                {'role': 'user', 'content': f'{dialog}'}]

        answer_from_gpt_base = chat_with_chatgpt(message_to_send_base,
                                                 model=self.model)

        message_result = [dialog, answer_from_gpt_base,]
        # Отсчет с 3 го системного промпта потомуц что 2 первых использовали для базового случая
        for i in range(len(message_result), len(message_result) + len(system_prompt[2:])):
            message_to_send = [system_prompt[i],
                               {'role': 'user', 'content': f'{message_result[i - 2] + message_result[i - 1]}'}]
            message_result.append(chat_with_chatgpt(message_to_send,
                                                    model=self.model))
        return self._form_full_text_from_list_of_text(text_list=message_result)


class GenerateGoogleSheetReport(GenerateReport):
    ...


if __name__ == '__main__':
    ...
