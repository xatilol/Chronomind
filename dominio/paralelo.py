from patrones.builder import HorarioBuilder


class Paralelo:
    def __init__(self, letraParalelo, capacidadEstudiante, carrera, nivel):
        if type(letraParalelo) != str or letraParalelo.strip() == "":
            raise ValueError("La letra o identificador del paralelo no puede estar vacío.")
        if type(nivel) != int or nivel <= 0:
            raise ValueError("El nivel debe ser un entero positivo.")
        self.__letraParalelo = letraParalelo.strip().upper()
        self.__carrera = carrera
        self.__nivel = nivel
        self.capacidadEstudiante = capacidadEstudiante

    @property
    def letraParalelo(self):
        return self.__letraParalelo

    @property
    def carrera(self):
        return self.__carrera

    @property
    def nivel(self):
        return self.__nivel

    @property
    def capacidadEstudiante(self):
        return self.__capacidadEstudiante

    @capacidadEstudiante.setter
    def capacidadEstudiante(self, valor):
        if type(valor) != int or valor <= 0:
            raise ValueError("La capacidad del paralelo debe ser un entero positivo.")
        self.__capacidadEstudiante = valor

    # Método: validarLimiteEstudiantes
    def validarLimiteEstudiantes(self, cantidadEstudiantes):
        if type(cantidadEstudiantes) != int or cantidadEstudiantes < 0:
            raise ValueError("La cantidad de estudiantes debe ser un entero no negativo.")
        return cantidadEstudiantes <= self.__capacidadEstudiante

    # Método: asignarParHorario
    def asignarParHorario(self, idHorario, periodo):
        return (HorarioBuilder().conId(idHorario).conPeriodo(periodo).conCarrera(self.carrera)
                .conNivel(self.nivel).conParalelo(self).construir())

    def a_diccionario(self):
        return {"carrera": self.carrera.nombre, "nivel": self.nivel,
                "letraParalelo": self.letraParalelo, "capacidadEstudiante": self.capacidadEstudiante}
