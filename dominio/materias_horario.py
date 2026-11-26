class MateriasHorario:
    """Una clase programada: asignatura + docente + salón + paralelo + franja."""

    def __init__(self, idClase, asignatura, docente, salon, paralelo, franjaHoraria,
                 carrera, nivel, periodo):
        self.__idClase = idClase
        self.__asignatura = asignatura
        self.__docente = docente
        self.__salon = salon
        self.__paralelo = paralelo
        self.__franjaHoraria = franjaHoraria
        self.__carrera = carrera
        self.__nivel = nivel
        self.__periodo = periodo

    @property
    def idClase(self):
        return self.__idClase

    @property
    def asignatura(self):
        return self.__asignatura

    @property
    def docente(self):
        return self.__docente

    @property
    def salon(self):
        return self.__salon

    @property
    def paralelo(self):
        return self.__paralelo

    @property
    def franjaHoraria(self):
        return self.__franjaHoraria

    @property
    def carrera(self):
        return self.__carrera

    @property
    def nivel(self):
        return self.__nivel

    @property
    def periodo(self):
        return self.__periodo

    @property
    def duracion(self):
        return self.__franjaHoraria.duracion

    @property
    def grupo(self):
        return (self.carrera.nombre, self.nivel, self.paralelo.letraParalelo)

    # Método: capacidadAula
    def capacidadAula(self):
        cupos = min(self.asignatura.cupos, self.paralelo.capacidadEstudiante)
        return self.salon.validarCapacidad(cupos)

    # Método: validarChoqueMaterias
    def validarChoqueMaterias(self, otraMateria):
        """Hay choque si se cruzan en el tiempo y comparten docente, salón o paralelo."""
        if self.periodo != otraMateria.periodo:
            return False
        if not self.franjaHoraria.cruzaConOtroHorario(otraMateria.franjaHoraria):
            return False
        return (self.docente is otraMateria.docente
                or self.salon is otraMateria.salon
                or self.grupo == otraMateria.grupo)

    def validarAsignacion(self):
        if not self.docente.imparte(self.carrera, self.asignatura):
            raise ValueError(f"{self.docente.nombreCompleto} no está vinculado a {self.asignatura.nombreAsignatura}.")
        if not self.docente.comprobarDisponibilidad(self.franjaHoraria):
            raise ValueError(f"{self.docente.nombreCompleto} no está disponible en ese horario.")
        if not self.salon.estaDisponible():
            raise ValueError(f"El salón {self.salon.nombreSalon} no está disponible.")
        if not self.asignatura.es_salon_apto(self.salon):
            raise ValueError(f"El salón {self.salon.nombreSalon} no cumple el requisito de espacio: "
                             f"{self.asignatura.requisito_espacio.obtener_descripcion()}.")
        if not self.capacidadAula():
            raise ValueError(f"El salón {self.salon.nombreSalon} no tiene capacidad suficiente.")

    def a_diccionario(self):
        return {"idClase": self.idClase, "idAsignatura": self.asignatura.idAsignatura,
                "idDocente": self.docente.idDocente, "idSalon": self.salon.idSalon,
                "franjaHoraria": self.franjaHoraria.a_diccionario()}
