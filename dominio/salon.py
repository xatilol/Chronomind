from abc import ABC, abstractmethod


class IReservable(ABC):
    """Interfaz: todo espacio que se pueda reservar para una clase."""

    @abstractmethod
    def estaDisponible(self):
        pass

    @abstractmethod
    def validarCapacidad(self, cantidadEstudiantes):
        pass


class Salon(IReservable, ABC):
    """Clase abstracta base de los espacios físicos (aulas y laboratorios)."""

    def __init__(self, idSalon, nombreSalon, capacidad, disponible=True):
        if type(idSalon) != str or idSalon.strip() == "":
            raise ValueError("El código del salón no puede estar vacío.")
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
        self.__disponible = bool(valor)

    def estaDisponible(self):
        return self.__disponible

    def validarCapacidad(self, cantidadEstudiantes):
        if type(cantidadEstudiantes) != int or cantidadEstudiantes < 0:
            raise ValueError("La cantidad de estudiantes debe ser un entero no negativo.")
        return cantidadEstudiantes <= self.__capacidad

    def cumpleEquipos(self, cantidad, tipoEquipo=None):
        """Por defecto un salón no ofrece equipos; los laboratorios lo sobrescriben."""
        return False

    @property
    @abstractmethod
    def tipo(self):
        pass

    @abstractmethod
    def obtenerDescripcion(self):
        pass

    def a_diccionario(self):
        return {"tipo": self.tipo, "idSalon": self.idSalon, "nombreSalon": self.nombreSalon,
                "capacidad": self.capacidad, "disponible": self.disponible}


class Aula(Salon):
    @property
    def tipo(self):
        return "aula"

    def obtenerDescripcion(self):
        return f"Aula {self.nombreSalon} (capacidad {self.capacidad})"
