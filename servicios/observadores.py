from datetime import datetime

from patrones.observer import Observador


class ObservadorHorasDocente(Observador):
    """Mantiene al día las horas dadas por cada docente cuando cambia un horario."""

    def actualizar(self, evento, datos):
        if evento == "clase_agregada":
            datos.docente.acumularHorasDadas(datos.duracion)
        elif evento == "clase_quitada":
            datos.docente.liberarHoras(datos.duracion)


class RegistroActividad(Observador):
    """Guarda un historial legible de los cambios hechos en los horarios."""

    LIMITE = 200

    def __init__(self):
        self.__entradas = []

    @property
    def entradas(self):
        return self.__entradas.copy()

    def actualizar(self, evento, datos):
        accion = "Añadida" if evento == "clase_agregada" else "Quitada"
        f = datos.franjaHoraria
        texto = (f"{datetime.now():%H:%M:%S} | {accion}: {datos.asignatura.nombreAsignatura} "
                 f"({datos.carrera.nombre} N{datos.nivel} '{datos.paralelo.letraParalelo}') "
                 f"{f.diaSemana} {f.horaInicio}-{f.horaFin} | {datos.docente.nombreCompleto} | "
                 f"{datos.salon.nombreSalon}")
        self.__entradas.append(texto)
        del self.__entradas[:-self.LIMITE]
