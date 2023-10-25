from mongoengine import Document, IntField, StringField, DateTimeField, ListField, BooleanField


class ProductManager(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    post = StringField()
    last_visit = DateTimeField()

    meta = {
        'collection': 'ProductManager'  # Здесь указывается имя коллекции
    }


class Client(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    job = StringField()
    date_of_review = DateTimeField()
    conversation = ListField()
    report_send = BooleanField()
    meta = {
        'collection': 'Client'  # Здесь указывается имя коллекции
    }


class Prompt(Document):
    promt = StringField()
    type = StringField()
    estimation = IntField()
    rule = StringField()

    meta = {
        'collection': 'SystemPromts'  # Здесь указывается имя коллекции
    }
