from dominio.malla_curricular import MallaCurricular


class Carrera:
    def __init__(self, nombre):
        self.nombre = nombre
        self.__mallaCurricular = MallaCurricular()

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El nombre de la carrera no puede estar vacío.")
        self.__nombre = valor.strip()

    # Método: mostrarMallaCurricular
    def mostrarMallaCurricular(self):
        return self.__mallaCurricular

    def a_diccionario(self):
        return {"nombre": self.nombre, "niveles": self.__mallaCurricular.a_diccionario()}
