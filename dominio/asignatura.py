import math
from abc import ABC, abstractmethod


class RequisitoEspacio(ABC):
    """Estrategia: qué tipo de espacio necesita una asignatura."""

    @abstractmethod
    def es_compatible(self, salon) -> bool:
        pass

    @abstractmethod
    def requiere_laboratorio(self) -> bool:
        pass

    @abstractmethod
    def obtener_descripcion(self) -> str:
        pass

    @abstractmethod
    def a_diccionario(self) -> dict:
        pass


class RequisitoAulaTeorica(RequisitoEspacio):
    def es_compatible(self, salon) -> bool:
        return True

    def requiere_laboratorio(self) -> bool:
        return False

    def obtener_descripcion(self) -> str:
        return "Aula teórica"

    def a_diccionario(self) -> dict:
        return {"tipo": "aula"}


class RequisitoLaboratorio(RequisitoEspacio):
    def __init__(self, equipos_minimos: int = 1, tipo_equipo: str = ""):
        if type(equipos_minimos) != int or equipos_minimos <= 0:
            raise ValueError("La cantidad mínima de equipos debe ser un entero positivo.")
        self.equipos_minimos = equipos_minimos
        self.tipo_equipo = (tipo_equipo or "").strip()

    def es_compatible(self, salon) -> bool:
        # Polimorfismo: Aula responde False y Laboratorio comprueba sus equipos.
        return salon.cumpleEquipos(self.equipos_minimos, self.tipo_equipo or None)

    def requiere_laboratorio(self) -> bool:
        return True

    def obtener_descripcion(self) -> str:
        extra = f" de {self.tipo_equipo}" if self.tipo_equipo else ""
        return f"Laboratorio (mín. {self.equipos_minimos} equipos{extra})"

    def a_diccionario(self) -> dict:
        return {"tipo": "laboratorio", "equiposMinimos": self.equipos_minimos,
                "tipoEquipo": self.tipo_equipo}


class Asignatura:
    SEMANAS_SEMESTRE = 16

    def __init__(self, idAsignatura, nombreAsignatura, horasSemestre,
                 requisito_espacio=None, cupos=35):
        if type(idAsignatura) != str or idAsignatura.strip() == "":
            raise ValueError("El código debe ser un texto no vacío.")
        self.__idAsignatura = idAsignatura.strip()
        self.nombreAsignatura = nombreAsignatura
        self.horasSemestre = horasSemestre
        self.cupos = cupos
        self.requisito_espacio = requisito_espacio if requisito_espacio else RequisitoAulaTeorica()

    @property
    def idAsignatura(self):
        return self.__idAsignatura

    @property
    def nombreAsignatura(self):
        return self.__nombreAsignatura

    @nombreAsignatura.setter
    def nombreAsignatura(self, valor):
        if type(valor) != str or valor.strip() == "":
            raise ValueError("El nombre de la asignatura no puede estar vacío.")
        self.__nombreAsignatura = valor.strip()

    @property
    def horasSemestre(self):
        return self.__horasSemestre

    @horasSemestre.setter
    def horasSemestre(self, valor):
        if type(valor) != int or valor < self.SEMANAS_SEMESTRE:
            raise ValueError(f"Las horas por semestre deben ser un entero de al menos {self.SEMANAS_SEMESTRE}.")
        self.__horasSemestre = valor

    @property
    def horasSemanales(self):
        """Horas por semana: las horas del semestre repartidas en 16 semanas (redondeo hacia arriba)."""
        return math.ceil(self.__horasSemestre / self.SEMANAS_SEMESTRE)

    @property
    def cupos(self):
        return self.__cupos

    @cupos.setter
    def cupos(self, valor):
        if type(valor) != int or valor <= 0:
            raise ValueError("Los cupos deben ser un entero positivo.")
        self.__cupos = valor

    @property
    def requisito_espacio(self):
        return self.__requisito_espacio

    @requisito_espacio.setter
    def requisito_espacio(self, valor):
        if not isinstance(valor, RequisitoEspacio):
            raise ValueError("Debe asignar un requisito de espacio válido.")
        self.__requisito_espacio = valor

    def es_salon_apto(self, salon) -> bool:
        return self.__requisito_espacio.es_compatible(salon)

    # Método del diagrama: usaLaboratorio
    def usaLaboratorio(self) -> bool:
        return self.__requisito_espacio.requiere_laboratorio()

    def verInformacionAsignatura(self) -> str:
        return (f"Código: {self.idAsignatura}\nAsignatura: {self.nombreAsignatura}\n"
                f"Horas por semestre: {self.horasSemestre} ({self.horasSemanales} h/semana)\n"
                f"Cupos: {self.cupos}\nEspacio: {self.requisito_espacio.obtener_descripcion()}")

    def a_diccionario(self):
        return {"idAsignatura": self.idAsignatura, "nombreAsignatura": self.nombreAsignatura,
                "horasSemestre": self.horasSemestre, "cupos": self.cupos,
                "requisito": self.requisito_espacio.a_diccionario()}
