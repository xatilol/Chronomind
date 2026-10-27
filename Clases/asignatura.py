from abc import ABC, abstractmethod

class RequisitoEspacio(ABC):
    """Interfaz base para definir los requisitos de espacio de una asignatura."""
    
    @abstractmethod
    def es_compatible(self, salon) -> bool:
        """Determina si un salón cumple con los requisitos necesarios."""
        pass

    @abstractmethod
    def obtener_descripcion(self) -> str:
        """Retorna una representación legible del requisito."""
        pass

class RequisitoAulaTeorica(RequisitoEspacio):
    """Requisito para asignaturas que solo requieren un aula convencional."""
    
    def es_compatible(self, salon) -> bool:
        return True  # Cualquier salón base es suficiente para teoría

    def obtener_descripcion(self) -> str:
        return "Aula Teórica Convencional"

class RequisitoLaboratorio(RequisitoEspacio):
    """Requisito para asignaturas que requieren equipos de laboratorio."""
    
    def __init__(self, equipos_minimos: int = 1):
        if type(equipos_minimos) != int or equipos_minimos <= 0:
            raise ValueError("La cantidad mínima de equipos debe ser un entero positivo.")
        self.equipos_minimos = equipos_minimos

    def es_compatible(self, salon) -> bool:
        # Usa polimorfismo en lugar de verificar el tipo exacto con isinstance
        if hasattr(salon, "ComprobarCuentaEquipos"):
            return salon.ComprobarCuentaEquipos(self.equipos_minimos)
        return False

    def obtener_descripcion(self) -> str:
        return f"Laboratorio (mínimo {self.equipos_minimos} equipos)"

class Asignatura:
    def __init__(self, idAsignatura: str, nombreAsignatura: str, horasSemanales: int, requisito_espacio: RequisitoEspacio):
        if type(idAsignatura) != str or idAsignatura.strip() == "":
            raise ValueError("El código debe ser un texto no vacío.")

        self.__idAsignatura = idAsignatura.strip()
        self.nombreAsignatura = nombreAsignatura
        self.horasSemanales = horasSemanales
        self.requisito_espacio = requisito_espacio

    @property
    def idAsignatura(self):
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
    def requisito_espacio(self) -> RequisitoEspacio:
        return self.__requisito_espacio

    @requisito_espacio.setter
    def requisito_espacio(self, valor: RequisitoEspacio):
        if not isinstance(valor, RequisitoEspacio):
            raise ValueError("Debe asignar una instancia válida de RequisitoEspacio.")
        self.__requisito_espacio = valor

    # Delegación polimórfica para consultar compatibilidad
    def es_salon_apto(self, salon) -> bool:
        return self.__requisito_espacio.es_compatible(salon)

    def verInformacionAsignatura(self) -> str:
        return (
            f"Código: {self.idAsignatura}\n"
            f"Asignatura: {self.nombreAsignatura}\n"
            f"Horas semanales: {self.horasSemanales}\n"
            f"Requisito de espacio: {self.requisito_espacio.obtener_descripcion()}"
        )
