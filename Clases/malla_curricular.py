from asignatura import Asignatura


class MallaCurricular:
    def __init__(self):
        self.__niveles = {}

    @property
    def niveles(self):
        # Devolvemos una lista nueva con los números de nivel.
        return sorted(self.__niveles.keys())

    #Método: agregarAsignaturasNivel

    def agregarAsignaturasNivel(self, nivel, idAsignatura, nombreAsignatura,
                               horasSemanales, necesitaLaboratorio):
        if nivel <= 0:
            raise ValueError("El nivel debe ser mayor que cero.")
        # Asignatura se encarga de validar sus propios datos.
        nueva = Asignatura(idAsignatura, nombreAsignatura,
                           horasSemanales, necesitaLaboratorio)

        # Un código no puede repetirse dentro de la misma malla.
        for asignaturas in self.__niveles.values():
            for asignatura in asignaturas:
                if asignatura.idAsignatura.lower() == nueva.idAsignatura.lower():
                    raise ValueError("Ese código ya está registrado en esta malla.")

        # Composición: la malla conserva la asignatura creada.
        if nivel not in self.__niveles:
            self.__niveles[nivel] = []
        self.__niveles[nivel].append(nueva)

    #Método: consultarAsignaturasNivel

    def consultarAsignaturasNivel(self, nivel):
        # Una lista nueva evita que desde fuera se borren elementos de la malla.
        resultado = []
        if nivel in self.__niveles:
            for asignatura in self.__niveles[nivel]:
                resultado.append(asignatura)
        return resultado

    def anadirDiccionario(self):
        datos = {}
        for nivel in self.__niveles:
            asignaturas = []
            for asignatura in self.__niveles[nivel]:
                registro = asignatura.anadirDiccionario()
                asignaturas.append(registro)
            # JSON utiliza texto para las claves de un diccionario.
            datos[str(nivel)] = asignaturas
        return {"niveles": datos}

    @classmethod
    def desdeDiccionario(cls, datos):
        malla = cls()
        for nivel in datos["niveles"]:
            for asignatura in datos["niveles"][nivel]:
                malla.agregarAsignaturasNivel(
                    int(nivel),
                    asignatura["idAsignatura"],
                    asignatura["nombreAsignatura"],
                    asignatura["horasSemanales"],
                    asignatura["necesitaLaboratorio"]
                )
        return malla
