class Asignatura:
    def __init__(self, idAsignatura, nombreAsignatura, horasSemanales, necesitaLaboratorio):
        if type(idAsignatura) != str or idAsignatura.strip() == "":
            raise ValueError("El código debe ser un texto no vacío.")

        self.__idAsignatura = idAsignatura.strip()
        # Estas asignaciones pasan por los setters para validar los datos.
        self.nombreAsignatura = nombreAsignatura
        self.horasSemanales = horasSemanales
        self.necesitaLaboratorio = necesitaLaboratorio

    @property
    def idAsignatura(self):
        # Solo lectura: cambiarlo sin revisar la malla podría duplicar códigos.
        return self.__idAsignatura

    @property
    def nombreAsignatura(self):
        return self.__nombreAsignatura

    @nombreAsignatura.setter
    def nombreAsignatura(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El nombre debe ser un texto no vacío.")
        self.__nombreAsignatura = valor.strip()

    @property
    def horasSemanales(self):
        return self.__horasSemanales

    @horasSemanales.setter
    def horasSemanales(self, valor):
        if type(valor) != int or valor <= 0:
            raise ValueError("Las horas semanales deben ser un entero positivo.")
        self.__horasSemanales = valor

    @property
    def necesitaLaboratorio(self):
        return self.__necesitaLaboratorio

    @necesitaLaboratorio.setter
    def necesitaLaboratorio(self, valor):
        if type(valor) != bool:
            raise ValueError("Indique True o False para el uso de laboratorio.")
        self.__necesitaLaboratorio = valor

    #Método: usaLaboratorio

    def usaLaboratorio(self):
        return self.__necesitaLaboratorio

    #Metodo: verInformacionAsignatura

    def verInformacionAsignatura(self):
        laboratorio = "No"
        if self.usaLaboratorio():
            laboratorio = "Sí"

        informacion = f"Código: {self.idAsignatura}\n"
        informacion += f"Asignatura: {self.nombreAsignatura}\n"
        informacion += f"Horas semanales: {self.horasSemanales}\n"
        informacion += f"Necesita laboratorio: {laboratorio}"
        return informacion

    def anadirDiccionario(self):
        return {
            "idAsignatura": self.idAsignatura,
            "nombreAsignatura": self.nombreAsignatura,
            "horasSemanales": self.horasSemanales,
            "necesitaLaboratorio": self.necesitaLaboratorio
        }
