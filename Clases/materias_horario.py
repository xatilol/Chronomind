import json
from pathlib import Path


class MateriasHorario:
    def __init__(self, idClase, asignatura, docente, salon, paralelo, franjaHoraria, carrera, nivel, periodo):
        self.__idClase = idClase
        self.__asignatura = asignatura
        self.__docente = docente
        self.__salon = salon
        self.__paralelo = paralelo
        self.__franjaHoraria = franjaHoraria
        self.__carrera = carrera
        self.__nivel = nivel
        self.__periodo = periodo

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
        return self.paralelo.capacidadEstudiante <= self.salon.capacidad

    #Método: validarChoqueMaterias

    def validarChoqueMaterias(self, otraMateria):
        
        if self.periodo != otraMateria.periodo:
            return False
        return self.franjaHoraria.cruzaConOtroHorario(otraMateria.franjaHoraria)

    #Método: guardarMaterias

    def guardarMaterias(self):
        ruta = Path(__file__).resolve().parent.parent / "Datos" / "materias_horario.json"
        ruta.parent.mkdir(parents=True, exist_ok=True)

        registros = []
        if ruta.exists():
            with ruta.open("r", encoding="utf-8") as archivo:
                registros = json.load(archivo)

        datos = {
            "idClase": self.idClase,
            "carrera": self.carrera.nombre,
            "nivel": self.nivel,
            "periodo": self.periodo,
            "idAsignatura": self.asignatura.idAsignatura,
            "idDocente": self.docente.idDocente,
            "idSalon": self.salon.idSalon,
            "paralelo": self.paralelo.letraParalelo,
            "franjaHoraria": {
                "diaSemana": self.franjaHoraria.diaSemana,
                "horaInicio": self.franjaHoraria.horaInicio,
                "horaFin": self.franjaHoraria.horaFin,
                "jornada": self.franjaHoraria.jornada
            }
        }

        registros.append(datos)
        with ruta.open("w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=4)
