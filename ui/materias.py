import tkinter as tk
from tkinter import messagebox, ttk

from dominio.asignatura import Asignatura
from ui.base import FUENTE, Pantalla, SelectorCarreraNivel, TablaObjetos, entero


class PantallaMaterias(Pantalla):
    def construir(self):
        self.titulo("Materias", "Elija carrera y semestre. Las horas por semestre se reparten en "
                                f"{Asignatura.SEMANAS_SEMESTRE} semanas.")
        self.selector = SelectorCarreraNivel(self.marco, self.fachada.carreras(), self.recargar)
        self.selector.pack(anchor="w", pady=(0, 8))
        columnas = [("Código", 90), ("Materia", 380), ("H. semestre", 90), ("H. semana", 80),
                    ("Cupos", 60), ("Espacio", 230)]
        self.tabla = TablaObjetos(self.marco, columnas, alto=12)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.alSeleccionar(self.cargarFormulario)

        form = ttk.LabelFrame(self.marco, text=" Datos de la materia ", padding=10)
        form.pack(fill="x", pady=10)
        izq, der = ttk.Frame(form), ttk.Frame(form)
        izq.pack(side="left", padx=(0, 40))
        der.pack(side="left")
        self.entradaNombre = self.campo(izq, "Nombre", 0, 44)
        self.varHoras = self.spin(izq, "Horas por semestre", 1, 16, 400, 64)
        self.varCupos = self.spin(izq, "Cupos por materia", 2, 1, 300, 35)
        self.etiquetaSemana = ttk.Label(izq, font=FUENTE)
        self.etiquetaSemana.grid(row=1, column=2, padx=8)
        self.varHoras.trace_add("write", lambda *a: self.actualizarSemana())
        self.varLab = tk.BooleanVar(value=False)
        ttk.Checkbutton(der, text="Requiere laboratorio", variable=self.varLab).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=3)
        self.varEquipos = self.spin(der, "Equipos mínimos", 1, 1, 200, 1)
        self.entradaTipoEquipo = self.campo(der, "Tipo de equipo (opcional)", 2, 22)
        self.actualizarSemana()

        botones = ttk.Frame(self.marco)
        botones.pack(fill="x")
        ttk.Button(botones, text="Volver al menú", command=self.volverAlMenu).pack(side="left")
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="right")
        ttk.Button(botones, text="Guardar cambios de la fila elegida", command=self.guardarCambios).pack(
            side="right", padx=8)
        ttk.Button(botones, text="Añadir materia nueva", command=self.anadir).pack(side="right")
        self.recargar()

    def actualizarSemana(self):
        try:
            horas = int(self.varHoras.get())
            self.etiquetaSemana.config(text=f"= {-(-horas // Asignatura.SEMANAS_SEMESTRE)} h/semana")
        except ValueError:
            self.etiquetaSemana.config(text="")

    def recargar(self):
        malla = self.selector.carrera().mostrarMallaCurricular()
        self.tabla.cargar(malla.consultarAsignaturasNivel(self.selector.nivel()),
                          lambda a: (a.idAsignatura, a.nombreAsignatura, a.horasSemestre, a.horasSemanales,
                                     a.cupos, a.requisito_espacio.obtener_descripcion()))

    def cargarFormulario(self):
        a = self.tabla.seleccionado()
        if a is None:
            return
        self.entradaNombre.delete(0, "end")
        self.entradaNombre.insert(0, a.nombreAsignatura)
        self.varHoras.set(str(a.horasSemestre))
        self.varCupos.set(str(a.cupos))
        self.varLab.set(a.usaLaboratorio())
        requisito = a.requisito_espacio
        self.varEquipos.set(str(getattr(requisito, "equipos_minimos", 1)))
        self.entradaTipoEquipo.delete(0, "end")
        self.entradaTipoEquipo.insert(0, getattr(requisito, "tipo_equipo", ""))

    def __guardar(self, asignatura):
        self.fachada.guardarMateria(
            self.selector.carrera(), self.selector.nivel(), self.entradaNombre.get(),
            entero(self.varHoras.get(), "Las horas por semestre"), entero(self.varCupos.get(), "Los cupos"),
            self.varLab.get(), entero(self.varEquipos.get(), "Los equipos mínimos"),
            self.entradaTipoEquipo.get(), asignatura)
        self.recargar()

    def anadir(self):
        self.intentar(lambda: self.__guardar(None))

    def guardarCambios(self):
        a = self.tabla.seleccionado()
        if a is None:
            messagebox.showinfo("Elija una materia", "Seleccione la materia de la tabla que desea modificar.")
            return
        self.intentar(lambda: self.__guardar(a))

    def eliminar(self):
        a = self.tabla.seleccionado()
        if a is None:
            messagebox.showinfo("Elija una materia", "Seleccione la materia que desea eliminar.")
            return
        if messagebox.askyesno("Eliminar", f"¿Eliminar «{a.nombreAsignatura}» de la malla?"):
            self.intentar(lambda: (self.fachada.eliminarMateria(self.selector.carrera(), a), self.recargar()))
