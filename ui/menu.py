from tkinter import ttk

from ui.base import FUENTE, Pantalla


class PantallaMenu(Pantalla):
    OPCIONES = [
        ("Crear horario automático", "generar"),
        ("Ver y modificar horarios creados", "horarios"),
        ("Materias (horas, cupos, semestre)", "materias"),
        ("Docentes", "docentes"),
        ("Salones y laboratorios", "salones"),
        ("Paralelos", "paralelos"),
    ]

    def construir(self):
        self.titulo("Menú principal", f"Sesión: {self.fachada.gestor.nombre} ({self.fachada.gestor.usuario})")
        caja = ttk.Frame(self.marco)
        caja.pack(pady=30)
        for i, (texto, destino) in enumerate(self.OPCIONES):
            ttk.Button(caja, text=texto, width=40,
                       command=lambda d=destino: self.app.mostrar(d)).grid(
                row=i // 2, column=i % 2, padx=10, pady=10, ipady=14)
        ttk.Button(self.marco, text="Cerrar sesión", command=self.cerrarSesion).pack(pady=10)
        avisos = self.fachada.avisosDeCarga()
        if avisos:
            ttk.Label(self.marco, foreground="#b9770e", font=FUENTE, justify="left",
                      text="Al cargar los datos se omitió:\n" + "\n".join(avisos[:5])).pack(pady=10)

    def cerrarSesion(self):
        self.fachada.cerrarSesion()
        self.app.mostrar("login")
