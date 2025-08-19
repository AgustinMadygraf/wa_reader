"""
Path: src/interface_adapters/presenters/historial_presenter.py
"""

from tabulate import tabulate
from src.entities.meta_parser import MetaParser

class HistorialPresenter:
    "Presenta el historial de mensajes en CLI"
    def __init__(self, meta_parser: MetaParser):
        self.meta_parser = meta_parser

    def mostrar_tabla_autor_cargo(self, tabla_prev, chat_name):
        "Muestra la tabla con columnas: Fecha, Autor, Mensaje (truncado y ancho fijo), Cargo, Obs"
        ANCHO_FECHA = 12
        ANCHO_AUTOR = 30
        ANCHO_MENSAJE = 40
        ANCHO_CARGO = 14
        ANCHO_OBS = 10
        def ajustar(texto, ancho):
            texto = str(texto) if texto is not None else ""
            if len(texto) > ancho:
                return texto[:ancho-3] + "..."
            return texto.ljust(ancho)
        filas = []
        for fila in tabla_prev:
            if len(fila) == 4:
                fecha, autor, mensaje, obs = fila
            else:
                fecha, autor, mensaje = fila
                obs = ""
            cargo = self.meta_parser.get_cargo(autor)
            fecha = ajustar(fecha, ANCHO_FECHA)
            autor = ajustar(autor, ANCHO_AUTOR)
            # Limpiar saltos de línea en el mensaje
            mensaje = mensaje.replace('\n', ' | ')
            mensaje = ajustar(mensaje, ANCHO_MENSAJE)
            cargo = ajustar(cargo, ANCHO_CARGO)
            obs = ajustar(obs, ANCHO_OBS)
            filas.append([fecha, autor, mensaje, cargo, obs])
        headers = ["Fecha", "Autor", "Mensaje", "Cargo", "Obs"]
        print(f"\nHistorial del chat: {chat_name}\n")
        print("| " + " | ".join([ajustar(h, a) for h, a in zip(headers, [ANCHO_FECHA, ANCHO_AUTOR, ANCHO_MENSAJE, ANCHO_CARGO, ANCHO_OBS])]) + " |")
        print("|" + "|".join(["-" * (a + 2) for a in [ANCHO_FECHA, ANCHO_AUTOR, ANCHO_MENSAJE, ANCHO_CARGO, ANCHO_OBS]]) + "|")
        for fila in filas:
            print("| " + " | ".join(fila) + " |")

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
