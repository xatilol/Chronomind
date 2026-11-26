from abc import ABC, abstractmethod


class Observador(ABC):
    """Interfaz del patrón Observer."""

    @abstractmethod
    def actualizar(self, evento, datos):
        pass


class Sujeto:
    """Sujeto observable: notifica a sus observadores cuando algo cambia."""

    def __init__(self):
        self.__observadores = []

    def suscribir(self, observador):
        if not isinstance(observador, Observador):
            raise ValueError("Solo se pueden suscribir objetos Observador.")
        if observador not in self.__observadores:
            self.__observadores.append(observador)

    def desuscribir(self, observador):
        if observador in self.__observadores:
            self.__observadores.remove(observador)

    def notificar(self, evento, datos=None):
        for observador in list(self.__observadores):
            observador.actualizar(evento, datos)
