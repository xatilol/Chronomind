from tkinter import ttk

from ui.base import FUENTE, Pantalla


class PantallaLogin(Pantalla):
    def construir(self):
        ttk.Label(self.marco, text="Chronomind", font=("Segoe UI", 30, "bold")).pack(pady=(110, 4))
        ttk.Label(self.marco, text="Gestión de horarios · Facultad de Ciencias de la Vida y Tecnología",
                  font=FUENTE).pack()
        ttk.Label(self.marco, text="Inicio de sesión del gestor académico", font=FUENTE).pack(pady=(4, 20))
        caja = ttk.Frame(self.marco)
        caja.pack()
        self.entradaUsuario = self.campo(caja, "Usuario", 0, 32)
        self.entradaClave = self.campo(caja, "Contraseña", 1, 32)
        self.entradaClave.config(show="*")
        self.error = ttk.Label(self.marco, text="", foreground="#c0392b", font=FUENTE)
        self.error.pack(pady=(10, 0))
        ttk.Button(self.marco, text="Ingresar", command=self.ingresar).pack(pady=12)
        for entrada in (self.entradaUsuario, self.entradaClave):
            entrada.bind("<Return>", lambda evento: self.ingresar())
        self.entradaUsuario.focus()

    def ingresar(self):
        if self.fachada.iniciarSesion(self.entradaUsuario.get(), self.entradaClave.get()):
            self.app.mostrar("menu")
        else:
            self.error.config(text="Usuario o contraseña incorrectos.")
