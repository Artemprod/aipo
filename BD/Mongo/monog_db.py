from BD.Mongo.mongo_enteties import Client, Prompt
from chat_bot.configs.bot_config import load_bot_config
from chat_bot.enteties.database import MongoDB
from mongoengine import connect, DoesNotExist


class MongoORMConnection:
    def __init__(self, mongo: MongoDB):
        connect(db=mongo.bd_name,
                host=mongo.host,
                port=mongo.port)


class MongoClientUserRepositoryORM:
    @staticmethod
    def check_report_send(user_telegram_id: int) -> bool:
        document = Client.objects(telegram_id=user_telegram_id).get()
        print()
        return document.report_send

    @staticmethod
    def set_report_send(user_telegram_id: int) -> None:
        document = Client.objects(telegram_id=user_telegram_id).get()
        document.report_send = True
        document.save()
        print(f'Отметка об отправке отчета установлена для пользователя {document.telegram_id}')

    @staticmethod
    def save_user_to_base(user: Client) -> None:
        user.save()
        print(f"пользователь c id: {Client.id}\nзанесен в базу \n {Client.objects}")

    @staticmethod
    def update_user_conversation_by_chat_id(user_telegram_id: int, answer: dict) -> None:
        user_to_update = Client.objects(telegram_id=user_telegram_id).get()
        user_to_update.conversation.append(answer)
        user_to_update.save()
        print(f"для пользователя c id: {user_telegram_id} \nответ: {answer}  \nзанесен в базу")

    @staticmethod
    def get_user_conversation_by_chat_id(user_telegram_id) -> list:
        user_answer = Client.objects(telegram_id=user_telegram_id).only("conversation").first()
        return user_answer.conversation

    @staticmethod
    def delete_user_conversation_by_chat_id(user_telegram_id):
        user= Client.objects(telegram_id=user_telegram_id).first()
        print()
        if user:
            user.conversation = []  # Присвоим пустой список полю conversation
            user.save()
            print(f"Разговор для пользователя c id: {user_telegram_id} удален")




    @staticmethod
    def get_conversation_by_user_chat_id_for_GPT_request(user_telegram_id) -> list:
        user_answer = Client.objects(telegram_id=user_telegram_id).only("conversation").first()
        if len(user_answer.conversation) > 5:
            short_dialog = [user_answer.conversation[0]] + user_answer.conversation[-5:]
            return short_dialog
        return user_answer.conversation

    @staticmethod
    def retrieve_all_data_from_special_user_by_chat_id(user_telegram_id):
        user_data = Client.objects(telegram_id=user_telegram_id).get()
        return user_data

    @staticmethod
    def check_user_in_database(user_telegram_id) -> bool:
        """
        проверяем пользователя в базе данных
        :return: bool
        """

        try:
            Client.objects(telegram_id=user_telegram_id).get()
            print(f"Пользователя с id: {user_telegram_id} \nесть в базе")
            return True
        except DoesNotExist:
            print(f"Пользователя с id: {user_telegram_id} \nне существует в базе данных")
            return False

    @staticmethod
    def check_conversation_in_user(user_telegram_id) -> bool:
        """
        проверяем разговор у пользователя
        :return: bool
        """
        client = Client.objects(telegram_id=user_telegram_id).get()
        if len(client.conversation) > 0:
            print(f"Разговор: {client.conversation} \nесть у пользователя")
            return True
        print(f"Разговора нет у пользователя")
        return False

    @staticmethod
    def retrieve_all_data_from_all_users():
        user_data = Client.objects()
        return user_data


class MongoPromptRepositoryORM:

    def get_initial_conversation_prompts(self) -> list:
        conversation = [self.get_start_system_prompts()]
        for i in [promt for promt in self.get_assistant_prompts()]:
            conversation.append(i)
        print()
        return conversation

    def get_start_system_prompts(self):
        prompt_object = Prompt.objects(type="start_conversation", rule="discription").first()
        prompt = {"role": "system", "content": self._crop_prompt(prompt_object.promt)}
        return prompt

    def get_category_system_prompts(self):
        prompt_object = Prompt.objects(type="categorization", rule="report").first()
        prompt = {"role": "system", "content": self._crop_prompt(prompt_object.promt)}
        return prompt

    def get_assistant_prompts(self):
        prompts_objects = Prompt.objects(type="start_conversation")
        conversation_initiation = []
        assistant_prompts = [prompt.promt for prompt in prompts_objects if prompt.rule != "discription"]
        print()
        for assistant in assistant_prompts:
            prompt = {"role": "assistant", "content": self._crop_prompt(assistant)}
            conversation_initiation.append(prompt)

        return conversation_initiation

    def get_report_prompts(self) -> list:
        prompts_objects = Prompt.objects(type="make_report")
        conversation_report = []
        for prompt in prompts_objects:
            system_prompt = {"role": "system", "content": self._crop_prompt(prompt.promt)}
            conversation_report.append(system_prompt)
        return conversation_report

    @staticmethod
    def _crop_prompt(prompt: str):
        prompt_text = str(prompt).replace('\n', '')
        cropped_prompt = prompt_text if len(prompt_text) <= 4000 else prompt_text[:4000]
        return cropped_prompt


class MongoDataBaseRepository:

    def __init__(self, client_repository: MongoClientUserRepositoryORM,
                 prompt_repository: MongoPromptRepositoryORM):
        self.client_repository = client_repository
        self.prompt_repository = prompt_repository

    def client_repository(self):
        return self.client_repository

    def prompt_repository(self):
        return self.prompt_repository


if __name__ == '__main__':
    configs = load_bot_config('.env')
    mongo_db = MongoDB(
        bd_name=configs.Data_base.bd_name,
        host=configs.Data_base.host,
        port=int(configs.Data_base.port),

    )
    MongoORMConnection(mongo_db)
    # a = MongoPromptRepositoryORM()
    # a.get_initial_conversation_prompts()
    b = MongoClientUserRepositoryORM()
    b.get_conversation_by_user_chat_id_for_GPT_request(370357284)

    #     cl_1 = Client(
    #     telegram_id = 123,
    #     name = 'джон',
    #     date_of_first_using = '01.02.2023',
    #     job = 'строитель',
    #     date_of_review = '01.02.2023',
    #     conversation = [
    #                        {"role": "assistent", "content": "ответ на бла бла бла "}
    #
    #                    ],
    # )

    # user_repo = MongoClientUserRepositoryORM(mongo_db)
    # user_repo.save_answer(cl_1)

    # conversation = {"role": "user", "content": "ЭТО АППЕНД"}
    print()
    # user_repo.save_answer(cl_1)
    # user_repo.update_user_answer_by_chatid(user_telegram_id=123, conversation=conversation)
    # data: Client = user_repo.retrieve_all_data_from_special_user_by_chatid(user_telegram_id=123)
    print()
    # print(data.conversation)
    # print(user_repo.check_user_in_database(user_telegram_id=12))
