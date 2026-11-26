from dominio.franja_horaria import FranjaHoraria


class EditorHorario:
    """Caretaker del Memento: edita a mano un horario y permite guardar o descartar."""

    def __init__(self, horario, catalogo):
        self.__horario = horario
        self.__catalogo = catalogo
        self.__memento = horario.crearMemento()
        self.__cambios = False

    @property
    def horario(self):
        return self.__horario

    @property
    def hayCambios(self):
        return self.__cambios

    def agregarClase(self, asignatura, docente, salon, dia, horaInicio, horaFin):
        franja = FranjaHoraria(dia, horaInicio, horaFin)
        clase = self.__horario.agregarMateria(None, asignatura, docente, salon, franja,
                                              self.__catalogo.horarios)
        self.__cambios = True
        return clase

    def quitarClase(self, clase):
        self.__horario.quitarMateria(clase)
        self.__cambios = True

    def guardar(self):
        self.__catalogo.guardar("horarios")
        self.__memento = self.__horario.crearMemento()
        self.__cambios = False

    def descartar(self):
        self.__horario.restaurar(self.__memento)
        self.__cambios = False
