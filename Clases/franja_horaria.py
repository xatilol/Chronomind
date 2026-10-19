class FranjaHoraria:
    DIAS_LABORABLES = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")

    def __init__(self, diaSemana, horaInicio, horaFin, jornada):
        self.diaSemana = diaSemana
        self.cambiarHoras(horaInicio, horaFin)
        self.jornada = jornada

    @property
    def diaSemana(self):
        return self.__diaSemana

    @diaSemana.setter
    def diaSemana(self, valor):
        if valor not in self.DIAS_LABORABLES:
            raise ValueError("Seleccione un día de lunes a viernes.")
        self.__diaSemana = valor

    @property
    def horaInicio(self):
        return self.__horaInicio

    @horaInicio.setter
    def horaInicio(self, valor):
        self.cambiarHoras(valor, self.__horaFin)

    @property
    def horaFin(self):
        return self.__horaFin

    @horaFin.setter
    def horaFin(self, valor):
        self.cambiarHoras(self.__horaInicio, valor)

    @property
    def jornada(self):
        return self.__jornada

    @jornada.setter
    def jornada(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("La jornada debe ser un texto no vacío.")
        self.__jornada = valor.strip()

    @staticmethod
    def validarHoras(horaInicio, horaFin):
        if type(horaInicio) != int or type(horaFin) != int:
            raise ValueError("Las horas deben ser enteras, por ejemplo 7 y 9.")
        if horaInicio < 7 or horaFin > 20 or horaInicio >= horaFin:
            raise ValueError("Use horas entre 7 y 20, con inicio menor que fin.")

    def cambiarHoras(self, horaInicio, horaFin):
        # Valida primero para no dejar un intervalo a medio modificar.
        self.validarHoras(horaInicio, horaFin)
        self.__horaInicio = horaInicio
        self.__horaFin = horaFin

    #Método: generarBloqueHorario

    def generarBloqueHorario(self):
        return (
            f"{self.diaSemana} | {self.horaInicio}:00 - {self.horaFin}:00"
            f" | {self.jornada}"
        )

    #Método: cruzaConOtroHorario


