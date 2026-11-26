from dominio.horario_completo import HorarioCompleto


class HorarioBuilder:
    """Builder: arma un HorarioCompleto paso a paso y valida al construir."""

    def __init__(self):
        self.__datos = {}

    def conId(self, idHorario):
        self.__datos["idHorario"] = idHorario
        return self

    def conPeriodo(self, periodo):
        self.__datos["periodo"] = periodo
        return self

    def conCarrera(self, carrera):
        self.__datos["carrera"] = carrera
        return self

    def conNivel(self, nivel):
        self.__datos["nivel"] = nivel
        return self

    def conParalelo(self, paralelo):
        self.__datos["paralelo"] = paralelo
        return self

    def construir(self):
        faltan = [c for c in ("idHorario", "periodo", "carrera", "nivel", "paralelo")
                  if c not in self.__datos]
        if faltan:
            raise ValueError("Falta indicar para el horario: " + ", ".join(faltan))
        return HorarioCompleto(self.__datos["idHorario"], self.__datos["periodo"],
                               self.__datos["nivel"], self.__datos["carrera"], self.__datos["paralelo"])
