from asignatura import Asignatura


class MallaCurricular:
    def __init__(self):
        self.__niveles = {}

    @property
    def niveles(self):
        # Devolvemos una lista nueva con los números de nivel.
        return sorted(self.__niveles.keys())

     #Método: agregarAsignaturasNivel

    def agregarAsignaturasNivel(self, nivel, idAsignatura, nombreAsignatura, horasSemanales, necesitaLaboratorio):
        if nivel <= 0:
            raise ValueError("El nivel debe ser mayor que cero.")
        nueva = Asignatura(idAsignatura, nombreAsignatura, horasSemanales, necesitaLaboratorio)

        for asignaturas in self.__niveles.values():
            for asignatura in asignaturas:
                if asignatura.idAsignatura.lower() == nueva.idAsignatura.lower():
                    raise ValueError("Ese código ya está registrado en esta malla.")

        if nivel not in self.__niveles:
            self.__niveles[nivel] = []
        self.__niveles[nivel].append(nueva)

    #Método: consultarAsignaturasNivel

    def consultarAsignaturasNivel(self, nivel):
        resultado = []
        if nivel in self.__niveles:
            for asignatura in self.__niveles[nivel]:
                resultado.append(asignatura)
        return resultado
