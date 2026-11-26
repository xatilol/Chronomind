from tkinter import messagebox, ttk

from ui.base import Pantalla, SelectorCarreraNivel, TablaObjetos, entero


class PantallaParalelos(Pantalla):
    def construir(self):
        self.titulo("Paralelos", "Cada paralelo de un semestre recibirá su propio horario.")
        self.selector = SelectorCarreraNivel(self.marco, self.fachada.carreras(), self.recargar)
        self.selector.pack(anchor="w", pady=(0, 8))
        self.tabla = TablaObjetos(self.marco, [("Paralelo", 120), ("Capacidad (estudiantes)", 200)], alto=10)
        self.tabla.pack(fill="both", expand=True)
        form = ttk.LabelFrame(self.marco, text=" Nuevo paralelo ", padding=10)
        form.pack(fill="x", pady=10)
        self.entradaLetra = self.campo(form, "Letra (A, B, C...)", 0, 8)
        self.entradaCapacidad = self.campo(form, "Capacidad", 1, 8)
        self.entradaCapacidad.insert(0, "35")
        botones = ttk.Frame(self.marco)
        botones.pack(fill="x")
        ttk.Button(botones, text="Volver al menú", command=self.volverAlMenu).pack(side="left")
        ttk.Button(botones, text="Eliminar seleccionado", command=self.eliminar).pack(side="right")
        ttk.Button(botones, text="Añadir paralelo", command=self.anadir).pack(side="right", padx=8)
        self.recargar()

    def recargar(self):
        paralelos = self.fachada.catalogo.paralelosDe(self.selector.carrera(), self.selector.nivel())
        self.tabla.cargar(paralelos, lambda p: (p.letraParalelo, p.capacidadEstudiante))

    def anadir(self):
        def accion():
            self.fachada.agregarParalelo(self.selector.carrera(), self.selector.nivel(),
                                         self.entradaLetra.get(), entero(self.entradaCapacidad.get(), "La capacidad"))
            self.entradaLetra.delete(0, "end")
            self.recargar()
        self.intentar(accion)

    def eliminar(self):
        p = self.tabla.seleccionado()
        if p is None:
            messagebox.showinfo("Elija un paralelo", "Seleccione el paralelo que desea eliminar.")
            return
        self.intentar(lambda: (self.fachada.eliminarParalelo(p), self.recargar()))
