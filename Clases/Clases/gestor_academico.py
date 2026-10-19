import hashlib
import hmac
import os


class GestorAcademico:
    # Atributos de clase: son iguales para todos los gestores.
    DOMINIO = "@live.uleam.edu.ec"
    ITERACIONES = 200000

    def __init__(self, correo, nombreGestor):
        self.__correo = self.validarCorreo(correo)
        self.nombreGestor = nombreGestor
        self.__sal = ""
        self.__hashContrasena = ""

    @staticmethod
    def validarCorreo(correo):
        if type(correo) != str:
            raise ValueError("El correo debe ser un texto.")
        correo = correo.strip().lower()
        if " " in correo or correo.count("@") != 1:
            raise ValueError("El correo no tiene un formato válido.")
        if not correo.endswith(GestorAcademico.DOMINIO):
            raise ValueError(f"El correo debe terminar en {GestorAcademico.DOMINIO}")
        if correo == GestorAcademico.DOMINIO:
            raise ValueError("Falta el nombre de usuario antes del @.")
        return correo

    @property
    def correo(self):
        # Solo lectura: es el identificador con el que inicia sesión.
        return self.__correo

    @property
    def nombreGestor(self):
        return self.__nombreGestor

    @nombreGestor.setter
    def nombreGestor(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El nombre del gestor no puede estar vacío.")
        self.__nombreGestor = valor.strip()

    #Método: establecerContrasena

    def establecerContrasena(self, contrasena):
        if type(contrasena) != str or len(contrasena) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        # Nunca se guarda la contraseña en texto: solo su huella (hash) y una sal.
        self.__sal = os.urandom(16).hex()
        self.__hashContrasena = self.__calcularHash(contrasena, self.__sal)

    #Método: verificarContrasena

    def verificarContrasena(self, contrasena):
        if type(contrasena) != str or self.__hashContrasena == "":
            return False
        intento = self.__calcularHash(contrasena, self.__sal)
        return hmac.compare_digest(intento, self.__hashContrasena)

    @staticmethod
    def __calcularHash(contrasena, sal):
        resultado = hashlib.pbkdf2_hmac(
            "sha256", contrasena.encode("utf-8"),
            bytes.fromhex(sal), GestorAcademico.ITERACIONES
        )
        return resultado.hex()

    def anadirDiccionario(self):
        return {
            "correo": self.correo,
            "nombreGestor": self.nombreGestor,
            "sal": self.__sal,
            "hashContrasena": self.__hashContrasena
        }

    @classmethod
    def desdeDiccionario(cls, datos):
        gestor = cls(datos["correo"], datos["nombreGestor"])
        gestor.__sal = datos["sal"]
        gestor.__hashContrasena = datos["hashContrasena"]
        return gestor
