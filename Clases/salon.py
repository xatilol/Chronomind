from abc import ABC, abstractmethod

class IReservable(ABC):
    @abstractmethod
    def estaDisponible(self):
        pass

    @abstractmethod
    def validarCapacidad(self, cantidadEstudiantes):
        pass

class Salon(IReservable, ABC):
    def __init__(self, idSalon, nombreSalon, capacidad, disponible=True):
        pass

    @abstractmethod
    def obtenerDescripcion(self):
        pass

class Laboratorio(Salon):
    def __init__(self, idSalon, nombreSalon, capacidad, tiposEquipos, cantidadEquipos, disponible=True):
        pass

    def estaDisponible(self):
        pass

    def validarCapacidad(self, cantidadEstudiantes):
        pass

    def obtenerDescripcion(self):
        pass

class INotificador(ABC):
    @abstractmethod
    def notificar(self, mensaje):
        pass

class NotificadorConsola(INotificador):
    def notificar(self, mensaje):
        pass

class ServicioReserva:
    def __init__(self, notificador: INotificador):
        self.__notificador = notificador  

    def reservar(self, salon: Salon, cantidadEstudiantes):
        pass