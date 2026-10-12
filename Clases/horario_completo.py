from franja_horaria import FranjaHoraria
from materias_horario import MateriasHorario


class HorarioCompleto:
    def __init__(self, idHorario, periodo, nivel, carrera, paralelo):
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

    #Método: verificarCrucesHorario

    def verificarCrucesHorario(self, materia, otrosHorarios=None):
        for existente in self.__materias:
            if materia.validarChoqueMaterias(existente):
                return True
        if otrosHorarios is not None:
            for horario in otrosHorarios:
                if horario is not self:
                    for existente in horario.materias:
                        if materia.validarChoqueMaterias(existente):
                            return True
        return False

    #Método: agregarMateria

    def agregarMateria(self, idClase, asignatura, docente, salon,
                       franjaHoraria, otrosHorarios=None):
        # Composición: el horario crea la asignación que va a contener.
        nueva = MateriasHorario(
            idClase, asignatura, docente, salon, self.paralelo,
            franjaHoraria, self.carrera, self.nivel, self.periodo
        )
        nueva.validarAsignacion()
        for materia in self.__materias:
            if materia.idClase.lower() == nueva.idClase.lower():
                raise ValueError("Ese código de clase ya existe.")
        if otrosHorarios is not None:
            for horario in otrosHorarios:
                for materia in horario.materias:
                    if materia.idClase.lower() == nueva.idClase.lower():
                        raise ValueError("Ese código de clase ya existe en otro horario.")
        if self.verificarCrucesHorario(nueva, otrosHorarios):
            raise ValueError("La clase choca con un docente, salón o paralelo ya asignado.")

        horas = franjaHoraria.horaFin - franjaHoraria.horaInicio
        for materia in self.__materias:
            if materia.asignatura.idAsignatura == asignatura.idAsignatura:
                horas += materia.franjaHoraria.horaFin - materia.franjaHoraria.horaInicio
        if horas > asignatura.horasSemanales:
            raise ValueError("Se superarían las horas semanales de esta asignatura.")
        self.__materias.append(nueva)
        return nueva

    #Método: quitarMateria

    def quitarMateria(self, idClase):
        if type(idClase) != str or idClase.strip() == "":
            raise ValueError("Indique el código de la clase que desea quitar.")
        for materia in self.__materias:
            if materia.idClase.lower() == idClase.strip().lower():
                self.__materias.remove(materia)
                return
        raise ValueError("No existe una clase con ese código en este horario.")

    #Método: verHorarioCompleto

    def verHorarioCompleto(self):
        texto = f"Horario {self.idHorario}\n"
        texto += f"{self.carrera.nombre} | Nivel {self.nivel} | "
        texto += f"Paralelo {self.paralelo.letraParalelo} | Período {self.periodo}\n"
        if not self.__materias:
            texto += "Todavía no hay clases asignadas.\n"

        # Recorremos los días y horas en orden, sin ordenar con funciones avanzadas.
        for dia in FranjaHoraria.DIAS_LABORABLES:
            for hora in range(7, 20):
                for materia in self.__materias:
                    franja = materia.franjaHoraria
                    if franja.diaSemana == dia and franja.horaInicio == hora:
                        texto += f"{dia} {franja.horaInicio}:00-{franja.horaFin}:00 | "
                        texto += f"{materia.idClase}: {materia.asignatura.nombreAsignatura} | "
                        texto += f"{materia.docente.nombreDocente} | {materia.salon.nombreSalon}\n"

        texto += "Horas semanales registradas / requeridas:\n"
        asignaturas = self.carrera.mostrarMallaCurricular().consultarAsignaturasNivel(self.nivel)
        for asignatura in asignaturas:
            horas = 0
            for materia in self.__materias:
                if materia.asignatura.idAsignatura == asignatura.idAsignatura:
                    horas += materia.franjaHoraria.horaFin - materia.franjaHoraria.horaInicio
            texto += f"{asignatura.nombreAsignatura}: {horas}/{asignatura.horasSemanales}\n"
        return texto

    def anadirDiccionario(self):
        materias = []
        for materia in self.__materias:
            materias.append(materia.anadirDiccionario())
        return {
            "idHorario": self.idHorario,
            "periodo": self.periodo,
            "nivel": self.nivel,
            "carrera": self.carrera.nombre,
            "paralelo": self.paralelo.letraParalelo,
            "materias": materias
        }
