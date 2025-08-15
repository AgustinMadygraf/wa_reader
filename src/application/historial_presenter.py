"""
Path: src/application/historial_presenter.py
"""

from tabulate import tabulate
from src.domain.meta_parser import MetaParser

class HistorialPresenter:
    "Presenta el historial de mensajes en CLI"
    def mostrar_tabla_autor_cargo(self, tabla_prev, chat_name):
        "Muestra la tabla con columnas: Fecha, Autor, Mensaje (truncado), Cargo"
        filas = []
        for fecha, autor, mensaje in tabla_prev:
            cargo = MetaParser.get_cargo(autor)
            mensaje_trunc = self.truncar_mensaje(mensaje, 40)
            filas.append([fecha, autor, mensaje_trunc, cargo])
        print(f"\nHistorial del chat: {chat_name}\n")
        print(tabulate(
            filas,
            headers=["Fecha", "Autor", "Mensaje", "Cargo"],
            tablefmt="github",
            showindex=False
        ))

    @staticmethod
    def truncar_mensaje(mensaje: str, max_len: int = 40) -> str:
        "Trunca el mensaje a max_len caracteres, agregando '...' si es necesario."
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
