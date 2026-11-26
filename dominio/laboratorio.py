from dominio.salon import Salon


class Laboratorio(Salon):
    def __init__(self, idSalon, nombreSalon, capacidad, tiposEquipos, cantidadEquipos, disponible=True):
        super().__init__(idSalon, nombreSalon, capacidad, disponible)
        self.tiposEquipos = tiposEquipos
        self.cantidadEquipos = cantidadEquipos

    @property
    def tiposEquipos(self):
        return self.__tiposEquipos.copy()

    @tiposEquipos.setter
    def tiposEquipos(self, valores):
        if type(valores) != list or len(valores) == 0:
            raise ValueError("Ingrese al menos un tipo de equipo.")
        tipos = []
        for valor in valores:
            if type(valor) != str or valor.strip() == "":
                raise ValueError("Los tipos de equipos deben ser textos no vacíos.")
            nombre = valor.strip()
            if nombre.lower() in [t.lower() for t in tipos]:
                raise ValueError("No repita un tipo de equipo en la lista.")
            tipos.append(nombre)
        self.__tiposEquipos = tipos

    @property
    def cantidadEquipos(self):
        return self.__cantidadEquipos

    @cantidadEquipos.setter
    def cantidadEquipos(self, valor):
        if type(valor) != int or valor < 0:
            raise ValueError("La cantidad de equipos debe ser un entero igual o mayor que cero.")
        self.__cantidadEquipos = valor

    @property
    def tipo(self):
        return "laboratorio"

    # Método: ComprobarCuentaEquipos
    def ComprobarCuentaEquipos(self, cantidadRequerida):
        if type(cantidadRequerida) != int or cantidadRequerida <= 0:
            raise ValueError("La cantidad requerida debe ser un entero positivo.")
        return cantidadRequerida <= self.__cantidadEquipos

    def cumpleEquipos(self, cantidad, tipoEquipo=None):
        if tipoEquipo and tipoEquipo.strip().lower() not in [t.lower() for t in self.__tiposEquipos]:
            return False
        return self.ComprobarCuentaEquipos(cantidad)

    def obtenerDescripcion(self):
        return (f"Laboratorio {self.nombreSalon} (capacidad {self.capacidad}, "
                f"{self.cantidadEquipos} equipos: {', '.join(self.__tiposEquipos)})")

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["tiposEquipos"] = self.tiposEquipos
        datos["cantidadEquipos"] = self.cantidadEquipos
        return datos
