from horario_completo import HorarioCompleto


class Paralelo:
    def __init__(self, letraParalelo, capacidadEstudiante):
        if type(letraParalelo) != str or letraParalelo.strip() == "":
            raise ValueError("La letra o identificador del paralelo no puede estar vacío.")
        self.__letraParalelo = letraParalelo.strip().upper()
        self.capacidadEstudiante = capacidadEstudiante

    @property
    def letraParalelo(self):
        return self.__letraParalelo

    @property
    def capacidadEstudiante(self):
        return self.__capacidadEstudiante

    @capacidadEstudiante.setter
    def capacidadEstudiante(self, valor):
        if type(valor) != int or valor <= 0:
            raise ValueError("La capacidad del paralelo debe ser un entero positivo.")
        self.__capacidadEstudiante = valor

    #Método:validarLimiteEstudiantes

    def validarLimiteEstudiantes(self, cantidadEstudiantes):
        if type(cantidadEstudiantes) != int or cantidadEstudiantes < 0:
            raise ValueError("La cantidad de estudiantes debe ser un entero no negativo.")
        return cantidadEstudiantes <= self.__capacidadEstudiante

    #Método:validarLimiteEstudiantes

    def asignarParHorario(self, idHorario, periodo, nivel, carrera):
        if type(idHorario) != str or idHorario.strip() == "":
            raise ValueError("El código del horario no puede estar vacío.")
        if type(periodo) != str or periodo.strip() == "":
            raise ValueError("Indique el período académico.")
        if type(nivel) != int or nivel <= 0:
            raise ValueError("El nivel debe ser un entero positivo.")
        if nivel not in carrera.mostrarMallaCurricular().niveles:
            raise ValueError("Ese nivel todavía no está registrado en la malla de la carrera.")

        return HorarioCompleto(
            idHorario.strip(), periodo.strip(), nivel, carrera, self
        )
