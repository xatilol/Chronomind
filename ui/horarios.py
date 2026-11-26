from tkinter import messagebox, ttk

from ui.base import FUENTE, GrillaHorario, Pantalla, TablaObjetos


class PantallaHorarios(Pantalla):
    def construir(self):
        self.titulo("Horarios creados")
        izq = ttk.Frame(self.marco)
        izq.pack(side="left", fill="y", padx=(0, 14))
        columnas = [("Carrera", 130), ("Sem.", 40), ("Par.", 40), ("Período", 70), ("Faltan h", 60)]
        self.tabla = TablaObjetos(izq, columnas, alto=20)
        self.tabla.pack(fill="y", expand=True)
        self.tabla.alSeleccionar(self.mostrar)
        for texto, comando in (("Modificar manualmente", self.modificar), ("Eliminar horario", self.eliminar),
                               ("Verificar conflictos", self.conflictos), ("Registro de cambios", self.actividad),
                               ("Volver al menú", self.volverAlMenu)):
            ttk.Button(izq, text=texto, command=comando).pack(fill="x", pady=2)
        derecha = ttk.Frame(self.marco)
        derecha.pack(side="left", fill="both", expand=True)
        self.etiqueta = ttk.Label(derecha, text="Seleccione un horario de la lista.", font=FUENTE)
        self.etiqueta.pack(anchor="w", pady=(0, 6))
        self.grilla = GrillaHorario(derecha)
        self.grilla.pack(fill="both", expand=True)
        self.grilla.mostrar(None)
        self.recargar()

    def recargar(self):
        self.tabla.cargar(self.fachada.horarios(),
                          lambda h: (h.carrera.nombre, h.nivel, h.paralelo.letraParalelo, h.periodo,
                                     h.horasFaltantes()))

    def mostrar(self):
        h = self.tabla.seleccionado()
        if h is None:
            return
        self.etiqueta.config(text=f"{h.carrera.nombre} · Semestre {h.nivel} · Paralelo "
                                  f"{h.paralelo.letraParalelo} · Período {h.periodo}")
        self.grilla.mostrar(h)

    def elegido(self):
        h = self.tabla.seleccionado()
        if h is None:
            messagebox.showinfo("Elija un horario", "Seleccione un horario de la lista.")
        return h

    def modificar(self):
        h = self.elegido()
        if h is not None:
            self.app.mostrar("editor", horario=h)

    def eliminar(self):
        h = self.elegido()
        if h is not None and messagebox.askyesno("Eliminar", f"¿Eliminar el horario {h.idHorario}?"):
            self.fachada.eliminarHorario(h)
            self.grilla.mostrar(None)
            self.recargar()

    def conflictos(self):
        choques = self.fachada.verificarConflictos()
        if choques:
            messagebox.showwarning("Conflictos", "Se encontraron choques:\n" + "\n".join(choques[:15]))
        else:
            messagebox.showinfo("Conflictos", "No hay choques de docente, salón ni paralelo.")

    def actividad(self):
        entradas = self.fachada.registroActividad()
        messagebox.showinfo("Registro de cambios (esta sesión)",
                            "\n".join(entradas[-15:]) if entradas else "Todavía no hay cambios en esta sesión.")
