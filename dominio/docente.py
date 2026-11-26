from functools import singledispatchmethod

from dominio.franja_horaria import FranjaHoraria


class Docente:
    DIAS_LABORABLES = FranjaHoraria.DIAS_LABORABLES

    def __init__(self, idDocente, nombreDocente, apellidoDocente, tituloGraduado, disponibilidad=None):
        if (type(idDocente) != str or not idDocente.strip().isdigit()
                or len(idDocente.strip()) != 10):
            raise ValueError("La cédula debe tener exactamente 10 dígitos numéricos.")
        self.__idDocente = idDocente.strip()
        self.nombreDocente = nombreDocente
        self.apellidoDocente = apellidoDocente
        self.tituloGraduado = tituloGraduado
        self.__asignaturasImparte = []
        self.__disponibilidad = []
        self.__horas = 0
        if disponibilidad is None:
            disponibilidad = [{"dia": d, "horaInicio": FranjaHoraria.HORA_MIN,
                               "horaFin": FranjaHoraria.HORA_MAX} for d in self.DIAS_LABORABLES]
        self.establecerDisponibilidad(disponibilidad)

    @property
    def idDocente(self):
        return self.__idDocente

    @property
    def nombreDocente(self):
        return self.__nombreDocente

    @nombreDocente.setter
    def nombreDocente(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El nombre del docente no puede estar vacío.")
        self.__nombreDocente = valor.strip()

    @property
    def apellidoDocente(self):
        return self.__apellidoDocente

    @apellidoDocente.setter
    def apellidoDocente(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El apellido del docente no puede estar vacío.")
        self.__apellidoDocente = valor.strip()

    @property
    def tituloGraduado(self):
        return self.__tituloGraduado

    @tituloGraduado.setter
    def tituloGraduado(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El título del docente no puede estar vacío.")
        self.__tituloGraduado = valor.strip()

    @property
    def nombreCompleto(self):
        return f"{self.nombreDocente} {self.apellidoDocente}"

    @property
    def asignaturasImparte(self):
        return [registro.copy() for registro in self.__asignaturasImparte]

    @property
    def disponibilidad(self):
        return [bloque.copy() for bloque in self.__disponibilidad]

    @property
    def horas(self):
        return self.__horas

    def establecerDisponibilidad(self, bloques):
        if type(bloques) != list or len(bloques) == 0:
            raise ValueError("Indique al menos un bloque de disponibilidad.")
        nuevos = []
        for bloque in bloques:
            dia, inicio, fin = bloque["dia"], bloque["horaInicio"], bloque["horaFin"]
            if dia not in self.DIAS_LABORABLES:
                raise ValueError("Seleccione un día de lunes a viernes.")
            FranjaHoraria.validarHoras(inicio, fin)
            nuevo = {"dia": dia, "horaInicio": inicio, "horaFin": fin}
            if nuevo in nuevos:
                raise ValueError("Ese bloque de disponibilidad ya está registrado.")
            nuevos.append(nuevo)
        self.__disponibilidad = nuevos

    # Método: vincularAsignatura
    def vincularAsignatura(self, carrera, asignatura):
        if carrera.mostrarMallaCurricular().buscarAsignatura(asignatura.idAsignatura) is not asignatura:
            raise ValueError("La asignatura no pertenece a esa carrera.")
        if self.imparte(carrera, asignatura):
            raise ValueError("El docente ya tiene vinculada esa asignatura.")
        self.__asignaturasImparte.append({"carrera": carrera, "asignatura": asignatura})

    def desvincularAsignatura(self, carrera, asignatura):
        self.__asignaturasImparte = [
            r for r in self.__asignaturasImparte
            if not (r["carrera"] is carrera and r["asignatura"] is asignatura)]

    def reemplazarVinculos(self, vinculos):
        """vinculos: lista de tuplas (carrera, asignatura)."""
        self.__asignaturasImparte = []
        for carrera, asignatura in vinculos:
            self.vincularAsignatura(carrera, asignatura)

    def imparte(self, carrera, asignatura):
        for r in self.__asignaturasImparte:
            if r["carrera"] is carrera and r["asignatura"] is asignatura:
                return True
        return False

    # Método: comprobarDisponibilidad (sobrecargado: por franja o por día + horas)
    @singledispatchmethod
    def comprobarDisponibilidad(self, dia, horaInicio=None, horaFin=None):
        if dia not in Docente.DIAS_LABORABLES:
            raise ValueError("Seleccione un día de lunes a viernes.")
        FranjaHoraria.validarHoras(horaInicio, horaFin)
        for hora in range(horaInicio, horaFin):
            if not any(b["dia"] == dia and b["horaInicio"] <= hora and hora + 1 <= b["horaFin"]
                       for b in self.__disponibilidad):
                return False
        return True

    @comprobarDisponibilidad.register(FranjaHoraria)
    def _(self, franja):
        return self.comprobarDisponibilidad(franja.diaSemana, franja.horaInicio, franja.horaFin)

    # Método: acumularHorasDadas
    def acumularHorasDadas(self, cantidad):
        if type(cantidad) != int or cantidad <= 0:
            raise ValueError("La cantidad de horas debe ser un entero positivo.")
        self.__horas += cantidad

    def liberarHoras(self, cantidad):
        if type(cantidad) != int or cantidad <= 0:
            raise ValueError("La cantidad de horas debe ser un entero positivo.")
        self.__horas = max(0, self.__horas - cantidad)

    def a_diccionario(self):
        return {"idDocente": self.idDocente, "nombreDocente": self.nombreDocente,
                "apellidoDocente": self.apellidoDocente, "tituloGraduado": self.tituloGraduado,
                "disponibilidad": self.disponibilidad,
                "asignaturas": [{"carrera": r["carrera"].nombre,
                                 "idAsignatura": r["asignatura"].idAsignatura}
                                for r in self.__asignaturasImparte]}
