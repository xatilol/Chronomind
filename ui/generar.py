import tkinter as tk
from tkinter import messagebox, ttk

from ui.base import FUENTE, Pantalla, SelectorCarreraNivel


class PantallaGenerar(Pantalla):
    def construir(self):
        self.titulo("Crear horario automático", "Se genera un horario por cada paralelo del semestre, "
                                                "sin choques de docente, salón ni paralelo.")
        self.selector = SelectorCarreraNivel(self.marco, self.fachada.carreras(), self.mostrarResumen)
        self.selector.pack(anchor="w", pady=(0, 8))
        opciones = ttk.Frame(self.marco)
        opciones.pack(anchor="w", pady=4)
        ttk.Label(opciones, text="Período académico", font=FUENTE).grid(row=0, column=0, padx=(0, 6))
        self.entradaPeriodo = ttk.Entry(opciones, width=10, font=FUENTE)
        self.entradaPeriodo.insert(0, "2026-2")
        self.entradaPeriodo.grid(row=0, column=1, padx=(0, 20))
        ttk.Label(opciones, text="Distribución", font=FUENTE).grid(row=0, column=2, padx=(0, 6))
        self.cmbEstrategia = ttk.Combobox(opciones, state="readonly", width=44,
                                          values=self.fachada.nombresEstrategias())
        self.cmbEstrategia.current(0)
        self.cmbEstrategia.grid(row=0, column=3)
        self.etiquetaResumen = ttk.Label(self.marco, font=FUENTE, justify="left")
        self.etiquetaResumen.pack(anchor="w", pady=6)
        self.salida = tk.Text(self.marco, height=18, font=("Consolas", 10), state="disabled", wrap="word")
        self.salida.pack(fill="both", expand=True, pady=6)
        botones = ttk.Frame(self.marco)
        botones.pack(fill="x")
        ttk.Button(botones, text="Volver al menú", command=self.volverAlMenu).pack(side="left")
        ttk.Button(botones, text="Ver horarios creados", command=lambda: self.app.mostrar("horarios")).pack(
            side="right")
        ttk.Button(botones, text="Generar horario", command=self.generar).pack(side="right", padx=8)
        self.mostrarResumen()

    def mostrarResumen(self):
        paralelos = self.fachada.catalogo.paralelosDe(self.selector.carrera(), self.selector.nivel())
        if paralelos:
            texto = "Paralelos de este semestre: " + ", ".join(
                f"{p.letraParalelo} ({p.capacidadEstudiante})" for p in paralelos)
        else:
            texto = "Este semestre todavía no tiene paralelos (créelos en «Paralelos»)."
        self.etiquetaResumen.config(text=texto)

    def escribir(self, texto):
        self.salida.config(state="normal")
        self.salida.delete("1.0", "end")
        self.salida.insert("end", texto)
        self.salida.config(state="disabled")

    def generar(self):
        carrera, nivel = self.selector.carrera(), self.selector.nivel()
        periodo = self.entradaPeriodo.get()
        if self.fachada.horariosExistentes(carrera, nivel, periodo):
            if not messagebox.askyesno("Ya existen horarios",
                                       "Ya hay horarios de este semestre y período. ¿Reemplazarlos?"):
                return

        def accion():
            resultado = self.fachada.generarHorarios(carrera, nivel, periodo, self.cmbEstrategia.get())
            texto = f"Se generaron {len(resultado.horarios)} horario(s).\n\n"
            for h in resultado.horarios:
                texto += f"• Paralelo {h.paralelo.letraParalelo}: {len(h.materias)} clases, faltan {h.horasFaltantes()} h.\n"
            if resultado.advertencias:
                texto += "\nAdvertencias:\n" + "\n".join(f"  - {a}" for a in resultado.advertencias)
            else:
                texto += "\nTodas las materias quedaron completas y sin choques."
            self.escribir(texto)
        self.intentar(accion)
