from dominio.asignatura import RequisitoAulaTeorica, RequisitoLaboratorio
from dominio.laboratorio import Laboratorio
from dominio.salon import Aula


class FabricaSalones:
    """Factory: crea el salón correcto según su tipo (abierta a nuevos tipos)."""

    __creadores = {
        "aula": lambda d: Aula(d["idSalon"], d["nombreSalon"], d["capacidad"], d.get("disponible", True)),
        "laboratorio": lambda d: Laboratorio(d["idSalon"], d["nombreSalon"], d["capacidad"],
                                             d["tiposEquipos"], d["cantidadEquipos"],
                                             d.get("disponible", True)),
    }

    @classmethod
    def registrar(cls, tipo, creador):
        cls.__creadores[tipo] = creador

    @classmethod
    def crear(cls, datos):
        tipo = datos.get("tipo")
        if tipo not in cls.__creadores:
            raise ValueError(f"Tipo de salón desconocido: {tipo}")
        return cls.__creadores[tipo](datos)


class FabricaRequisitos:
    """Factory: crea el requisito de espacio de una asignatura."""

    @staticmethod
    def crear(datos):
        if datos is None or datos.get("tipo", "aula") == "aula":
            return RequisitoAulaTeorica()
        if datos["tipo"] == "laboratorio":
            return RequisitoLaboratorio(datos.get("equiposMinimos", 1), datos.get("tipoEquipo", ""))
        raise ValueError("Tipo de requisito desconocido.")
