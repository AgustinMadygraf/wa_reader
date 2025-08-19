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
        "Muestra la tabla con columnas: Fecha, Autor, Mensaje (truncado y ancho fijo)"
        ANCHO_FECHA = 12
        ANCHO_AUTOR = 30
        ANCHO_MENSAJE = 40
        try:
            from wcwidth import wcswidth
        except ImportError:
            def wcswidth(text):
                return len(text)
        def ajustar(texto, ancho):
            texto = str(texto) if texto is not None else ""
            texto = texto.replace('\n', ' | ')
            visual = wcswidth(texto)
            if visual > ancho:
                acc = ''
                total = 0
                for c in texto:
                    w = wcswidth(c)
                    if total + w > ancho - 3:
                        break
                    acc += c
                    total += w
                return acc + '...'
            pad = ' ' * (ancho - visual)
            return texto + pad
        filas = []
        for fila in tabla_prev:
            if len(fila) >= 3:
                fecha, autor, mensaje = fila[:3]
            else:
                fecha, autor, mensaje = (fila + ["", "", ""])[:3]
            fecha = ajustar(fecha, ANCHO_FECHA)
            autor = ajustar(autor, ANCHO_AUTOR)
            mensaje = ajustar(mensaje, ANCHO_MENSAJE)
            filas.append([fecha, autor, mensaje])
        headers = ["Fecha", "Autor", "Mensaje"]
        print(f"\nTabla datos crudos: {chat_name}\n")
        print("| " + " | ".join([ajustar(h, a) for h, a in zip(headers, [ANCHO_FECHA, ANCHO_AUTOR, ANCHO_MENSAJE])]) + " |")
        print("|" + "|".join(["-" * (a + 2) for a in [ANCHO_FECHA, ANCHO_AUTOR, ANCHO_MENSAJE]]) + "|")
        for fila in filas:
            print("| " + " | ".join(fila) + " |")

    @staticmethod
    def truncar_mensaje(mensaje: str, max_len: int = 40) -> str:
        "Trunca el mensaje a max_len caracteres, agregando '...' si es necesario."
        if len(mensaje) > max_len:
            return mensaje[:max_len-3] + '...'
        return mensaje
    def mostrar_tabla_cruda(self, tabla_prev, _chat_name):
        "Muestra la tabla cruda de mensajes (solo Fecha, Autor, Mensaje truncado)"
        import logging
        logger = logging.getLogger("wa_reader.historial")
        logger.debug("Mostrando tabla de datos crudos")
        ANCHO_FECHA = 12
        ANCHO_AUTOR = 30
        ANCHO_MENSAJE = 40
        def ajustar(texto, ancho):
            texto = str(texto) if texto is not None else ""
            texto = texto.replace('\n', ' | ')
            if len(texto) > ancho:
                return texto[:ancho-3] + "..."
            return texto.ljust(ancho)
        filas = []
        for fila in tabla_prev:
            # Mantener estructura, pero solo mostrar los primeros tres campos
            if len(fila) >= 3:
                fecha, autor, mensaje = fila[:3]
            else:
                fecha, autor, mensaje = (fila + ["", "", ""])[:3]
            fecha = ajustar(fecha, ANCHO_FECHA)
            autor = ajustar(autor, ANCHO_AUTOR)
            mensaje = ajustar(mensaje, ANCHO_MENSAJE)
            filas.append([fecha, autor, mensaje])
        headers = ["Fecha", "Autor", "Mensaje"]
        print("\nMensajes crudos del chat:\n")
        print("| " + " | ".join([ajustar(h, a) for h, a in zip(headers, [ANCHO_FECHA, ANCHO_AUTOR, ANCHO_MENSAJE])]) + " |")
        print("|" + "|".join(["-" * (a + 2) for a in [ANCHO_FECHA, ANCHO_AUTOR, ANCHO_MENSAJE]]) + "|")
        for fila in filas:
            print("| " + " | ".join(fila) + " |")

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
