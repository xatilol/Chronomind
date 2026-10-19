class Salon:
    def __init__(self, idSalon, nombreSalon, capacidad, disponible=True):
        if type(idSalon) != str or idSalon.strip() == "":
            raise ValueError("El código del salón debe ser un texto no vacío.")
        self.__idSalon = idSalon.strip()
        self.nombreSalon = nombreSalon
        self.capacidad = capacidad
        self.disponible = disponible

    @property
    def idSalon(self):
        return self.__idSalon

    @property
    def nombreSalon(self):
        return self.__nombreSalon

    @nombreSalon.setter
    def nombreSalon(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El nombre del salón no puede estar vacío.")
        self.__nombreSalon = valor.strip()

    @property
    def capacidad(self):
        return self.__capacidad

    @capacidad.setter
    def capacidad(self, valor):
        if type(valor) != int or valor <= 0:
            raise ValueError("La capacidad debe ser un entero positivo.")
        self.__capacidad = valor

    @property
    def disponible(self):
        return self.__disponible

    @disponible.setter
    def disponible(self, valor):
        if type(valor) != bool:
            raise ValueError("La disponibilidad debe ser True o False.")
        self.__disponible = valor

    #Método: validarCapacidad

    def validarCapacidad(self, cantidadEstudiantes):
        if type(cantidadEstudiantes) != int or cantidadEstudiantes <= 0:
            raise ValueError("La cantidad de estudiantes debe ser un entero positivo.")
        return cantidadEstudiantes <= self.__capacidad

    #Método: estaDisponible

    def estaDisponible(self):
        return self.__disponible
