from dominio.gestor_academico import GestorAcademico

class ServicioAutenticacion:
    USUARIO_INICIAL = "gestor@uleam"
    CLAVE_INICIAL = "12345"

    def __init__(self, repositorio):
        self.__repositorio = repositorio
        self.__gestores = []
        self.__cargar()

    def __cargar(self):
        for d in self.__repositorio.cargar():
            if isinstance(d, dict) and {"usuario", "nombre", "claveHash"} <= d.keys():
                self.__gestores.append(GestorAcademico(d["usuario"], d["nombre"], d["claveHash"]))
        if not self.__gestores:
            inicial = GestorAcademico(self.USUARIO_INICIAL, "Gestor Académico", GestorAcademico.calcularHash(self.CLAVE_INICIAL))
            self.__gestores.append(inicial)
            self.__repositorio.guardar([g.a_diccionario() for g in self.__gestores])

    def autenticar(self, usuario, clave):
        usuario = (usuario or "").strip().lower()
        for gestor in self.__gestores:
            if gestor.usuario == usuario and gestor.verificarClave(clave or ""):
                return gestor
        return None
