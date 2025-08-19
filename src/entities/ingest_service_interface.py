from abc import ABC, abstractmethod

class IIngestService(ABC):
    @abstractmethod
    def send(self, payload: dict) -> str:
        pass
