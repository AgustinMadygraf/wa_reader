from abc import ABC, abstractmethod

class IWhatsAppClient(ABC):
    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def open_chat(self, chat_name: str):
        pass

    @abstractmethod
    def get_messages(self) -> list:
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
