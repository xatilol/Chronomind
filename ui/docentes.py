import tkinter as tk
from tkinter import messagebox, ttk

from dominio.franja_horaria import FranjaHoraria
from ui.base import FUENTE, Pantalla, SelectorCarreraNivel, TablaObjetos, entero


class PantallaDocentes(Pantalla):
    def construir(self):
        self.titulo("Docentes", "Registre al docente, su disponibilidad y las materias (carrera y semestre) que imparte. "
                                "Si la cédula ya existe, se actualizan sus datos.")
        self.vinculos = []
        izq = ttk.Frame(self.marco)
        izq.pack(side="left", fill="both", expand=True, padx=(0, 14))
        self.tabla = TablaObjetos(izq, [("Cédula", 90), ("Nombre", 190), ("Título", 120), ("Materias", 60)], alto=22)
        self.tabla.pack(fill="both", expand=True)
        self.tabla.alSeleccionar(self.cargarFormulario)
        ttk.Button(izq, text="Eliminar docente", command=self.eliminar).pack(anchor="e", pady=6)
        ttk.Button(izq, text="Volver al menú", command=self.volverAlMenu).pack(anchor="w")

        der = ttk.Frame(self.marco)
        der.pack(side="left", fill="y")
        datos = ttk.LabelFrame(der, text=" Datos ", padding=8)
        datos.pack(fill="x")
        self.entradaCedula = self.campo(datos, "Cédula (10 dígitos)", 0, 20)
        self.entradaNombre = self.campo(datos, "Nombres", 1, 28)
        self.entradaApellido = self.campo(datos, "Apellidos", 2, 28)
        self.entradaTitulo = self.campo(datos, "Título", 3, 28)

        disp = ttk.LabelFrame(der, text=" Disponibilidad (hora inicio - hora fin) ", padding=8)
        disp.pack(fill="x", pady=8)
        self.dispo = {}
        for i, dia in enumerate(FranjaHoraria.DIAS_LABORABLES):
            activo, ini, fin = tk.BooleanVar(value=True), tk.StringVar(value="7"), tk.StringVar(value="20")
            ttk.Checkbutton(disp, text=dia, variable=activo, width=11).grid(row=i, column=0, sticky="w")
            ttk.Spinbox(disp, from_=7, to=19, width=4, textvariable=ini).grid(row=i, column=1)
            ttk.Label(disp, text=" a ").grid(row=i, column=2)
            ttk.Spinbox(disp, from_=8, to=20, width=4, textvariable=fin).grid(row=i, column=3)
            self.dispo[dia] = (activo, ini, fin)

        mat = ttk.LabelFrame(der, text=" Materias que imparte ", padding=8)
        mat.pack(fill="x")
        self.selector = SelectorCarreraNivel(mat, self.fachada.carreras(), self.recargarAsignaturas)
        self.selector.pack(anchor="w")
        cuerpo = ttk.Frame(mat)
        cuerpo.pack(fill="x", pady=6)
        self.listaAsignaturas = tk.Listbox(cuerpo, selectmode="extended", height=6, width=34,
                                           exportselection=False, font=FUENTE)
        self.listaAsignaturas.pack(side="left")
        ttk.Button(cuerpo, text="Añadir ›", command=self.vincular).pack(side="left", padx=6)
        self.listaVinculos = tk.Listbox(cuerpo, selectmode="extended", height=6, width=40,
                                        exportselection=False, font=FUENTE)
        self.listaVinculos.pack(side="left")
        ttk.Button(mat, text="Quitar seleccionadas", command=self.desvincular).pack(anchor="e")

        botones = ttk.Frame(der)
        botones.pack(fill="x", pady=8)
        ttk.Button(botones, text="Limpiar formulario", command=self.limpiar).pack(side="left")
        ttk.Button(botones, text="Guardar docente", command=self.guardar).pack(side="right")
        self.recargarAsignaturas()
        self.recargar()

    def recargar(self):
        self.tabla.cargar(self.fachada.catalogo.docentes,
                          lambda d: (d.idDocente, d.nombreCompleto, d.tituloGraduado, len(d.asignaturasImparte)))

    def recargarAsignaturas(self):
        self.asignaturasMostradas = self.selector.carrera().mostrarMallaCurricular().consultarAsignaturasNivel(
            self.selector.nivel())
        self.listaAsignaturas.delete(0, "end")
        for a in self.asignaturasMostradas:
            self.listaAsignaturas.insert("end", a.nombreAsignatura)

    def refrescarVinculos(self):
        self.listaVinculos.delete(0, "end")
        for carrera, a in self.vinculos:
            nivel = carrera.mostrarMallaCurricular().nivelDe(a)
            self.listaVinculos.insert("end", f"{carrera.nombre} · S{nivel} · {a.nombreAsignatura}")

    def vincular(self):
        for i in self.listaAsignaturas.curselection():
            par = (self.selector.carrera(), self.asignaturasMostradas[i])
            if par not in self.vinculos:
                self.vinculos.append(par)
        self.refrescarVinculos()

    def desvincular(self):
        for i in sorted(self.listaVinculos.curselection(), reverse=True):
            del self.vinculos[i]
        self.refrescarVinculos()

    def limpiar(self):
        for e in (self.entradaCedula, self.entradaNombre, self.entradaApellido, self.entradaTitulo):
            e.delete(0, "end")
        for activo, ini, fin in self.dispo.values():
            activo.set(True)
            ini.set("7")
            fin.set("20")
        self.vinculos = []
        self.refrescarVinculos()

    def cargarFormulario(self):
        d = self.tabla.seleccionado()
        if d is None:
            return
        self.limpiar()
        for entrada, valor in ((self.entradaCedula, d.idDocente), (self.entradaNombre, d.nombreDocente),
                               (self.entradaApellido, d.apellidoDocente), (self.entradaTitulo, d.tituloGraduado)):
            entrada.insert(0, valor)
        for activo, _, _ in self.dispo.values():
            activo.set(False)
        for bloque in d.disponibilidad:
            activo, ini, fin = self.dispo[bloque["dia"]]
            activo.set(True)
            ini.set(str(bloque["horaInicio"]))
            fin.set(str(bloque["horaFin"]))
        self.vinculos = [(r["carrera"], r["asignatura"]) for r in d.asignaturasImparte]
        self.refrescarVinculos()

    def guardar(self):
        def accion():
            bloques = [{"dia": dia, "horaInicio": entero(ini.get(), "La hora de inicio"),
                        "horaFin": entero(fin.get(), "La hora de fin")}
                       for dia, (activo, ini, fin) in self.dispo.items() if activo.get()]
            self.fachada.guardarDocente(self.entradaCedula.get(), self.entradaNombre.get(),
                                        self.entradaApellido.get(), self.entradaTitulo.get(),
                                        bloques, list(self.vinculos))
            self.limpiar()
            self.recargar()
        self.intentar(accion)

    def eliminar(self):
        d = self.tabla.seleccionado()
        if d is None:
            messagebox.showinfo("Elija un docente", "Seleccione un docente de la tabla.")
            return
        if messagebox.askyesno("Eliminar", f"¿Eliminar a {d.nombreCompleto}?"):
            self.intentar(lambda: (self.fachada.eliminarDocente(d), self.recargar()))
