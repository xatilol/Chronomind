from salon import Salon


class Laboratorio(Salon):
    def __init__(self, idSalon, nombreSalon, capacidad, tiposEquipos, cantidadEquipos, disponible=True):
        # Inicializa y valida los atributos heredados de Salon.
        super().__init__(idSalon, nombreSalon, capacidad, disponible)
        self.tiposEquipos = tiposEquipos
        self.cantidadEquipos = cantidadEquipos

    @property
    def tiposEquipos(self):
        return self.__tiposEquipos.copy()

    @tiposEquipos.setter
    def tiposEquipos(self, valores):
        if type(valores) != list or len(valores) == 0:
            raise ValueError("Ingrese una lista con al menos un tipo de equipo.")
        tipos = []
        for valor in valores:
            if type(valor) != str or valor.strip() == "":
                raise ValueError("Los tipos de equipos deben ser textos no vacíos.")
            nombre = valor.strip()
            for tipo in tipos:
                if tipo.lower() == nombre.lower():
                    raise ValueError("No repita un tipo de equipo en la lista.")
            tipos.append(nombre)
        self.__tiposEquipos = tipos

    @property
    def cantidadEquipos(self):
        return self.__cantidadEquipos

    @cantidadEquipos.setter
    def cantidadEquipos(self, valor):
        if type(valor) != int or valor < 0:
            raise ValueError("La cantidad de equipos debe ser un entero igual o mayor que cero.")
        self.__cantidadEquipos = valor

    #Método: ComprobarCuentaEquipos

    def ComprobarCuentaEquipos(self, cantidadRequerida):
        if type(cantidadRequerida) != int or cantidadRequerida <= 0:
            raise ValueError("La cantidad requerida debe ser un entero positivo.")
        return cantidadRequerida <= self.__cantidadEquipos


