from tkinter import ttk

from ui.docentes import PantallaDocentes
from ui.editor import PantallaEditor
from ui.generar import PantallaGenerar
from ui.horarios import PantallaHorarios
from ui.login import PantallaLogin
from ui.materias import PantallaMaterias
from ui.menu import PantallaMenu
from ui.paralelos import PantallaParalelos
from ui.salones import PantallaSalones

PANTALLAS = {
    "login": PantallaLogin, "menu": PantallaMenu, "materias": PantallaMaterias,
    "docentes": PantallaDocentes, "salones": PantallaSalones, "paralelos": PantallaParalelos,
    "generar": PantallaGenerar, "horarios": PantallaHorarios, "editor": PantallaEditor,
}


class Aplicacion:
    def __init__(self, ventana, fachada):
        self.ventana = ventana
        self.fachada = fachada
        self.__marco = None
        ventana.title("Chronomind · Gestión de horarios FCVT")
        ventana.geometry("1260x800")
        ventana.minsize(1100, 720)
        try:
            ttk.Style().theme_use("clam")
        except Exception:
            pass
        self.mostrar("login")

    def mostrar(self, nombre, **opciones):
        if self.__marco is not None:
            self.__marco.destroy()
        self.__marco = ttk.Frame(self.ventana, padding=16)
        self.__marco.pack(fill="both", expand=True)
        PANTALLAS[nombre](self, self.__marco, self.fachada, **opciones).construir()
