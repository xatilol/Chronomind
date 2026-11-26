class HorarioMemento:
    """Memento: instantánea inmutable de las clases de un horario."""

    def __init__(self, materias):
        self.__materias = tuple(materias)

    @property
    def materias(self):
        return list(self.__materias)
