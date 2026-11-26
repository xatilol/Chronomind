from dominio.asignatura import Asignatura


class MallaCurricular:
    def __init__(self):
        self.__niveles = {}

    @property
    def niveles(self):
        return sorted(self.__niveles.keys())

    # Método: agregarAsignaturasNivel
    def agregarAsignaturasNivel(self, nivel, asignatura):
        if type(nivel) != int or nivel <= 0:
            raise ValueError("El nivel debe ser un entero mayor que cero.")
        if not isinstance(asignatura, Asignatura):
            raise ValueError("Debe indicar una asignatura válida.")
        if self.buscarAsignatura(asignatura.idAsignatura) is not None:
            raise ValueError("Ese código ya está registrado en esta malla.")
        self.__niveles.setdefault(nivel, []).append(asignatura)

    # Método: consultarAsignaturasNivel
    def consultarAsignaturasNivel(self, nivel):
        return list(self.__niveles.get(nivel, []))

    def buscarAsignatura(self, idAsignatura):
        for lista in self.__niveles.values():
            for asignatura in lista:
                if asignatura.idAsignatura.lower() == idAsignatura.lower():
                    return asignatura
        return None

    def nivelDe(self, asignatura):
        for nivel, lista in self.__niveles.items():
            if asignatura in lista:
                return nivel
        return None

    def quitarAsignatura(self, idAsignatura):
        for lista in self.__niveles.values():
            for asignatura in lista:
                if asignatura.idAsignatura == idAsignatura:
                    lista.remove(asignatura)
                    return
        raise ValueError("La asignatura no existe en la malla.")

    def todasLasAsignaturas(self):
        return [a for nivel in self.niveles for a in self.__niveles[nivel]]

    def a_diccionario(self):
        return {str(n): [a.a_diccionario() for a in self.__niveles[n]] for n in self.niveles}
