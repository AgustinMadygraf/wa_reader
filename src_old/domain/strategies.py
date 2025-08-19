"""
Estrategias para análisis de mensajes (patrón Strategy)
"""
from src.entities.interfaces import IMessageParser

class ClasificacionBasicaStrategy(IMessageParser):
    "Estrategia básica: solo detecta máquina, formato, cantidad, personas, turno y observaciones."
    def __init__(self, base_parser):
        self.base_parser = base_parser
    def parse(self, text: str) -> dict:
        return self.base_parser.parse(text)

class ObservacionTareaStrategy(IMessageParser):
    """Estrategia que prioriza la detección de tareas pendientes/finalizadas en observaciones."""
    def __init__(self, base_parser):
        self.base_parser = base_parser
    def parse(self, text: str) -> dict:
        result = self.base_parser.parse(text)
        # Aquí se podría modificar el resultado para priorizar la observación de tareas
        # Por ejemplo, si hay 'Tarea Pendiente' o 'Tarea Finalizada', se puede sobrescribir obs
        if "obs" in result:
            if "Tarea Finalizada" in result["obs"]:
                result["obs"] = "Tarea Finalizada"
            elif "Tarea Pendiente" in result["obs"]:
                result["obs"] = "Tarea Pendiente"
        return result
