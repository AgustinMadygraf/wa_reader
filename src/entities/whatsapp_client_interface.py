"""
Path: src/entities/whatsapp_client_interface.py
"""

from abc import ABC, abstractmethod

class IWhatsAppClient(ABC):
    "Interfaz para el cliente de WhatsApp"
    @abstractmethod
    def initialize(self):
        "Inicializa el cliente de WhatsApp."
        pass

    @abstractmethod
    def open_chat(self, chat_name: str):
        "Abre un chat en WhatsApp."
        pass

    @abstractmethod
    def get_messages(self) -> list:
        "Obtiene los mensajes del chat actual."
        pass

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
