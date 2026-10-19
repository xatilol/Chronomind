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
