from dominio.asignatura import Asignatura
from dominio.paralelo import Paralelo
from patrones.factory import FabricaRequisitos, FabricaSalones
from patrones.strategy import ESTRATEGIAS
from servicios.editor_horario import EditorHorario


class FachadaChronomind:
    """Facade: la interfaz gráfica solo habla con esta clase."""

    def __init__(self, autenticacion, catalogo, generador):
        self.__autenticacion = autenticacion
        self.__catalogo = catalogo
        self.__generador = generador
        self.__estrategias = {e.nombre: e() for e in ESTRATEGIAS}
        self.__gestor = None

    # ----- sesión -----
    def iniciarSesion(self, usuario, clave):
        self.__gestor = self.__autenticacion.autenticar(usuario, clave)
        return self.__gestor is not None

    def cerrarSesion(self):
        self.__gestor = None

    @property
    def gestor(self):
        return self.__gestor

    @property
    def catalogo(self):
        return self.__catalogo

    # ----- consultas -----
    def carreras(self):
        return self.__catalogo.carreras

    def nombresEstrategias(self):
        return list(self.__estrategias.keys())

    def avisosDeCarga(self):
        return list(self.__catalogo.avisosCarga)

    def registroActividad(self):
        return self.__catalogo.registroActividad.entradas

    # ----- materias -----
    def guardarMateria(self, carrera, nivel, nombre, horasSemestre, cupos, requiereLab,
                       equipos, tipoEquipo, asignatura=None):
        requisito = FabricaRequisitos.crear({"tipo": "laboratorio", "equiposMinimos": equipos,
                                             "tipoEquipo": tipoEquipo} if requiereLab else {"tipo": "aula"})
        if asignatura is None:
            nueva = Asignatura(self.__catalogo.siguienteIdAsignatura(carrera, nivel), nombre,
                               horasSemestre, requisito, cupos)
            self.__catalogo.agregarAsignatura(carrera, nivel, nueva)
            return nueva
        asignatura.nombreAsignatura = nombre
        asignatura.horasSemestre = horasSemestre
        asignatura.cupos = cupos
        asignatura.requisito_espacio = requisito
        self.__catalogo.guardar("carreras")
        return asignatura

    def eliminarMateria(self, carrera, asignatura):
        self.__catalogo.eliminarAsignatura(carrera, asignatura)

    # ----- docentes / salones / paralelos -----
    def guardarDocente(self, *args):
        self.__catalogo.guardarDocente(*args)

    def eliminarDocente(self, docente):
        self.__catalogo.eliminarDocente(docente)

    def agregarSalon(self, datos):
        self.__catalogo.agregarSalon(FabricaSalones.crear(datos))

    def eliminarSalon(self, salon):
        self.__catalogo.eliminarSalon(salon)

    def agregarParalelo(self, carrera, nivel, letra, capacidad):
        self.__catalogo.agregarParalelo(Paralelo(letra, capacidad, carrera, nivel))

    def eliminarParalelo(self, paralelo):
        self.__catalogo.eliminarParalelo(paralelo)

    def alternarDisponibilidad(self, salon):
        salon.disponible = not salon.disponible
        self.__catalogo.guardar("salones")

    def docentesDe(self, carrera, asignatura):
        return self.__catalogo.docentesDe(carrera, asignatura)

    def salonesPara(self, asignatura, paralelo):
        return self.__catalogo.salonesAptos(asignatura, paralelo)

    # ----- horarios -----
    def horariosExistentes(self, carrera, nivel, periodo):
        return [h for h in self.__catalogo.horarios
                if h.carrera is carrera and h.nivel == nivel and h.periodo == periodo.strip()]

    def generarHorarios(self, carrera, nivel, periodo, nombreEstrategia):
        if periodo.strip() == "":
            raise ValueError("Indique el período académico (por ejemplo 2026-2).")
        return self.__generador.generar(carrera, nivel, periodo.strip(), self.__estrategias[nombreEstrategia])

    def horarios(self):
        return sorted(self.__catalogo.horarios,
                      key=lambda h: (h.carrera.nombre, h.nivel, h.paralelo.letraParalelo, h.periodo))

    def eliminarHorario(self, horario):
        self.__catalogo.eliminarHorario(horario)

    def iniciarEdicion(self, horario):
        return EditorHorario(horario, self.__catalogo)

    def verificarConflictos(self):
        """Revisa todos los horarios guardados y devuelve los choques encontrados."""
        choques = []
        horarios = self.__catalogo.horarios
        for i, h1 in enumerate(horarios):
            for h2 in horarios[i:]:
                for a in h1.materias:
                    for b in h2.materias:
                        if a is not b and a.validarChoqueMaterias(b):
                            choques.append(f"{a.asignatura.nombreAsignatura} / {b.asignatura.nombreAsignatura}")
        return choques
