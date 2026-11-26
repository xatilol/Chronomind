import unicodedata

from dominio.franja_horaria import FranjaHoraria
from patrones.builder import HorarioBuilder


class ResultadoGeneracion:
    def __init__(self):
        self.horarios = []
        self.advertencias = []


class GeneradorHorarios:
    """Crea horarios automáticos sin choques de docente, salón ni paralelo."""

    def __init__(self, catalogo):
        self.__catalogo = catalogo  # inyección de dependencias

    @staticmethod
    def idHorario(carrera, nivel, letra, periodo):
        sigla = "".join(c for c in unicodedata.normalize("NFKD", carrera.nombre)
                        if c.isascii() and c.isalnum()).upper()[:12]
        return f"H-{sigla}-N{nivel}-{letra}-{periodo}"

    def generar(self, carrera, nivel, periodo, estrategia):
        resultado = ResultadoGeneracion()
        paralelos = self.__catalogo.paralelosDe(carrera, nivel)
        if not paralelos:
            raise ValueError("Ese nivel no tiene paralelos. Créelos primero en «Paralelos».")
        if not carrera.mostrarMallaCurricular().consultarAsignaturasNivel(nivel):
            raise ValueError("Ese nivel no tiene materias registradas.")
        for paralelo in paralelos:
            anterior = self.__catalogo.buscarHorario(carrera, nivel, paralelo.letraParalelo, periodo)
            if anterior is not None:
                self.__catalogo.eliminarHorario(anterior)
            horario = paralelo.asignarParHorario(
                self.idHorario(carrera, nivel, paralelo.letraParalelo, periodo), periodo)
            self.__catalogo.suscribirObservadores(horario)  # para que cuente horas mientras se arma
            self.__llenar(horario, estrategia, resultado.advertencias)
            self.__catalogo.registrarHorario(horario)
            resultado.horarios.append(horario)
        self.__catalogo.guardar("horarios")
        return resultado

    def __llenar(self, horario, estrategia, advertencias):
        etiqueta = f"Paralelo {horario.paralelo.letraParalelo}"
        asignaturas = sorted(horario.carrera.mostrarMallaCurricular().consultarAsignaturasNivel(horario.nivel),
                             key=lambda a: -a.horasSemanales)
        for posicion, asignatura in enumerate(asignaturas):
            docentes = self.__catalogo.docentesDe(horario.carrera, asignatura)
            if not docentes:
                advertencias.append(f"{etiqueta} · {asignatura.nombreAsignatura}: no tiene docente vinculado.")
                continue
            salones = self.__catalogo.salonesAptos(asignatura, horario.paralelo)
            if not salones:
                advertencias.append(f"{etiqueta} · {asignatura.nombreAsignatura}: no hay salón apto "
                                    f"({asignatura.requisito_espacio.obtener_descripcion()}).")
                continue
            usados = set()
            for i, duracion in enumerate(estrategia.dividir(asignatura.horasSemanales)):
                if not self.__ubicar(horario, asignatura, docentes, salones, duracion, estrategia, posicion + i, usados):
                    # Si no cabe el bloque completo, se intenta hora por hora.
                    for _ in range(duracion):
                        self.__ubicar(horario, asignatura, docentes, salones, 1, estrategia, posicion + i, usados)
            faltan = asignatura.horasSemanales - horario.horasRegistradas(asignatura)
            if faltan > 0:
                advertencias.append(f"{etiqueta} · {asignatura.nombreAsignatura}: faltan {faltan} h por ubicar "
                                    f"(sin espacio libre de docente/salón).")

    def __ubicar(self, horario, asignatura, docentes, salones, duracion, estrategia, indice, usados):
        dias = estrategia.ordenDias(indice)
        dias = [d for d in dias if d not in usados] + [d for d in dias if d in usados]
        for dia in dias:
            for inicio in estrategia.ordenHoras(duracion):
                franja = FranjaHoraria(dia, inicio, inicio + duracion)
                for docente in sorted(docentes, key=lambda d: d.horas):
                    if not docente.comprobarDisponibilidad(franja):
                        continue
                    for salon in salones:
                        try:
                            horario.agregarMateria(None, asignatura, docente, salon, franja,
                                                   self.__catalogo.horarios)
                        except ValueError:
                            continue
                        usados.add(dia)
                        return True
        return False
