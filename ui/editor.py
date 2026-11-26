from tkinter import messagebox, ttk

from dominio.franja_horaria import FranjaHoraria
from ui.base import FUENTE, GrillaHorario, Pantalla, TablaObjetos, entero


class PantallaEditor(Pantalla):
    def __init__(self, app, marco, fachada, horario):
        super().__init__(app, marco, fachada)
        self.editor = fachada.iniciarEdicion(horario)
        self.horario = horario

    def construir(self):
        h = self.horario
        self.titulo("Modificar horario manualmente",
                    f"{h.carrera.nombre} · Semestre {h.nivel} · Paralelo {h.paralelo.letraParalelo} · Período {h.periodo}")
        izq = ttk.Frame(self.marco)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 12))
        self.estado = ttk.Label(izq, font=FUENTE)
        self.estado.pack(anchor="w")
        self.grilla = GrillaHorario(izq, altoFila=34)
        self.grilla.pack(fill="both", expand=True)

        der = ttk.Frame(self.marco)
        der.pack(side="left", fill="y")
        ttk.Label(der, text="Clases del horario", font=FUENTE).pack(anchor="w")
        self.tablaClases = TablaObjetos(der, [("Materia", 150), ("Docente", 110), ("Día", 70), ("Hora", 60)], alto=7)
        self.tablaClases.pack(fill="x")
        ttk.Button(der, text="Quitar clase seleccionada", command=self.quitar).pack(anchor="e", pady=4)

        form = ttk.LabelFrame(der, text=" Añadir clase ", padding=8)
        form.pack(fill="x", pady=4)
        self.materias = {a.nombreAsignatura: a for a in
                         h.carrera.mostrarMallaCurricular().consultarAsignaturasNivel(h.nivel)}
        self.cmbMateria = self.__combo(form, "Materia", 0, list(self.materias), 36)
        self.cmbMateria.bind("<<ComboboxSelected>>", lambda e: self.alElegirMateria())
        self.cmbDocente = self.__combo(form, "Docente", 1, [], 36)
        self.cmbSalon = self.__combo(form, "Salón", 2, [], 36)
        self.cmbDia = self.__combo(form, "Día", 3, list(FranjaHoraria.DIAS_LABORABLES), 12)
        self.cmbDia.current(0)
        self.varInicio = self.spin(form, "Hora inicio", 4, 7, 19, 7, 5)
        self.varFin = self.spin(form, "Hora fin", 5, 8, 20, 9, 5)
        ttk.Button(form, text="Añadir clase", command=self.anadir).grid(row=6, column=1, sticky="e", pady=6)
        if self.materias:
            self.cmbMateria.current(0)
            self.alElegirMateria()

        ttk.Label(der, text="Horas semanales (registradas / requeridas)", font=FUENTE).pack(anchor="w", pady=(6, 0))
        self.tablaHoras = TablaObjetos(der, [("Materia", 230), ("Horas", 90)], alto=5)
        self.tablaHoras.pack(fill="x")

        botones = ttk.Frame(der)
        botones.pack(fill="x", pady=10)
        ttk.Button(botones, text="Volver", command=self.volver).pack(side="left")
        ttk.Button(botones, text="Guardar", command=self.guardar).pack(side="right")
        ttk.Button(botones, text="Descartar cambios", command=self.descartar).pack(side="right", padx=6)
        self.refrescar()

    def __combo(self, padre, texto, fila, valores, ancho):
        ttk.Label(padre, text=texto, font=FUENTE).grid(row=fila, column=0, sticky="w", pady=3, padx=(0, 8))
        combo = ttk.Combobox(padre, state="readonly", values=valores, width=ancho)
        combo.grid(row=fila, column=1, sticky="w", pady=3)
        return combo

    def alElegirMateria(self):
        asignatura = self.materias[self.cmbMateria.get()]
        self.docentes = {f"{d.nombreCompleto} ({d.idDocente})": d
                         for d in self.fachada.docentesDe(self.horario.carrera, asignatura)}
        self.salones = {f"{s.nombreSalon} [{s.tipo}, cap. {s.capacidad}]": s
                        for s in self.fachada.salonesPara(asignatura, self.horario.paralelo)}
        self.cmbDocente["values"] = list(self.docentes)
        self.cmbSalon["values"] = list(self.salones)
        self.cmbDocente.set(next(iter(self.docentes), ""))
        self.cmbSalon.set(next(iter(self.salones), ""))

    def refrescar(self):
        self.grilla.mostrar(self.horario)
        orden = {d: i for i, d in enumerate(FranjaHoraria.DIAS_LABORABLES)}
        clases = sorted(self.horario.materias, key=lambda m: (orden[m.franjaHoraria.diaSemana],
                                                              m.franjaHoraria.horaInicio))
        self.tablaClases.cargar(clases, lambda m: (m.asignatura.nombreAsignatura, m.docente.nombreCompleto,
                                                   m.franjaHoraria.diaSemana,
                                                   f"{m.franjaHoraria.horaInicio}-{m.franjaHoraria.horaFin}"))
        self.tablaHoras.cargar(self.horario.resumenHoras(), lambda t: (t[0].nombreAsignatura, f"{t[1]} / {t[2]}"))
        self.estado.config(text="● Cambios sin guardar" if self.editor.hayCambios else "Sin cambios pendientes",
                           foreground="#c0392b" if self.editor.hayCambios else "#1e8449")

    def anadir(self):
        def accion():
            if not self.cmbMateria.get() or not self.cmbDocente.get() or not self.cmbSalon.get():
                raise ValueError("Elija materia, docente y salón (la materia debe tener docente y salón aptos).")
            self.editor.agregarClase(self.materias[self.cmbMateria.get()], self.docentes[self.cmbDocente.get()],
                                     self.salones[self.cmbSalon.get()], self.cmbDia.get(),
                                     entero(self.varInicio.get(), "La hora de inicio"),
                                     entero(self.varFin.get(), "La hora de fin"))
            self.refrescar()
        self.intentar(accion)

    def quitar(self):
        clase = self.tablaClases.seleccionado()
        if clase is None:
            messagebox.showinfo("Elija una clase", "Seleccione la clase que desea quitar.")
            return
        self.intentar(lambda: (self.editor.quitarClase(clase), self.refrescar()))

    def guardar(self):
        self.editor.guardar()
        self.refrescar()
        messagebox.showinfo("Guardado", "El horario se guardó correctamente.")

    def descartar(self):
        if not self.editor.hayCambios:
            return
        if messagebox.askyesno("Descartar", "¿Descartar todos los cambios sin guardar?"):
            self.editor.descartar()
            self.refrescar()

    def volver(self):
        if self.editor.hayCambios:
            decision = messagebox.askyesnocancel("Cambios sin guardar", "¿Guardar los cambios antes de salir?")
            if decision is None:
                return
            if decision:
                self.editor.guardar()
            else:
                self.editor.descartar()
        self.app.mostrar("horarios")
