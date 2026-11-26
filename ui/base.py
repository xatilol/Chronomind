import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import messagebox, ttk

from dominio.franja_horaria import FranjaHoraria

FUENTE = ("Segoe UI", 10)
FUENTE_TITULO = ("Segoe UI", 18, "bold")


def entero(texto, nombre):
    try:
        return int(str(texto).strip())
    except ValueError:
        raise ValueError(f"{nombre} debe ser un número entero.")


class Pantalla(ABC):
    """Clase abstracta de toda pantalla: recibe la fachada (inyección) y construye su contenido."""

    def __init__(self, app, marco, fachada):
        self.app = app
        self.marco = marco
        self.fachada = fachada

    @abstractmethod
    def construir(self):
        pass

    def titulo(self, texto, subtitulo=""):
        ttk.Label(self.marco, text=texto, font=FUENTE_TITULO).pack(anchor="w")
        if subtitulo:
            ttk.Label(self.marco, text=subtitulo, font=FUENTE).pack(anchor="w", pady=(0, 8))

    def campo(self, padre, texto, fila, ancho=26):
        ttk.Label(padre, text=texto, font=FUENTE).grid(row=fila, column=0, sticky="w", pady=3, padx=(0, 8))
        entrada = ttk.Entry(padre, width=ancho, font=FUENTE)
        entrada.grid(row=fila, column=1, sticky="w", pady=3)
        return entrada

    def spin(self, padre, texto, fila, desde, hasta, valor, ancho=8):
        ttk.Label(padre, text=texto, font=FUENTE).grid(row=fila, column=0, sticky="w", pady=3, padx=(0, 8))
        variable = tk.StringVar(value=str(valor))
        ttk.Spinbox(padre, from_=desde, to=hasta, width=ancho, textvariable=variable).grid(
            row=fila, column=1, sticky="w", pady=3)
        return variable

    def intentar(self, accion):
        """Ejecuta una acción mostrando el error de validación (si lo hay) en un aviso."""
        try:
            accion()
            return True
        except ValueError as error:
            messagebox.showwarning("Revise los datos", str(error))
            return False

    def volverAlMenu(self):
        self.app.mostrar("menu")


class TablaObjetos(ttk.Frame):
    """Tabla (Treeview) que asocia cada fila con su objeto de dominio."""

    def __init__(self, padre, columnas, alto=10):
        super().__init__(padre)
        self.__arbol = ttk.Treeview(self, columns=[c for c, _ in columnas], show="headings",
                                    height=alto, selectmode="browse")
        for nombre, ancho in columnas:
            self.__arbol.heading(nombre, text=nombre)
            self.__arbol.column(nombre, width=ancho, anchor="w")
        barra = ttk.Scrollbar(self, orient="vertical", command=self.__arbol.yview)
        self.__arbol.configure(yscrollcommand=barra.set)
        self.__arbol.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self.__objetos = {}

    def cargar(self, objetos, fila):
        self.__arbol.delete(*self.__arbol.get_children())
        self.__objetos = {}
        for i, objeto in enumerate(objetos):
            self.__arbol.insert("", "end", iid=str(i), values=fila(objeto))
            self.__objetos[str(i)] = objeto

    def seleccionado(self):
        seleccion = self.__arbol.selection()
        return self.__objetos.get(seleccion[0]) if seleccion else None

    def alSeleccionar(self, callback):
        self.__arbol.bind("<<TreeviewSelect>>", lambda evento: callback())


class SelectorCarreraNivel(ttk.Frame):
    """Par de listas desplegables: carrera y nivel (semestre)."""

    def __init__(self, padre, carreras, alCambiar):
        super().__init__(padre)
        self.__carreras = {c.nombre: c for c in carreras}
        self.__alCambiar = alCambiar
        ttk.Label(self, text="Carrera", font=FUENTE).grid(row=0, column=0, padx=(0, 6))
        self.__cmbCarrera = ttk.Combobox(self, state="readonly", width=34, values=list(self.__carreras))
        self.__cmbCarrera.grid(row=0, column=1, padx=(0, 16))
        ttk.Label(self, text="Semestre", font=FUENTE).grid(row=0, column=2, padx=(0, 6))
        self.__cmbNivel = ttk.Combobox(self, state="readonly", width=6)
        self.__cmbNivel.grid(row=0, column=3)
        self.__cmbCarrera.bind("<<ComboboxSelected>>", lambda e: self.__cambioCarrera())
        self.__cmbNivel.bind("<<ComboboxSelected>>", lambda e: self.__alCambiar())
        self.__cmbCarrera.current(0)
        self.__cambioCarrera(False)  # al crearlo no avisa: la pantalla carga sus datos después

    def __cambioCarrera(self, avisar=True):
        niveles = self.carrera().mostrarMallaCurricular().niveles
        self.__cmbNivel["values"] = niveles
        self.__cmbNivel.current(0)
        if avisar:
            self.__alCambiar()

    def carrera(self):
        return self.__carreras[self.__cmbCarrera.get()]

    def nivel(self):
        return int(self.__cmbNivel.get())


class GrillaHorario(tk.Frame):
    """Dibuja un horario semanal (lunes a viernes, 7:00 a 20:00)."""

    COLORES = ["#cfe8ff", "#d8f5d0", "#ffe9c2", "#f6d2ec", "#e1d8ff", "#d0f3f0", "#ffd9d2", "#eeeec0"]

    def __init__(self, padre, altoFila=36):
        super().__init__(padre, bg="#888888")
        self.__alto = altoFila

    def mostrar(self, horario):
        for widget in self.winfo_children():
            widget.destroy()
        dias = FranjaHoraria.DIAS_LABORABLES
        horas = range(FranjaHoraria.HORA_MIN, FranjaHoraria.HORA_MAX)
        tk.Label(self, text="Hora", font=("Segoe UI", 9, "bold"), bg="#e8e8e8").grid(
            row=0, column=0, sticky="nsew", padx=1, pady=1)
        for c, dia in enumerate(dias, 1):
            tk.Label(self, text=dia, font=("Segoe UI", 9, "bold"), bg="#e8e8e8").grid(
                row=0, column=c, sticky="nsew", padx=1, pady=1)
        for r, hora in enumerate(horas, 1):
            tk.Label(self, text=f"{hora}:00", font=("Segoe UI", 8), bg="#f4f4f4").grid(
                row=r, column=0, sticky="nsew", padx=1, pady=1)
        ocupadas = set()
        if horario is not None:
            for materia in horario.materias:
                franja = materia.franjaHoraria
                col = dias.index(franja.diaSemana) + 1
                fila = franja.horaInicio - FranjaHoraria.HORA_MIN + 1
                color = self.COLORES[sum(map(ord, materia.asignatura.idAsignatura)) % len(self.COLORES)]
                texto = (f"{materia.asignatura.nombreAsignatura}\n{materia.docente.nombreCompleto}\n"
                         f"{materia.salon.nombreSalon}")
                tk.Label(self, text=texto, bg=color, font=("Segoe UI", 7), wraplength=125,
                         justify="center").grid(row=fila, column=col, rowspan=franja.duracion,
                                                sticky="nsew", padx=1, pady=1)
                for k in range(franja.duracion):
                    ocupadas.add((fila + k, col))
        for r in range(1, len(horas) + 1):
            for c in range(1, len(dias) + 1):
                if (r, c) not in ocupadas:
                    tk.Label(self, bg="white").grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
        for c in range(1, len(dias) + 1):
            self.columnconfigure(c, weight=1, minsize=128)
        for r in range(1, len(horas) + 1):
            self.rowconfigure(r, minsize=self.__alto)
