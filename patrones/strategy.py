from abc import ABC, abstractmethod

from dominio.franja_horaria import FranjaHoraria


class EstrategiaDistribucion(ABC):
    """Strategy: cómo se reparten las horas semanales de una asignatura."""

    nombre = ""
    MAX_BLOQUE = 2

    def dividir(self, horas):
        """Divide las horas semanales en bloques lo más parejos posible."""
        cantidad = -(-horas // self.MAX_BLOQUE)
        base, extra = divmod(horas, cantidad)
        return [base + 1 if i < extra else base for i in range(cantidad)]

    @abstractmethod
    def ordenDias(self, indiceBloque, dias):
        pass

    def ordenHoras(self, duracion):
        return range(FranjaHoraria.HORA_MIN, FranjaHoraria.HORA_MAX - duracion + 1)


class DistribucionEquilibrada(EstrategiaDistribucion):
    """Bloques de 2 horas repartidos en distintos días de la semana."""
    nombre = "Equilibrada (bloques de 2 h en varios días)"
    MAX_BLOQUE = 2

    def ordenDias(self, indiceBloque, dias):
        dias = list(dias)
        inicio = (indiceBloque * 2) % len(dias)
        return dias[inicio:] + dias[:inicio]


class DistribucionCompacta(EstrategiaDistribucion):
    """Pocos bloques largos (hasta 4 h), empezando por el lunes."""
    nombre = "Compacta (bloques largos, menos días)"
    MAX_BLOQUE = 4

    def ordenDias(self, indiceBloque, dias):
        return list(dias)


ESTRATEGIAS = [DistribucionEquilibrada, DistribucionCompacta]
