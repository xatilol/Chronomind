from franja_horaria import FranjaHoraria


class Docente:
    # Atributo de clase: los días disponibles son comunes a los docentes.
    DIAS_LABORABLES = FranjaHoraria.DIAS_LABORABLES

    def __init__(self, idDocente, nombreDocente, apellidoDocente, tituloGraduado,disponibilidad=None):
        
        if type(idDocente) != str or not idDocente.strip().isdigit() \ or len(idDocente.strip()) != 10:
            raise ValueError("La cédula debe tener exactamente 10 dígitos numéricos.")
        self.__idDocente = idDocente.strip()
        # Estas asignaciones pasan por los setters para validar los datos.
        self.nombreDocente = nombreDocente
        self.apellidoDocente = apellidoDocente
        self.tituloGraduado = tituloGraduado
        self.__asignaturasImparte = []
        self.__disponibilidad = []
        self.__horas = 0

        # La disponibilidad inicial se recibe al crear el docente.
        # Cada bloque contiene: dia, horaInicio y horaFin.
        if disponibilidad is not None:
            if type(disponibilidad) != list:
                raise ValueError("La disponibilidad debe ser una lista de bloques.")
            for bloque in disponibilidad:
                dia = bloque["dia"]
                inicio = bloque["horaInicio"]
                fin = bloque["horaFin"]
                if dia not in Docente.DIAS_LABORABLES:
                    raise ValueError("Seleccione un día de lunes a viernes.")
                FranjaHoraria.validarHoras(inicio, fin)
                nuevo = {"dia": dia, "horaInicio": inicio, "horaFin": fin}
                if nuevo in self.__disponibilidad:
                    raise ValueError("Ese bloque de disponibilidad ya está registrado.")
                self.__disponibilidad.append(nuevo)

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


    #Método: comprobarDisponibilidad

    def comprobarDisponibilidad(self, dia, horaInicio, horaFin):
        if dia not in Docente.DIAS_LABORABLES:
            raise ValueError("Seleccione un día de lunes a viernes.")
        FranjaHoraria.validarHoras(horaInicio, horaFin)

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
