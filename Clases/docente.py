from franja_horaria import FranjaHoraria


class Docente:
    # Atributo de clase: los días disponibles son comunes a los docentes.
    DIAS_LABORABLES = FranjaHoraria.DIAS_LABORABLES

    def __init__(self, idDocente, nombreDocente):
        if type(idDocente) != str or idDocente.strip() == "":
            raise ValueError("El código del docente no puede estar vacío.")
        self.__idDocente = idDocente.strip()
        self.nombreDocente = nombreDocente
        self.__asignaturasImparte = []
        self.__disponibilidad = []
        self.__horas = 0

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
    def asignaturasImparte(self):
        resultado = []
        for registro in self.__asignaturasImparte:
            resultado.append(registro.copy())
        return resultado

    @property
    def disponibilidad(self):
        resultado = []
        for bloque in self.__disponibilidad:
            resultado.append(bloque.copy())
        return resultado

    @property
    def horas(self):
        return self.__horas

    #Método: vincularAsignatura

    def vincularAsignatura(self, carrera, asignatura):
        # Debe ser una asignatura existente en la malla de esa carrera.
        malla = carrera.mostrarMallaCurricular()
        encontrada = False
        for nivel in malla.niveles:
            if asignatura in malla.consultarAsignaturasNivel(nivel):
                encontrada = True
        if not encontrada:
            raise ValueError("La asignatura no pertenece a esa carrera.")

        for registro in self.__asignaturasImparte:
            if (registro["carrera"].nombre == carrera.nombre
                    and registro["asignatura"].idAsignatura == asignatura.idAsignatura):
                raise ValueError("El docente ya tiene vinculada esa asignatura.")

        # Asociación: usa la asignatura de la malla, no crea otra.
        self.__asignaturasImparte.append({
            "carrera": carrera,
            "asignatura": asignatura
        })

    @staticmethod
    def validarDisponibilidad(dia, horaInicio, horaFin):
        if dia not in Docente.DIAS_LABORABLES:
            raise ValueError("Seleccione un día de lunes a viernes.")
        FranjaHoraria.validarHoras(horaInicio, horaFin)

    def registrarDisponibilidad(self, dia, horaInicio, horaFin):
        self.validarDisponibilidad(dia, horaInicio, horaFin)
        nuevo = {"dia": dia, "horaInicio": horaInicio, "horaFin": horaFin}
        if nuevo in self.__disponibilidad:
            raise ValueError("Ese bloque de disponibilidad ya está registrado.")
        self.__disponibilidad.append(nuevo)

    #Método: comprobarDisponibilidad

    def comprobarDisponibilidad(self, dia, horaInicio, horaFin):
        self.validarDisponibilidad(dia, horaInicio, horaFin)
        # Revisa cada hora solicitada. También admite bloques contiguos.
        for hora in range(horaInicio, horaFin):
            disponible = False
            for bloque in self.__disponibilidad:
                if (bloque["dia"] == dia
                        and bloque["horaInicio"] <= hora
                        and hora + 1 <= bloque["horaFin"]):
                    disponible = True
            if not disponible:
                return False
        return True

    #Método: acumularHorasDadas

    def acumularHorasDadas(self, cantidad):
        if type(cantidad) != int or cantidad <= 0:
            raise ValueError("La cantidad de horas debe ser un entero positivo.")
        self.__horas += cantidad

    def anadirDiccionario(self):
        asignaturas = []
        for registro in self.__asignaturasImparte:
            asignaturas.append({
                "carrera": registro["carrera"].nombre,
                "idAsignatura": registro["asignatura"].idAsignatura
            })
        return {
            "idDocente": self.idDocente,
            "nombreDocente": self.nombreDocente,
            "asignaturasImparte": asignaturas,
            "disponibilidad": self.disponibilidad,
            "horas": self.horas
        }

    @classmethod
    def desdeDiccionario(cls, datos, carreras):
        docente = cls(datos["idDocente"], datos["nombreDocente"])
        for bloque in datos["disponibilidad"]:
            docente.registrarDisponibilidad(
                bloque["dia"], bloque["horaInicio"], bloque["horaFin"]
            )
        horas = datos["horas"]
        if type(horas) != int or horas < 0:
            raise ValueError("Las horas guardadas deben ser un entero no negativo.")
        if horas > 0:
            docente.acumularHorasDadas(horas)

        # Recupera las mismas asignaturas cargadas en las mallas.
        for referencia in datos["asignaturasImparte"]:
            encontrada = False
            for carrera in carreras:
                if carrera.nombre == referencia["carrera"]:
                    malla = carrera.mostrarMallaCurricular()
                    for nivel in malla.niveles:
                        for asignatura in malla.consultarAsignaturasNivel(nivel):
                            if asignatura.idAsignatura == referencia["idAsignatura"]:
                                docente.vincularAsignatura(carrera, asignatura)
                                encontrada = True
            if not encontrada:
                raise ValueError("Una asignatura del docente ya no existe en su carrera.")
        return docente
