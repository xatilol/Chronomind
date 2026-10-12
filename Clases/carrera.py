from malla_curricular import MallaCurricular


class Carrera:
    def __init__(self, nombre):
        self.nombre = nombre
        self.__mallaCurricular = MallaCurricular()

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if valor.strip() == "":
            raise ValueError("El nombre no puede estar vacío.")
        self.__nombre = valor.strip()

    #Método: mostrarMallaCurricular

    def mostrarMallaCurricular(self):
        return self.__mallaCurricular

    def anadirDiccionario(self):
        return {
            "nombre": self.nombre,
            "mallaCurricular": self.__mallaCurricular.anadirDiccionario()
        }

    @classmethod
    def desdeDiccionario(cls, datos):
        carrera = cls(datos["nombre"])
        # Compatible con las carreras antiguas que solo guardaban el nombre.
        if "mallaCurricular" in datos:
            carrera.__mallaCurricular = MallaCurricular.desdeDiccionario(
                datos["mallaCurricular"]
            )
        return carrera
