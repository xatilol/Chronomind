from functools import singledispatchmethod

from dominio.franja_horaria import FranjaHoraria
from dominio.materias_horario import MateriasHorario
from patrones.memento import HorarioMemento
from patrones.observer import Sujeto


class HorarioCompleto(Sujeto):
    """Horario semanal de un paralelo (carrera + nivel + período). Es observable."""

    def __init__(self, idHorario, periodo, nivel, carrera, paralelo):
        super().__init__()
        if type(idHorario) != str or idHorario.strip() == "":
            raise ValueError("El código del horario no puede estar vacío.")
        if type(periodo) != str or periodo.strip() == "":
            raise ValueError("El período no puede estar vacío.")
        if type(nivel) != int or nivel <= 0:
            raise ValueError("El nivel debe ser un entero positivo.")
        if nivel not in carrera.mostrarMallaCurricular().niveles:
            raise ValueError("El nivel no está registrado en la malla de esta carrera.")
        if paralelo is None:
            raise ValueError("El horario debe tener un paralelo.")
        self.__idHorario = idHorario.strip()
        self.__periodo = periodo.strip()
        self.__nivel = nivel
        self.__carrera = carrera
        self.__paralelo = paralelo
        self.__materias = []
        self.__contador = 0

    @property
    def idHorario(self):
        return self.__idHorario

    @property
    def periodo(self):
        return self.__periodo

    @property
    def nivel(self):
        return self.__nivel

    @property
    def carrera(self):
        return self.__carrera

    @property
    def paralelo(self):
        return self.__paralelo

    @property
    def materias(self):
        return self.__materias.copy()

    # Método: verificarCrucesHorario
    def verificarCrucesHorario(self, materia, otrosHorarios=None):
        for existente in self.__materias:
            if materia.validarChoqueMaterias(existente):
                return True
        for horario in (otrosHorarios or []):
            if horario is not self:
                for existente in horario.materias:
                    if materia.validarChoqueMaterias(existente):
                        return True
        return False

    def horasRegistradas(self, asignatura):
        return sum(m.duracion for m in self.__materias
                   if m.asignatura.idAsignatura == asignatura.idAsignatura)

    def resumenHoras(self):
        """Lista de (asignatura, horas registradas, horas requeridas)."""
        asignaturas = self.carrera.mostrarMallaCurricular().consultarAsignaturasNivel(self.nivel)
        return [(a, self.horasRegistradas(a), a.horasSemanales) for a in asignaturas]

    def horasFaltantes(self):
        return sum(max(0, req - reg) for _, reg, req in self.resumenHoras())

    # Método: agregarMateria
    def agregarMateria(self, idClase, asignatura, docente, salon, franjaHoraria, otrosHorarios=None):
        malla = self.carrera.mostrarMallaCurricular()
        if asignatura not in malla.consultarAsignaturasNivel(self.nivel):
            raise ValueError("La asignatura no pertenece a este nivel de la carrera.")
        if idClase is None:
            self.__contador += 1
            idClase = f"{self.idHorario}-C{self.__contador:02d}"
            while any(m.idClase == idClase for m in self.__materias):
                self.__contador += 1
                idClase = f"{self.idHorario}-C{self.__contador:02d}"
        nueva = MateriasHorario(idClase, asignatura, docente, salon, self.paralelo, franjaHoraria,
                                self.carrera, self.nivel, self.periodo)
        nueva.validarAsignacion()
        for horario in [self] + [h for h in (otrosHorarios or []) if h is not self]:
            if any(m.idClase.lower() == nueva.idClase.lower() for m in horario.materias):
                raise ValueError("Ese código de clase ya existe.")
        if self.verificarCrucesHorario(nueva, otrosHorarios):
            raise ValueError("La clase choca con un docente, salón o paralelo ya asignado.")
        if self.horasRegistradas(asignatura) + franjaHoraria.duracion > asignatura.horasSemanales:
            raise ValueError("Se superarían las horas semanales de esta asignatura.")
        self.__materias.append(nueva)
        self.notificar("clase_agregada", nueva)
        return nueva

    # Método: quitarMateria (sobrecargado: por código de clase o por objeto)
    @singledispatchmethod
    def quitarMateria(self, objetivo):
        raise TypeError("Indique el código de la clase o la clase a quitar.")

    @quitarMateria.register(str)
    def _(self, idClase):
        for materia in self.__materias:
            if materia.idClase.lower() == idClase.strip().lower():
                return self.quitarMateria(materia)
        raise ValueError("No existe una clase con ese código en este horario.")

    @quitarMateria.register(MateriasHorario)
    def _(self, materia):
        if materia not in self.__materias:
            raise ValueError("Esa clase no pertenece a este horario.")
        self.__materias.remove(materia)
        self.notificar("clase_quitada", materia)

    def vaciar(self):
        for materia in self.materias:
            self.quitarMateria(materia)

    # Memento
    def crearMemento(self):
        return HorarioMemento(self.__materias)

    def restaurar(self, memento):
        """Vuelve al estado guardado, notificando cada diferencia."""
        guardadas = memento.materias
        for materia in self.materias:
            if materia not in guardadas:
                self.quitarMateria(materia)
        for materia in guardadas:
            if materia not in self.__materias:
                self.__materias.append(materia)
                self.notificar("clase_agregada", materia)

    # Método: verHorarioCompleto
    def verHorarioCompleto(self):
        texto = f"Horario {self.idHorario}\n"
        texto += (f"{self.carrera.nombre} | Nivel {self.nivel} | "
                  f"Paralelo {self.paralelo.letraParalelo} | Período {self.periodo}\n")
        if not self.__materias:
            texto += "Todavía no hay clases asignadas.\n"
        for dia in FranjaHoraria.DIAS_LABORABLES:
            for materia in sorted((m for m in self.__materias if m.franjaHoraria.diaSemana == dia),
                                  key=lambda m: m.franjaHoraria.horaInicio):
                f = materia.franjaHoraria
                texto += (f"{dia} {f.horaInicio}:00-{f.horaFin}:00 | {materia.asignatura.nombreAsignatura} | "
                          f"{materia.docente.nombreCompleto} | {materia.salon.nombreSalon}\n")
        texto += "Horas semanales registradas / requeridas:\n"
        for asignatura, reg, req in self.resumenHoras():
            texto += f"{asignatura.nombreAsignatura}: {reg}/{req}\n"
        return texto

    def a_diccionario(self):
        return {"idHorario": self.idHorario, "periodo": self.periodo, "nivel": self.nivel,
                "carrera": self.carrera.nombre, "paralelo": self.paralelo.letraParalelo,
                "materias": [m.a_diccionario() for m in self.__materias]}
