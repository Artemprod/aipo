from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    telegram_id: int
    name: str | None
    date_of_first_using: datetime


@dataclass
class ProductManager(User):
    post: str | None
    last_visit: datetime | None


# сохроняем разговор в клиента
@dataclass
class Clients(User):
    job: str | None
    date_of_review: datetime | None
    conversation: list[dict] | None
