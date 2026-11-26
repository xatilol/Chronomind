import unicodedata

from dominio.asignatura import Asignatura
from dominio.carrera import Carrera
from dominio.docente import Docente
from dominio.paralelo import Paralelo
from patrones.builder import HorarioBuilder
from patrones.factory import FabricaRequisitos, FabricaSalones
from servicios.observadores import ObservadorHorasDocente, RegistroActividad


class Catalogo:
    """Mantiene en memoria carreras, docentes, salones, paralelos y horarios, y los persiste."""

    def __init__(self, repoCarreras, repoDocentes, repoSalones, repoParalelos, repoHorarios):
        self.__repos = {"carreras": repoCarreras, "docentes": repoDocentes, "salones": repoSalones,
                        "paralelos": repoParalelos, "horarios": repoHorarios}
        self.__carreras = []
        self.__docentes = []
        self.__salones = []
        self.__paralelos = []
        self.__horarios = []
        self.__observadores = [ObservadorHorasDocente(), RegistroActividad()]
        self.avisosCarga = []
        self.__cargar()

    # ---------- carga ----------
    def __cargar(self):
        for d in self.__repos["carreras"].cargar():
            carrera = Carrera(d["nombre"])
            for nivel, lista in d.get("niveles", {}).items():
                for a in lista:
                    carrera.mostrarMallaCurricular().agregarAsignaturasNivel(int(nivel), Asignatura(
                        a["idAsignatura"], a["nombreAsignatura"], a["horasSemestre"],
                        FabricaRequisitos.crear(a.get("requisito")), a.get("cupos", 35)))
            self.__carreras.append(carrera)
        for d in self.__repos["salones"].cargar():
            self.__salones.append(FabricaSalones.crear(d))
        for d in self.__repos["docentes"].cargar():
            docente = Docente(d["idDocente"], d["nombreDocente"], d["apellidoDocente"],
                              d["tituloGraduado"], d.get("disponibilidad"))
            for v in d.get("asignaturas", []):
                carrera = self.buscarCarrera(v["carrera"])
                asignatura = carrera.mostrarMallaCurricular().buscarAsignatura(v["idAsignatura"]) if carrera else None
                if asignatura is None:
                    self.avisosCarga.append(f"Docente {docente.nombreCompleto}: vínculo omitido ({v}).")
                    continue
                docente.vincularAsignatura(carrera, asignatura)
            self.__docentes.append(docente)
        for d in self.__repos["paralelos"].cargar():
            carrera = self.buscarCarrera(d["carrera"])
            if carrera is not None:
                self.__paralelos.append(Paralelo(d["letraParalelo"], d["capacidadEstudiante"],
                                                 carrera, d["nivel"]))
        for d in self.__repos["horarios"].cargar():
            self.__reconstruirHorario(d)

    def __reconstruirHorario(self, d):
        from dominio.franja_horaria import FranjaHoraria
        carrera = self.buscarCarrera(d["carrera"])
        paralelo = self.buscarParalelo(carrera, d["nivel"], d["paralelo"]) if carrera else None
        if paralelo is None:
            self.avisosCarga.append(f"Horario {d.get('idHorario')} omitido: carrera o paralelo inexistente.")
            return
        horario = (HorarioBuilder().conId(d["idHorario"]).conPeriodo(d["periodo"]).conCarrera(carrera)
                   .conNivel(d["nivel"]).conParalelo(paralelo).construir())
        self.suscribirObservadores(horario)
        malla = carrera.mostrarMallaCurricular()
        for m in d.get("materias", []):
            try:
                horario.agregarMateria(m["idClase"], malla.buscarAsignatura(m["idAsignatura"]),
                                       self.buscarDocente(m["idDocente"]), self.buscarSalon(m["idSalon"]),
                                       FranjaHoraria.desde_diccionario(m["franjaHoraria"]), self.__horarios)
            except (ValueError, AttributeError) as error:
                self.avisosCarga.append(f"Clase {m.get('idClase')} omitida: {error}")
        self.__horarios.append(horario)

    def suscribirObservadores(self, horario):
        for observador in self.__observadores:
            horario.suscribir(observador)

    @property
    def registroActividad(self):
        return self.__observadores[1]

    # ---------- guardado ----------
    def guardar(self, *que):
        datos = {"carreras": self.__carreras, "docentes": self.__docentes, "salones": self.__salones,
                 "paralelos": self.__paralelos, "horarios": self.__horarios}
        for clave in (que or datos.keys()):
            self.__repos[clave].guardar([o.a_diccionario() for o in datos[clave]])

    # ---------- consultas ----------
    @property
    def carreras(self):
        return self.__carreras.copy()

    @property
    def docentes(self):
        return self.__docentes.copy()

    @property
    def salones(self):
        return self.__salones.copy()

    @property
    def paralelos(self):
        return self.__paralelos.copy()

    @property
    def horarios(self):
        return self.__horarios.copy()

    def buscarCarrera(self, nombre):
        return next((c for c in self.__carreras if c.nombre == nombre), None)

    def buscarDocente(self, idDocente):
        return next((d for d in self.__docentes if d.idDocente == idDocente), None)

    def buscarSalon(self, idSalon):
        return next((s for s in self.__salones if s.idSalon == idSalon), None)

    def buscarParalelo(self, carrera, nivel, letra):
        return next((p for p in self.__paralelos if p.carrera is carrera and p.nivel == nivel
                     and p.letraParalelo == letra.strip().upper()), None)

    def paralelosDe(self, carrera, nivel):
        return sorted((p for p in self.__paralelos if p.carrera is carrera and p.nivel == nivel),
                      key=lambda p: p.letraParalelo)

    def buscarHorario(self, carrera, nivel, letra, periodo):
        return next((h for h in self.__horarios if h.carrera is carrera and h.nivel == nivel
                     and h.paralelo.letraParalelo == letra and h.periodo == periodo), None)

    def docentesDe(self, carrera, asignatura):
        return [d for d in self.__docentes if d.imparte(carrera, asignatura)]

    def salonesAptos(self, asignatura, paralelo):
        cupos = min(asignatura.cupos, paralelo.capacidadEstudiante)
        aptos = [s for s in self.__salones if s.estaDisponible() and s.validarCapacidad(cupos)
                 and asignatura.es_salon_apto(s)]
        return sorted(aptos, key=lambda s: (s.tipo != "aula", s.capacidad))

    def clasesUsando(self, criterio):
        return [m for h in self.__horarios for m in h.materias if criterio(m)]

    # ---------- materias ----------
    def siguienteIdAsignatura(self, carrera, nivel):
        sigla = "".join(c for c in unicodedata.normalize("NFKD", carrera.nombre.split()[0])
                        if c.isascii() and c.isalpha()).upper()[:3] or "ASG"
        usados = {a.idAsignatura for a in carrera.mostrarMallaCurricular().todasLasAsignaturas()}
        n = 1
        while f"{sigla}-{nivel}-{n:02d}" in usados:
            n += 1
        return f"{sigla}-{nivel}-{n:02d}"

    def agregarAsignatura(self, carrera, nivel, asignatura):
        carrera.mostrarMallaCurricular().agregarAsignaturasNivel(nivel, asignatura)
        self.guardar("carreras")

    def eliminarAsignatura(self, carrera, asignatura):
        if self.clasesUsando(lambda m: m.asignatura is asignatura):
            raise ValueError("Esa materia ya está en horarios creados; elimine primero esos horarios.")
        for docente in self.__docentes:
            docente.desvincularAsignatura(carrera, asignatura)
        carrera.mostrarMallaCurricular().quitarAsignatura(asignatura.idAsignatura)
        self.guardar("carreras", "docentes")

    # ---------- docentes ----------
    def guardarDocente(self, cedula, nombre, apellido, titulo, disponibilidad, vinculos):
        existente = self.buscarDocente(cedula.strip())
        if existente is None:
            docente = Docente(cedula, nombre, apellido, titulo, disponibilidad)
            docente.reemplazarVinculos(vinculos)
            self.__docentes.append(docente)
        else:  # se modifica el mismo objeto para no romper los horarios que lo usan
            if self.clasesUsando(lambda m: m.docente is existente):
                usadas = {(m.carrera, m.asignatura) for m in self.clasesUsando(lambda m: m.docente is existente)}
                if not usadas <= {(c, a) for c, a in vinculos}:
                    raise ValueError("No puede desvincular una materia que ya tiene clases con este docente.")
            existente.nombreDocente = nombre
            existente.apellidoDocente = apellido
            existente.tituloGraduado = titulo
            existente.establecerDisponibilidad(disponibilidad)
            existente.reemplazarVinculos(vinculos)
        self.guardar("docentes")

    def eliminarDocente(self, docente):
        if self.clasesUsando(lambda m: m.docente is docente):
            raise ValueError("Ese docente tiene clases en horarios creados.")
        self.__docentes.remove(docente)
        self.guardar("docentes")

    # ---------- salones ----------
    def agregarSalon(self, salon):
        if self.buscarSalon(salon.idSalon) is not None:
            raise ValueError("Ya existe un salón con ese código.")
        self.__salones.append(salon)
        self.guardar("salones")

    def eliminarSalon(self, salon):
        if self.clasesUsando(lambda m: m.salon is salon):
            raise ValueError("Ese salón tiene clases en horarios creados.")
        self.__salones.remove(salon)
        self.guardar("salones")

    # ---------- paralelos ----------
    def agregarParalelo(self, paralelo):
        if self.buscarParalelo(paralelo.carrera, paralelo.nivel, paralelo.letraParalelo) is not None:
            raise ValueError("Ese paralelo ya existe en ese nivel.")
        self.__paralelos.append(paralelo)
        self.guardar("paralelos")

    def eliminarParalelo(self, paralelo):
        if any(h.paralelo is paralelo for h in self.__horarios):
            raise ValueError("Ese paralelo tiene horarios creados; elimínelos primero.")
        self.__paralelos.remove(paralelo)
        self.guardar("paralelos")

    # ---------- horarios ----------
    def registrarHorario(self, horario):
        self.suscribirObservadores(horario)
        self.__horarios.append(horario)

    def eliminarHorario(self, horario):
        horario.vaciar()
        self.__horarios.remove(horario)
        self.guardar("horarios")
