"""
Path: src/application/historial_presenter.py
"""

from tabulate import tabulate

class HistorialPresenter:
    "Presenta el historial de mensajes en CLI"
    @staticmethod
    def truncar_mensaje(mensaje: str, max_len: int = 40) -> str:
        """Trunca el mensaje a max_len caracteres, agregando '...' si es necesario."""
        if len(mensaje) > max_len:
            return mensaje[:max_len-3] + '...'
        return mensaje
    def mostrar_tabla_cruda(self, tabla_prev, _chat_name):
        "Muestra la tabla cruda de mensajes"
        print("\nMensajes crudos del chat:\n")
        print(tabulate(
            tabla_prev,
            headers=["Fecha", "Autor", "Mensaje"],
            tablefmt="github",
            showindex=False
        ))

    def mostrar_tabla_procesada(self, tabla, chat_name):
        "Muestra la tabla procesada de mensajes"
        fecha = tabla[0][0] if tabla and tabla[0][0] else "(sin datos)"
        print(f"\nHistorial del chat: {chat_name} - Fecha: {fecha}\n")
        print(tabulate(
            tabla,
            headers=["Fecha", "Máquina", "Formato", "Cantidad", "Turno", "Personas", "Obs"],
            tablefmt="github",
            showindex=False
        ))
