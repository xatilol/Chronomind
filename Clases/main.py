import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from mallas_fcvt import MALLAS

CARPETA_DATOS = Path(__file__).resolve().parent.parent / "Datos"
ARCHIVO_GESTORES = "gestores_academicos.json"
ARCHIVO_IMPARTIENDO = "docentes_impartiendo.json"

GESTOR_EJEMPLO = {"correo": "ejemplo@live.uleam.edu.ec", "contrasena": "123."}

FUENTE_TITULO = ("Arial", 18, "bold")
FUENTE_TEXTO = ("Arial", 11)


def leer_json(nombre):
    ruta = CARPETA_DATOS / nombre
    if not ruta.exists():
        return []
    texto = ruta.read_text(encoding="utf-8").strip()
    if texto == "":
        return []
    return json.loads(texto)


def guardar_json(nombre, datos):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / nombre
    with ruta.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=4)
        archivo.write("\n")


def preparar_datos():
    if len(leer_json(ARCHIVO_GESTORES)) == 0:
        guardar_json(ARCHIVO_GESTORES, [GESTOR_EJEMPLO])
    if not (CARPETA_DATOS / ARCHIVO_IMPARTIENDO).exists():
        guardar_json(ARCHIVO_IMPARTIENDO, [])


class Aplicacion:
    def __init__(self, ventana):
        self.ventana = ventana
        ventana.title("Chronomind")
        ventana.geometry("720x540")
        ventana.minsize(620, 460)
        self.cont = None
        self.gestor = None
        self.docente = {}
        self.carrera = None
        self.semestre = None 
        self.pantalla_login()

    def _limpiar(self):
        if self.cont is not None:
            self.cont.destroy()
        self.cont = ttk.Frame(self.ventana, padding=30)
        self.cont.pack(fill="both", expand=True)

    def _campo(self, texto):
        ttk.Label(self.cont, text=texto, font=FUENTE_TEXTO).pack(anchor="w", pady=(10, 2))
        entrada = ttk.Entry(self.cont, font=FUENTE_TEXTO)
        entrada.pack(fill="x")
        return entrada

    def _botones(self, texto_siguiente, siguiente, atras):
        marco = ttk.Frame(self.cont)
        marco.pack(fill="x", pady=(15, 0))
        ttk.Button(marco, text="Atrás", command=atras).pack(side="left")
        ttk.Button(marco, text=texto_siguiente, command=siguiente).pack(side="right")

    def _pantalla_lista(self, titulo, subtitulo, opciones, texto_boton, al_elegir, al_volver):
        self._limpiar()
        ttk.Label(self.cont, text=titulo, font=FUENTE_TITULO).pack(pady=(0, 4))
        ttk.Label(self.cont, text=subtitulo, font=FUENTE_TEXTO).pack(pady=(0, 10))

        marco = ttk.Frame(self.cont)
        marco.pack(fill="both", expand=True)
        barra = ttk.Scrollbar(marco)
        barra.pack(side="right", fill="y")
        lista = tk.Listbox(marco, font=FUENTE_TEXTO, activestyle="none",
                           exportselection=False, yscrollcommand=barra.set)
        lista.pack(side="left", fill="both", expand=True)
        barra.config(command=lista.yview)
        for opcion in opciones:
            lista.insert("end", opcion)

        def elegir(evento=None):
            seleccion = lista.curselection()
            if not seleccion:
                messagebox.showwarning("Falta elegir", "Seleccione una opción de la lista.")
                return
            al_elegir(seleccion[0])

        lista.bind("<Double-Button-1>", elegir)
        self._botones(texto_boton, elegir, al_volver)


    def pantalla_login(self):
        self._limpiar()
        ttk.Label(self.cont, text="Chronomind", font=("Segoe UI", 26, "bold")).pack(pady=(30, 4))
        ttk.Label(self.cont, text="Inicio de sesión del gestor académico",
                  font=FUENTE_TEXTO).pack(pady=(0, 20))

        self.entrada_correo = self._campo("Correo")
        self.entrada_clave = self._campo("Contraseña")
        self.entrada_clave.config(show="*")
        self.etiqueta_error = ttk.Label(self.cont, text="", foreground="#c0392b", font=FUENTE_TEXTO)
        self.etiqueta_error.pack(pady=(10, 0))
        ttk.Button(self.cont, text="Ingresar", command=self.iniciar_sesion).pack(pady=15)

        self.entrada_correo.focus()
        self.ventana.bind("<Return>", lambda evento: self.iniciar_sesion())

    def iniciar_sesion(self):
        correo = self.entrada_correo.get().strip().lower()
        clave = self.entrada_clave.get()
        for gestor in leer_json(ARCHIVO_GESTORES):
            if gestor["correo"].lower() == correo and gestor["contrasena"] == clave:
                self.gestor = gestor
                self.ventana.unbind("<Return>")
                self.pantalla_menu()
                return
        self.etiqueta_error.config(text="Correo o contraseña incorrectos.")

    def pantalla_menu(self):
        self._limpiar()
        ttk.Label(self.cont, text="Menú principal", font=FUENTE_TITULO).pack(pady=(10, 4))
        ttk.Label(self.cont, text=f"Sesión: {self.gestor['correo']}",
                  font=FUENTE_TEXTO).pack(pady=(0, 25))

        ttk.Button(self.cont, text="Agregar docente",
                   command=self.pantalla_datos_docente).pack(fill="x", ipady=10, pady=6)
        for texto in ("Gestionar salones", "Gestionar paralelos", "Generar horarios"):
            ttk.Button(self.cont, text=texto, state="disabled").pack(fill="x", ipady=10, pady=6)


    def pantalla_datos_docente(self):
        self._limpiar()
        ttk.Label(self.cont, text="Agregar docente", font=FUENTE_TITULO).pack(pady=(0, 4))
        ttk.Label(self.cont, text="Paso 1: datos del docente", font=FUENTE_TEXTO).pack()

        self.entrada_id = self._campo("Código / cédula del docente")
        self.entrada_nombre = self._campo("Nombre completo")
        self.entrada_id.insert(0, self.docente.get("idDocente", ""))
        self.entrada_nombre.insert(0, self.docente.get("nombreDocente", ""))
        self._botones("Siguiente", self.validar_datos_docente, self.pantalla_menu)
        self.entrada_id.focus()

    def validar_datos_docente(self):
        idDocente = self.entrada_id.get().strip()
        nombre = self.entrada_nombre.get().strip()
        if idDocente == "" or nombre == "":
            messagebox.showwarning("Datos incompletos", "Escriba el código y el nombre del docente.")
            return
        self.docente = {"idDocente": idDocente, "nombreDocente": nombre}
        self.pantalla_carrera()

    def pantalla_carrera(self):
        carreras = list(MALLAS.keys())

        def elegir(indice):
            self.carrera = carreras[indice]
            self.pantalla_semestres()

        self._pantalla_lista("Agregar docente", "Paso 2: seleccione la carrera",
                             carreras, "Siguiente", elegir, self.pantalla_datos_docente)

    def pantalla_semestres(self):
        cantidad = len(MALLAS[self.carrera])
        opciones = [f"Semestre {n}" for n in range(1, cantidad + 1)]

        def elegir(indice):
            self.semestre = indice + 1
            self.pantalla_asignaturas()

        self._pantalla_lista(self.carrera, "Paso 3: seleccione el semestre",
                             opciones, "Siguiente", elegir, self.pantalla_carrera)

    def pantalla_asignaturas(self):
        asignaturas = MALLAS[self.carrera][self.semestre - 1]

        def elegir(indice):
            self.guardar_docente(asignaturas[indice])

        self._pantalla_lista(f"{self.carrera} - Semestre {self.semestre}",
                             f"Paso 4: asignatura que impartirá {self.docente['nombreDocente']}",
                             asignaturas, "Guardar", elegir, self.pantalla_semestres)

    def guardar_docente(self, asignatura):
        registros = leer_json(ARCHIVO_IMPARTIENDO)
        for registro in registros:
            if registro["idDocente"].lower() == self.docente["idDocente"].lower():
                if (registro["carrera"] == self.carrera
                        and registro["asignatura"] == asignatura):
                    messagebox.showwarning("Ya registrado",
                                           "Ese docente ya imparte esa asignatura en esa carrera.")
                    return
        registros.append({
            "idDocente": self.docente["idDocente"],
            "nombreDocente": self.docente["nombreDocente"],
            "carrera": self.carrera,
            "asignatura": asignatura
        })
        guardar_json(ARCHIVO_IMPARTIENDO, registros)
        messagebox.showinfo("Guardado",
                            f"{self.docente['nombreDocente']} impartirá {asignatura}.")
        self.docente = {}
        self.pantalla_menu()


if __name__ == "__main__":
    preparar_datos()
    ventana = tk.Tk()
    Aplicacion(ventana)
    ventana.mainloop()
