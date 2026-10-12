"""Menú inicial de Chronomind v1. Ejecutar este archivo."""

import json
from pathlib import Path

from carrera import Carrera
from docente import Docente
from salon import Salon
from laboratorio import Laboratorio
from franja_horaria import FranjaHoraria
from paralelo import Paralelo
from materias_horario import MateriasHorario

# La ruta funciona aunque el programa se ejecute desde otra carpeta.
CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"

CLASES = [
    "Carrera", "Malla Curricular", "Asignatura", "Docente", "Salón",
    "Laboratorio", "Paralelo", "Franja Horaria", "Materias Horario",
    "Horario Completo", "Gestor Académico"
]
