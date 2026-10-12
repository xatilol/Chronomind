import json
from pathlib import Path

from franja_horaria import FranjaHoraria
from laboratorio import Laboratorio


class MateriasHorario:
    def __init__(self, idClase, asignatura, docente, salon, paralelo, franjaHoraria, carrera, nivel, periodo):
        if type(idClase) != str or idClase.strip() == "":
            raise ValueError("El código de la clase no puede estar vacío.")
        if type(nivel) != int or nivel <= 0:
            raise ValueError("El nivel debe ser un entero positivo.")
        if type(periodo) != str or periodo.strip() == "":
            raise ValueError("Indique el período académico.")

        self.__idClase = idClase.strip()
        self.__asignatura = asignatura
        self.__docente = docente
        self.__salon = salon
        self.__paralelo = paralelo
        self.__franjaHoraria = franjaHoraria
        self.__carrera = carrera
        self.__nivel = nivel
        self.__periodo = periodo.strip()

    @property
    def idClase(self):
        return self.__idClase

    @property
    def asignatura(self):
        return self.__asignatura

    @property
    def docente(self):
        return self.__docente

    @property
    def salon(self):
        return self.__salon

    @property
    def paralelo(self):
        return self.__paralelo

    @property
    def franjaHoraria(self):
        return self.__franjaHoraria

    @property
    def carrera(self):
        return self.__carrera

    @property
    def nivel(self):
        return self.__nivel

    @property
    def periodo(self):
        return self.__periodo

    #Método: capacidadAula

    def capacidadAula(self):
        return self.salon.validarCapacidad(self.paralelo.capacidadEstudiante)

    def validarAsignacion(self):
        # Revisa los datos de la asignación antes de guardarla.
        franja = self.franjaHoraria
        FranjaHoraria.validarHoras(franja.horaInicio, franja.horaFin)
        if (type(self.paralelo.capacidadEstudiante) != int
                or self.paralelo.capacidadEstudiante <= 0):
            raise ValueError("El tamaño del paralelo debe ser un entero positivo.")
        if (type(self.paralelo.letraParalelo) != str
                or self.paralelo.letraParalelo.strip() == ""):
            raise ValueError("El paralelo debe tener una letra o identificador.")
        if not self.salon.estaDisponible():
            raise ValueError("El salón no está habilitado para uso.")
        if not self.capacidadAula():
            raise ValueError("La capacidad del salón es insuficiente para el paralelo.")
        if self.asignatura.usaLaboratorio() and not isinstance(self.salon, Laboratorio):
            raise ValueError("Esta asignatura necesita un laboratorio.")

        asignaturas = self.carrera.mostrarMallaCurricular().consultarAsignaturasNivel(self.nivel)
        if self.asignatura not in asignaturas:
            raise ValueError("La asignatura no pertenece a ese nivel de la carrera.")

        vinculada = False
        for registro in self.docente.asignaturasImparte:
            if (registro["carrera"].nombre == self.carrera.nombre
                    and registro["asignatura"].idAsignatura == self.asignatura.idAsignatura):
                vinculada = True
        if not vinculada:
            raise ValueError("El docente no tiene vinculada esta asignatura de la carrera.")
        if not self.docente.comprobarDisponibilidad(
            franja.diaSemana, franja.horaInicio, franja.horaFin
        ):
            raise ValueError("La clase está fuera de la disponibilidad del docente.")

    #Método: validarChoqueMaterias

    def validarChoqueMaterias(self, otraMateria):
        # True significa que SÍ existe un conflicto entre las dos clases.
        return self.__hayChoqueConDatos(otraMateria.anadirDiccionario())

    def __hayChoqueConDatos(self, otra):
        # Reutilizado al comparar con un objeto y con los registros del JSON.
        if self.periodo.lower() != otra["periodo"].lower():
            return False
        franja = self.franjaHoraria
        otraFranja = FranjaHoraria.desdeDiccionario(otra["franjaHoraria"])
        if not franja.cruzaConOtroHorario(otraFranja):
            return False

        mismoDocente = self.docente.idDocente.lower() == otra["idDocente"].lower()
        mismoSalon = self.salon.idSalon.strip().lower() == otra["idSalon"].strip().lower()
        mismoParalelo = (
            self.carrera.nombre.lower() == otra["carrera"].lower()
            and self.nivel == otra["nivel"]
            and self.paralelo.letraParalelo.strip().lower() == otra["paralelo"].strip().lower()
        )
        return mismoDocente or mismoSalon or mismoParalelo

    def anadirDiccionario(self):
        return {
            "idClase": self.idClase,
            "carrera": self.carrera.nombre,
            "nivel": self.nivel,
            "periodo": self.periodo,
            "idAsignatura": self.asignatura.idAsignatura,
            "idDocente": self.docente.idDocente,
            "idSalon": self.salon.idSalon,
            "paralelo": self.paralelo.letraParalelo,
            "franjaHoraria": self.franjaHoraria.anadirDiccionario()
        }

    #Método: guardarMaterias

    def guardarMaterias(self, ruta=None):
        self.validarAsignacion()
        if ruta is None:
            ruta = Path(__file__).resolve().parent.parent / "datos" / "materias_horario.json"
        else:
            ruta = Path(ruta)
        registros = []
        if ruta.exists():
            with ruta.open(encoding="utf-8") as archivo:
                registros = json.load(archivo)
        if type(registros) != list:
            raise ValueError("El archivo de materias horario debe contener una lista.")

        for registro in registros:
            if self.idClase.lower() == registro["idClase"].lower():
                raise ValueError("El código de la clase ya está registrado.")
            if self.__hayChoqueConDatos(registro):
                raise ValueError("La clase choca con el docente, salón o paralelo de otra clase.")

        # También respeta las clases guardadas dentro de horarios completos.
        archivoHorarios = ruta.parent / "horarios_completos.json"
        if archivoHorarios.exists():
            with archivoHorarios.open(encoding="utf-8") as archivo:
                horarios = json.load(archivo)
            if type(horarios) != list:
                raise ValueError("El archivo de horarios completos debe contener una lista.")
            for horario in horarios:
                for materia in horario["materias"]:
                    if self.idClase.lower() == materia["idClase"].lower():
                        raise ValueError("El código de clase ya pertenece a un horario completo.")
                    if self.__hayChoqueConDatos(materia):
                        raise ValueError("La clase choca con una clase de un horario completo.")

        registros.append(self.anadirDiccionario())
        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta.with_name(ruta.name + ".tmp")
        try:
            with temporal.open("w", encoding="utf-8") as archivo:
                json.dump(registros, archivo, ensure_ascii=False, indent=4)
                archivo.write("\n")
            temporal.replace(ruta)
        finally:
            if temporal.exists():
                temporal.unlink()
