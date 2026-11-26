import hashlib
import hmac


class GestorAcademico:
    """Usuario que administra el sistema (único rol que usa la aplicación)."""

    def __init__(self, usuario, nombre, claveHash):
        if type(usuario) != str or usuario.strip() == "":
            raise ValueError("El usuario no puede estar vacío.")
        self.__usuario = usuario.strip().lower()
        self.__nombre = nombre
        self.__claveHash = claveHash

    @property
    def usuario(self):
        return self.__usuario

    @property
    def nombre(self):
        return self.__nombre

    @staticmethod
    def calcularHash(clave):
        return hashlib.sha256(clave.encode("utf-8")).hexdigest()

    def verificarClave(self, clave):
        return hmac.compare_digest(self.__claveHash, self.calcularHash(clave))

    def a_diccionario(self):
        return {"usuario": self.__usuario, "nombre": self.__nombre, "claveHash": self.__claveHash}
