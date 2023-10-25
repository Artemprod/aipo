from dataclasses import dataclass
from pymongo import MongoClient


class DataBase:
    ...


@dataclass
class MongoDB:
    bd_name: str
    host: str
    port: int

    def create_client(self) -> MongoClient:
        with MongoClient(self.host, self.port) as client:
            return client
