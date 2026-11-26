import tkinter as tk
from tkinter import messagebox, ttk

from ui.base import Pantalla, TablaObjetos, entero


class PantallaSalones(Pantalla):
    def construir(self):
        self.titulo("Salones y laboratorios", "Los laboratorios se usan en las materias que lo requieren.")
        columnas = [("Tipo", 90), ("Código", 80), ("Nombre", 200), ("Capacidad", 80),
                    ("Equipos", 330), ("Disponible", 80)]
        self.tabla = TablaObjetos(self.marco, columnas, alto=11)
        self.tabla.pack(fill="both", expand=True)
        form = ttk.LabelFrame(self.marco, text=" Nuevo espacio ", padding=10)
        form.pack(fill="x", pady=10)
        izq, der = ttk.Frame(form), ttk.Frame(form)
        izq.pack(side="left", padx=(0, 40))
        der.pack(side="left")
        ttk.Label(izq, text="Tipo").grid(row=0, column=0, sticky="w", pady=3)
        self.cmbTipo = ttk.Combobox(izq, state="readonly", values=["Aula", "Laboratorio"], width=14)
        self.cmbTipo.current(0)
        self.cmbTipo.grid(row=0, column=1, sticky="w")
        self.cmbTipo.bind("<<ComboboxSelected>>", lambda e: self.alternarCamposLab())
        self.entradaId = self.campo(izq, "Código", 1, 16)
        self.entradaNombre = self.campo(izq, "Nombre", 2, 26)
        self.entradaCapacidad = self.campo(izq, "Capacidad", 3, 8)
        self.entradaTipos = self.campo(der, "Tipos de equipos (separe con coma)", 0, 30)
        self.entradaCantidad = self.campo(der, "Cantidad de equipos", 1, 8)
        self.alternarCamposLab()
        botones = ttk.Frame(self.marco)
        botones.pack(fill="x")
        ttk.Button(botones, text="Volver al menú", command=self.volverAlMenu).pack(side="left")
        ttk.Button(botones, text="Eliminar", command=self.eliminar).pack(side="right")
        ttk.Button(botones, text="Activar / desactivar", command=self.alternar).pack(side="right", padx=8)
        ttk.Button(botones, text="Añadir", command=self.anadir).pack(side="right")
        self.recargar()

    def alternarCamposLab(self):
        estado = "normal" if self.cmbTipo.get() == "Laboratorio" else "disabled"
        self.entradaTipos.config(state=estado)
        self.entradaCantidad.config(state=estado)

    def recargar(self):
        def fila(s):
            detalle = "-"
            if s.tipo == "laboratorio":
                detalle = f"{s.cantidadEquipos}: {', '.join(s.tiposEquipos)}"
            return (s.tipo.capitalize(), s.idSalon, s.nombreSalon, s.capacidad, detalle,
                    "Sí" if s.disponible else "No")
        self.tabla.cargar(self.fachada.catalogo.salones, fila)

    def anadir(self):
        def accion():
            datos = {"tipo": self.cmbTipo.get().lower(), "idSalon": self.entradaId.get(),
                     "nombreSalon": self.entradaNombre.get(),
                     "capacidad": entero(self.entradaCapacidad.get(), "La capacidad")}
            if datos["tipo"] == "laboratorio":
                datos["tiposEquipos"] = [t for t in self.entradaTipos.get().split(",") if t.strip()]
                datos["cantidadEquipos"] = entero(self.entradaCantidad.get(), "La cantidad de equipos")
            self.fachada.agregarSalon(datos)
            for e in (self.entradaId, self.entradaNombre, self.entradaCapacidad):
                e.delete(0, "end")
            self.recargar()
        self.intentar(accion)

    def alternar(self):
        s = self.tabla.seleccionado()
        if s is None:
            messagebox.showinfo("Elija un salón", "Seleccione una fila de la tabla.")
            return
        self.fachada.alternarDisponibilidad(s)
        self.recargar()

    def eliminar(self):
        s = self.tabla.seleccionado()
        if s is None:
            messagebox.showinfo("Elija un salón", "Seleccione una fila de la tabla.")
            return
        self.intentar(lambda: (self.fachada.eliminarSalon(s), self.recargar()))
