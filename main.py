"""Chronomind: único punto de entrada del proyecto.  Ejecutar:  python main.py"""
import tkinter as tk
from pathlib import Path

from persistencia.gestor_archivos import GestorArchivos
from persistencia.repositorio import RepositorioJSON
from servicios.autenticacion import ServicioAutenticacion
from servicios.catalogo import Catalogo
from servicios.fachada import FachadaChronomind
from servicios.generador import GeneradorHorarios
from ui.aplicacion import Aplicacion


def construir_fachada():
    """Raíz de composición: aquí se crean y se inyectan todas las dependencias."""
    archivos = GestorArchivos.obtener(Path(__file__).resolve().parent / "Datos")
    repo = lambda nombre: RepositorioJSON(archivos, nombre)
    autenticacion = ServicioAutenticacion(repo("gestores_academicos.json"))
    catalogo = Catalogo(repo("carreras.json"), repo("docentes.json"), repo("salones.json"),
                        repo("paralelos.json"), repo("horarios_completos.json"))
    return FachadaChronomind(autenticacion, catalogo, GeneradorHorarios(catalogo))


if __name__ == "__main__":
    ventana = tk.Tk()
    Aplicacion(ventana, construir_fachada())
    ventana.mainloop()
