from abc import ABC, abstractmethod


class MongoDataBaseRepositoryInterface(ABC):

    @abstractmethod
    def client_repository(self):
        pass

    @abstractmethod
    def prompt_repository(self):
        pass
