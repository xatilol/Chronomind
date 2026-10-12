"""Menú inicial de Chronomind v1. Ejecutar este archivo."""

import json
from pathlib import Path

from carrera import Carrera
from docente import Docente
from salon import Salon
from laboratorio import Laboratorio
from franja_horaria import FranjaHoraria
from paralelo import Paralelo
from materias_horario import MateriasHorario

# La ruta funciona aunque el programa se ejecute desde otra carpeta.
CARPETA_DATOS = Path(__file__).resolve().parent.parent / "datos"

CLASES = [
    "Carrera", "Malla Curricular", "Asignatura", "Docente", "Salón",
    "Laboratorio", "Paralelo", "Franja Horaria", "Materias Horario",
    "Horario Completo", "Gestor Académico"
]


def seleccionar(titulo, opciones):
    """Muestra una lista y devuelve el índice elegido, o None para volver."""
    while True:
        print("\n" + titulo)
        for numero, opcion in enumerate(opciones, start=1):
            print(f"{numero}. {opcion}")
        print("0. Volver / salir")
        entrada = input("Seleccione una opción: ").strip()
        try:
            numero = int(entrada)
        except ValueError:
            print("Ingrese un número de la lista.")
            continue
        if numero == 0:
            return None
        if 1 <= numero <= len(opciones):
            return numero - 1
        print("Opción fuera de rango.")


def cargar_carreras():
    """Lee registros JSON y reconstruye objetos Carrera."""
    ruta = CARPETA_DATOS / "carreras.json"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if not isinstance(registros, list):
        raise ValueError("carreras.json debe contener una lista.")
    carreras = []
    for registro in registros:
        carrera = Carrera.desdeDiccionario(registro)
        carreras.append(carrera)
    return carreras


def guardar_carreras(carreras):
    """Escribe primero un temporal para proteger el archivo anterior."""
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / "carreras.json"
    temporal = CARPETA_DATOS / "carreras.json.tmp"
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            registros = []
            for carrera in carreras:
                datos = carrera.anadirDiccionario()
                registros.append(datos)
            json.dump(registros, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def registrar_carrera():
    try:
        carreras = cargar_carreras()
    except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
        print(f"No se pudieron cargar las carreras: {error}")
        print("Revise el archivo antes de registrar una nueva carrera.")
        return

    while True:
        nombre = input("Nombre de la carrera (0 para volver): ").strip()
        if nombre == "0":
            return
        try:
            nueva = Carrera(nombre)
        except ValueError as error:
            print(error)
            continue
        repetida = False
        for carrera in carreras:
            if carrera.nombre.lower() == nueva.nombre.lower():
                repetida = True

        if repetida:
            print("Esa carrera ya está registrada.")
            continue
        try:
            guardar_carreras(carreras + [nueva])
        except (OSError, UnicodeError) as error:
            print(f"No se pudo guardar la carrera: {error}")
            return
        print(f"Carrera registrada: {nueva.nombre}.")
        return


def gestionar_malla():
    try:
        carreras = cargar_carreras()
    except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
        print(f"No se pudieron cargar las carreras: {error}")
        return

    if not carreras:
        print("Primero registre una carrera.")
        return
    nombres = []
    for carrera in carreras:
        nombres.append(carrera.nombre)
    indice = seleccionar("Seleccione la carrera de la malla", nombres)
    if indice is None:
        return
    carrera = carreras[indice]
    malla = carrera.mostrarMallaCurricular()

    while True:
        opcion = seleccionar(
            "Malla de " + carrera.nombre,
            ["Añadir asignatura a un nivel", "Consultar asignaturas de un nivel"]
        )
        if opcion is None:
            return
        try:
            nivel = int(input("Ingrese el nivel (0 para volver): "))
            if nivel == 0:
                continue
            if nivel < 0:
                raise ValueError("El nivel debe ser mayor que cero.")
            if opcion == 0:
                codigo = input("Código de la asignatura: ")
                nombre = input("Nombre de la asignatura: ")
                horas = int(input("Horas semanales: "))
                respuesta = input("¿Necesita laboratorio? (s/n): ").strip().lower()
                if respuesta != "s" and respuesta != "n":
                    raise ValueError("Escriba s para sí o n para no.")
                necesitaLaboratorio = respuesta == "s"
                malla.agregarAsignaturasNivel(
                    nivel, codigo, nombre, horas, necesitaLaboratorio
                )
                try:
                    guardar_carreras(carreras)
                except (OSError, UnicodeError) as error:
                    print(f"No se guardó el cambio: {error}")
                    # Salimos para descartar el cambio que solo está en memoria.
                    return
                print("Asignatura añadida y malla guardada.")
            else:
                asignaturas = malla.consultarAsignaturasNivel(nivel)
                if not asignaturas:
                    print("No hay asignaturas registradas en ese nivel.")
                for asignatura in asignaturas:
                    print(asignatura.verInformacionAsignatura())
        except ValueError as error:
            print(f"Revise los datos: {error}")


def cargar_docentes(carreras):
    ruta = CARPETA_DATOS / "docentes.json"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if not isinstance(registros, list):
        raise ValueError("docentes.json debe contener una lista.")
    docentes = []
    for registro in registros:
        docentes.append(Docente.desdeDiccionario(registro, carreras))
    return docentes


def guardar_docentes(docentes):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / "docentes.json"
    temporal = CARPETA_DATOS / "docentes.json.tmp"
    registros = []
    for docente in docentes:
        registros.append(docente.anadirDiccionario())
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def elegir_asignatura_docente(docente, carreras):
    nombres = []
    for carrera in carreras:
        nombres.append(carrera.nombre)
    if not nombres:
        print("Primero registre carreras y asignaturas.")
        return False
    indice = seleccionar("Seleccione la carrera", nombres)
    if indice is None:
        return False
    carrera = carreras[indice]
    malla = carrera.mostrarMallaCurricular()
    niveles = malla.niveles
    if not niveles:
        print("Esta carrera todavía no tiene asignaturas.")
        return False
    opciones = []
    for nivel in niveles:
        opciones.append("Nivel " + str(nivel))
    indice = seleccionar("Seleccione el nivel", opciones)
    if indice is None:
        return False
    asignaturas = malla.consultarAsignaturasNivel(niveles[indice])
    opciones = []
    for asignatura in asignaturas:
        opciones.append(asignatura.idAsignatura + " - " + asignatura.nombreAsignatura)
    indice = seleccionar("Seleccione la asignatura", opciones)
    if indice is None:
        return False
    docente.vincularAsignatura(carrera, asignaturas[indice])
    return True


def mostrar_docente(docente):
    print(f"\nCódigo: {docente.idDocente}")
    print(f"Nombre: {docente.nombreDocente}")
    print(f"Horas acumuladas: {docente.horas}")
    print("Asignaturas que puede impartir:")
    if not docente.asignaturasImparte:
        print("Todavía no tiene asignaturas vinculadas.")
    for registro in docente.asignaturasImparte:
        print(registro["carrera"].nombre + " - " + registro["asignatura"].nombreAsignatura)
    print("Disponibilidad:")
    if not docente.disponibilidad:
        print("Todavía no tiene disponibilidad registrada.")
    for bloque in docente.disponibilidad:
        print(f"{bloque['dia']}: {bloque['horaInicio']}:00 a {bloque['horaFin']}:00")


def gestionar_docentes():
    while True:
        # Se vuelve a cargar en cada vuelta: un fallo al guardar no deja cambios pendientes.
        try:
            carreras = cargar_carreras()
            docentes = cargar_docentes(carreras)
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
            print(f"No se pudieron cargar los datos: {error}")
            return
        opcion = seleccionar("Docentes", [
            "Registrar docente", "Vincular asignatura", "Registrar disponibilidad",
            "Comprobar disponibilidad", "Acumular horas dadas", "Consultar docente"
        ])
        if opcion is None:
            return
        try:
            if opcion == 0:
                codigo = input("Código del docente (0 para volver): ").strip()
                if codigo == "0":
                    continue
                repetido = False
                for docente in docentes:
                    if docente.idDocente.lower() == codigo.lower():
                        repetido = True
                if repetido:
                    print("Ese código de docente ya está registrado.")
                    continue
                nombre = input("Nombre del docente: ")
                docentes.append(Docente(codigo, nombre))
                guardar_docentes(docentes)
                print("Docente guardado.")
                continue

            if not docentes:
                print("Primero registre un docente.")
                continue
            opciones = []
            for docente in docentes:
                opciones.append(docente.idDocente + " - " + docente.nombreDocente)
            indice = seleccionar("Seleccione el docente", opciones)
            if indice is None:
                continue
            docente = docentes[indice]
            cambio = False

            if opcion == 1:
                cambio = elegir_asignatura_docente(docente, carreras)
            elif opcion == 2 or opcion == 3:
                indice_dia = seleccionar("Seleccione el día", Docente.DIAS_LABORABLES)
                if indice_dia is None:
                    continue
                dia = Docente.DIAS_LABORABLES[indice_dia]
                inicio = int(input("Hora de inicio, entera (por ejemplo 7): "))
                fin = int(input("Hora de fin, entera (por ejemplo 11): "))
                if opcion == 2:
                    docente.registrarDisponibilidad(dia, inicio, fin)
                    cambio = True
                elif docente.comprobarDisponibilidad(dia, inicio, fin):
                    print("El intervalo está dentro de su disponibilidad registrada.")
                else:
                    print("El intervalo no está completamente disponible.")
            elif opcion == 4:
                cantidad = int(input("Cantidad de horas que desea sumar: "))
                docente.acumularHorasDadas(cantidad)
                cambio = True
            elif opcion == 5:
                mostrar_docente(docente)

            if cambio:
                guardar_docentes(docentes)
                print("Datos del docente guardados.")
        except ValueError as error:
            print(f"Revise los datos: {error}")
        except (OSError, UnicodeError) as error:
            print(f"No se pudo guardar el cambio: {error}")


def cargar_salones():
    ruta = CARPETA_DATOS / "salones.json"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if type(registros) != list:
        raise ValueError("salones.json debe contener una lista.")
    salones = []
    for registro in registros:
        salones.append(Salon.desdeDiccionario(registro))
    return salones


def guardar_salones(salones):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / "salones.json"
    temporal = CARPETA_DATOS / "salones.json.tmp"
    registros = []
    for salon in salones:
        registros.append(salon.anadirDiccionario())
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def gestionar_salones():
    while True:
        try:
            salones = cargar_salones()
            laboratorios = cargar_laboratorios()
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
            print(f"No se pudieron cargar los salones: {error}")
            return

        opcion = seleccionar("Salones", [
            "Registrar salón", "Consultar salones", "Comprobar capacidad"
        ])
        if opcion is None:
            return
        try:
            if opcion == 0:
                codigo = input("Código del salón (0 para volver): ").strip()
                if codigo == "0":
                    continue
                if codigo_espacio_registrado(codigo, salones, laboratorios):
                    print("Ese código ya está registrado en un salón o laboratorio.")
                    continue
                nombre = input("Nombre del salón: ")
                capacidad = int(input("Capacidad máxima de estudiantes: "))
                respuesta = input("¿Está habilitado para uso? (s/n): ").strip().lower()
                if respuesta != "s" and respuesta != "n":
                    raise ValueError("Escriba s para sí o n para no.")
                disponible = respuesta == "s"
                salon = Salon(codigo, nombre, capacidad, disponible)
                salones.append(salon)
                guardar_salones(salones)
                print("Salón guardado.")
            elif not salones:
                print("Todavía no hay salones registrados.")
            elif opcion == 1:
                for salon in salones:
                    estado = "No habilitado"
                    if salon.estaDisponible():
                        estado = "Habilitado"
                    print(f"{salon.idSalon} - {salon.nombreSalon}")
                    print(f"Capacidad: {salon.capacidad} estudiantes. Estado: {estado}.")
            elif opcion == 2:
                opciones = []
                for salon in salones:
                    opciones.append(salon.idSalon + " - " + salon.nombreSalon)
                indice = seleccionar("Seleccione el salón", opciones)
                if indice is None:
                    continue
                cantidad = int(input("Cantidad de estudiantes del grupo: "))
                salon = salones[indice]
                if salon.validarCapacidad(cantidad):
                    print("El salón tiene capacidad suficiente.")
                else:
                    print("El salón no tiene capacidad suficiente.")
                if not salon.estaDisponible():
                    print("Además, este salón no está habilitado para uso.")
        except ValueError as error:
            print(f"Revise los datos: {error}")
        except (OSError, UnicodeError) as error:
            print(f"No se pudo guardar el salón: {error}")


def cargar_laboratorios():
    ruta = CARPETA_DATOS / "laboratorios.json"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if type(registros) != list:
        raise ValueError("laboratorios.json debe contener una lista.")
    laboratorios = []
    for registro in registros:
        laboratorios.append(Laboratorio.desdeDiccionario(registro))
    return laboratorios


def guardar_laboratorios(laboratorios):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / "laboratorios.json"
    temporal = CARPETA_DATOS / "laboratorios.json.tmp"
    registros = []
    for laboratorio in laboratorios:
        registros.append(laboratorio.anadirDiccionario())
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def codigo_espacio_registrado(codigo, salones, laboratorios):
    for salon in salones:
        if salon.idSalon.lower() == codigo.strip().lower():
            return True
    for laboratorio in laboratorios:
        if laboratorio.idSalon.lower() == codigo.strip().lower():
            return True
    return False


def gestionar_laboratorios():
    while True:
        try:
            laboratorios = cargar_laboratorios()
            salones = cargar_salones()
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
            print(f"No se pudieron cargar los espacios: {error}")
            return

        opcion = seleccionar("Laboratorios", [
            "Registrar laboratorio", "Consultar laboratorios",
            "Comprobar capacidad de estudiantes", "Comprobar cantidad de equipos"
        ])
        if opcion is None:
            return
        try:
            if opcion == 0:
                codigo = input("Código del laboratorio (0 para volver): ").strip()
                if codigo == "0":
                    continue
                if codigo_espacio_registrado(codigo, salones, laboratorios):
                    print("Ese código ya está registrado en un salón o laboratorio.")
                    continue
                nombre = input("Nombre del laboratorio: ")
                capacidad = int(input("Capacidad máxima de estudiantes: "))
                entrada = input("Tipos de equipos separados por coma: ")
                tipos = entrada.split(",")
                cantidad = int(input("Cantidad total de equipos: "))
                respuesta = input("¿Está habilitado para uso? (s/n): ").strip().lower()
                if respuesta != "s" and respuesta != "n":
                    raise ValueError("Escriba s para sí o n para no.")
                laboratorio = Laboratorio(
                    codigo, nombre, capacidad, tipos, cantidad, respuesta == "s"
                )
                laboratorios.append(laboratorio)
                guardar_laboratorios(laboratorios)
                print("Laboratorio guardado.")
            elif not laboratorios:
                print("Todavía no hay laboratorios registrados.")
            elif opcion == 1:
                for laboratorio in laboratorios:
                    print(f"{laboratorio.idSalon} - {laboratorio.nombreSalon}")
                    print(f"Capacidad: {laboratorio.capacidad} estudiantes.")
                    print("Tipos de equipos:")
                    for tipo in laboratorio.tiposEquipos:
                        print("- " + tipo)
                    print(f"Cantidad total de equipos: {laboratorio.cantidadEquipos}")
                    if laboratorio.estaDisponible():
                        print("Estado: habilitado.")
                    else:
                        print("Estado: no habilitado.")
            else:
                opciones = []
                for laboratorio in laboratorios:
                    opciones.append(laboratorio.idSalon + " - " + laboratorio.nombreSalon)
                indice = seleccionar("Seleccione el laboratorio", opciones)
                if indice is None:
                    continue
                laboratorio = laboratorios[indice]
                if opcion == 2:
                    cantidad = int(input("Cantidad de estudiantes del grupo: "))
                    if laboratorio.validarCapacidad(cantidad):
                        print("El grupo cabe en el laboratorio.")
                    else:
                        print("La capacidad del laboratorio es insuficiente.")
                elif opcion == 3:
                    cantidad = int(input("Cantidad de equipos que se necesitan: "))
                    if laboratorio.ComprobarCuentaEquipos(cantidad):
                        print("Hay suficientes equipos en total.")
                    else:
                        print("No hay suficientes equipos en total.")
                if not laboratorio.estaDisponible():
                    print("Además, el laboratorio no está habilitado para uso.")
        except ValueError as error:
            print(f"Revise los datos: {error}")
        except (OSError, UnicodeError) as error:
            print(f"No se pudo guardar el laboratorio: {error}")


def cargar_franjas():
    ruta = CARPETA_DATOS / "franjas_horarias.json"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if type(registros) != list:
        raise ValueError("franjas_horarias.json debe contener una lista.")
    franjas = []
    for registro in registros:
        franjas.append(FranjaHoraria.desdeDiccionario(registro))
    return franjas


def guardar_franjas(franjas):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / "franjas_horarias.json"
    temporal = CARPETA_DATOS / "franjas_horarias.json.tmp"
    registros = []
    for franja in franjas:
        registros.append(franja.anadirDiccionario())
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def gestionar_franjas():
    while True:
        try:
            franjas = cargar_franjas()
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
            print(f"No se pudieron cargar las franjas: {error}")
            return
        opcion = seleccionar("Franjas horarias", [
            "Registrar franja", "Consultar franjas", "Comparar dos franjas"
        ])
        if opcion is None:
            return
        try:
            if opcion == 0:
                indice = seleccionar("Seleccione el día", FranjaHoraria.DIAS_LABORABLES)
                if indice is None:
                    continue
                dia = FranjaHoraria.DIAS_LABORABLES[indice]
                inicio = int(input("Hora de inicio, entera (7 a 19): "))
                fin = int(input("Hora de fin, entera (8 a 20): "))
                jornada = input("Nombre de la jornada (por ejemplo Matutina): ")
                nueva = FranjaHoraria(dia, inicio, fin, jornada)
                repetida = False
                for franja in franjas:
                    if (franja.diaSemana == nueva.diaSemana
                            and franja.horaInicio == nueva.horaInicio
                            and franja.horaFin == nueva.horaFin):
                        repetida = True
                if repetida:
                    print("Ya existe una franja con ese día y esas horas.")
                    continue
                franjas.append(nueva)
                guardar_franjas(franjas)
                print("Franja guardada: " + nueva.generarBloqueHorario())
            elif not franjas:
                print("Todavía no hay franjas registradas.")
            elif opcion == 1:
                for franja in franjas:
                    print(franja.generarBloqueHorario())
            elif opcion == 2:
                if len(franjas) < 2:
                    print("Registre al menos dos franjas para compararlas.")
                    continue
                opciones = []
                for franja in franjas:
                    opciones.append(franja.generarBloqueHorario())
                primera = seleccionar("Seleccione la primera franja", opciones)
                if primera is None:
                    continue
                segunda = seleccionar("Seleccione la segunda franja", opciones)
                if segunda is None:
                    continue
                if primera == segunda:
                    print("Seleccione dos franjas distintas.")
                    continue
                if franjas[primera].cruzaConOtroHorario(franjas[segunda]):
                    print("Las franjas se superponen.")
                else:
                    print("Las franjas no se superponen.")
        except ValueError as error:
            print(f"Revise los datos: {error}")
        except (OSError, UnicodeError) as error:
            print(f"No se pudo guardar la franja: {error}")


def cargar_paralelos():
    ruta = CARPETA_DATOS / "paralelos.json"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    if type(datos) != list:
        raise ValueError("paralelos.json debe contener una lista.")
    registros = []
    for dato in datos:
        if type(dato["carrera"]) != str or dato["carrera"].strip() == "":
            raise ValueError("Cada paralelo debe indicar su carrera.")
        if type(dato["nivel"]) != int or dato["nivel"] <= 0:
            raise ValueError("Cada paralelo debe indicar un nivel entero positivo.")
        if type(dato["periodo"]) != str or dato["periodo"].strip() == "":
            raise ValueError("Cada paralelo debe indicar su período.")
        registros.append({
            "carrera": dato["carrera"],
            "nivel": dato["nivel"],
            "periodo": dato["periodo"].strip(),
            "paralelo": Paralelo.desdeDiccionario(dato)
        })
    return registros


def guardar_paralelos(registros):
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / "paralelos.json"
    temporal = CARPETA_DATOS / "paralelos.json.tmp"
    datos = []
    for registro in registros:
        dato = registro["paralelo"].anadirDiccionario()
        dato["carrera"] = registro["carrera"]
        dato["nivel"] = registro["nivel"]
        dato["periodo"] = registro["periodo"]
        datos.append(dato)
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def gestionar_paralelos():
    while True:
        try:
            registros = cargar_paralelos()
            carreras = cargar_carreras()
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
            print(f"No se pudieron cargar los datos: {error}")
            return
        opcion = seleccionar("Paralelos", [
            "Registrar paralelo", "Consultar paralelos", "Comprobar límite de estudiantes"
        ])
        if opcion is None:
            return
        try:
            if opcion == 0:
                if not carreras:
                    print("Primero registre una carrera y su malla.")
                    continue
                opciones = []
                for carrera in carreras:
                    opciones.append(carrera.nombre)
                indice = seleccionar("Seleccione la carrera", opciones)
                if indice is None:
                    continue
                carrera = carreras[indice]
                niveles = carrera.mostrarMallaCurricular().niveles
                if not niveles:
                    print("Primero registre asignaturas por nivel en la malla de esta carrera.")
                    continue
                opciones = []
                for nivel in niveles:
                    opciones.append("Nivel " + str(nivel))
                indice = seleccionar("Seleccione el nivel", opciones)
                if indice is None:
                    continue
                nivel = niveles[indice]
                periodo = input("Período académico (por ejemplo 2026-2; 0 para volver): ").strip()
                if periodo == "0":
                    continue
                if periodo == "":
                    raise ValueError("El período no puede estar vacío.")
                letra = input("Letra o identificador del paralelo: ")
                capacidad = int(input("Capacidad máxima de estudiantes del paralelo: "))
                paralelo = Paralelo(letra, capacidad)
                repetido = False
                for registro in registros:
                    if (registro["carrera"].lower() == carrera.nombre.lower()
                            and registro["nivel"] == nivel
                            and registro["periodo"].lower() == periodo.lower()
                            and registro["paralelo"].letraParalelo == paralelo.letraParalelo):
                        repetido = True
                if repetido:
                    print("Ese paralelo ya existe en esa carrera, nivel y período.")
                    continue
                registros.append({
                    "carrera": carrera.nombre, "nivel": nivel,
                    "periodo": periodo, "paralelo": paralelo
                })
                guardar_paralelos(registros)
                print("Paralelo guardado.")
            elif not registros:
                print("Todavía no hay paralelos registrados.")
            elif opcion == 1:
                for registro in registros:
                    paralelo = registro["paralelo"]
                    print(f"{registro['carrera']} | Nivel {registro['nivel']} | {registro['periodo']}")
                    print(f"Paralelo {paralelo.letraParalelo}: cupo de {paralelo.capacidadEstudiante} estudiantes.")
            elif opcion == 2:
                opciones = []
                for registro in registros:
                    opciones.append(
                        f"{registro['carrera']} | Nivel {registro['nivel']} | "
                        f"{registro['periodo']} | Paralelo {registro['paralelo'].letraParalelo}"
                    )
                indice = seleccionar("Seleccione el paralelo", opciones)
                if indice is None:
                    continue
                cantidad = int(input("Cantidad de estudiantes que desea comprobar: "))
                if registros[indice]["paralelo"].validarLimiteEstudiantes(cantidad):
                    print("La cantidad está dentro del cupo del paralelo.")
                else:
                    print("La cantidad supera el cupo del paralelo.")
        except ValueError as error:
            print(f"Revise los datos: {error}")
        except (OSError, UnicodeError) as error:
            print(f"No se pudo guardar el paralelo: {error}")


def cargar_contexto_horarios():
    carreras = cargar_carreras()
    return {
        "carreras": carreras,
        "docentes": cargar_docentes(carreras),
        "espacios": cargar_salones() + cargar_laboratorios(),
        "paralelos": cargar_paralelos(),
        "franjas": cargar_franjas()
    }


def buscar_carrera_horario(nombre, contexto):
    for carrera in contexto["carreras"]:
        if carrera.nombre == nombre:
            return carrera
    raise ValueError("La carrera del horario ya no está registrada.")


def buscar_paralelo_horario(datos, contexto):
    for registro in contexto["paralelos"]:
        if (registro["carrera"] == datos["carrera"]
                and registro["nivel"] == datos["nivel"]
                and registro["periodo"].lower() == datos["periodo"].lower()
                and registro["paralelo"].letraParalelo == datos["paralelo"]):
            return registro["paralelo"]
    raise ValueError("El paralelo del horario ya no está registrado en ese contexto.")


def recuperar_materia(datos, contexto):
    carrera = buscar_carrera_horario(datos["carrera"], contexto)
    paralelo = buscar_paralelo_horario(datos, contexto)
    asignatura = None
    for candidata in carrera.mostrarMallaCurricular().consultarAsignaturasNivel(datos["nivel"]):
        if candidata.idAsignatura == datos["idAsignatura"]:
            asignatura = candidata
    docente = None
    for candidato in contexto["docentes"]:
        if candidato.idDocente == datos["idDocente"]:
            docente = candidato
    salon = None
    for espacio in contexto["espacios"]:
        if espacio.idSalon == datos["idSalon"]:
            salon = espacio
    if asignatura is None or docente is None or salon is None:
        raise ValueError("Una clase hace referencia a una asignatura, docente o espacio inexistente.")
    franja = FranjaHoraria.desdeDiccionario(datos["franjaHoraria"])
    return MateriasHorario(
        datos["idClase"], asignatura, docente, salon, paralelo, franja,
        carrera, datos["nivel"], datos["periodo"]
    )


def comprobar_materias_sueltas(horarios, contexto):
    # Compatibilidad: las clases guardadas antes por guardarMaterias también reservan recursos.
    ruta = CARPETA_DATOS / "materias_horario.json"
    if not ruta.exists():
        return
    with ruta.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if type(registros) != list:
        raise ValueError("materias_horario.json debe contener una lista.")
    for registro in registros:
        suelta = recuperar_materia(registro, contexto)
        for horario in horarios:
            for materia in horario.materias:
                if (materia.idClase.lower() == suelta.idClase.lower()
                        or materia.validarChoqueMaterias(suelta)):
                    raise ValueError("Una clase coincide o choca con un registro de materias_horario.json.")


def cargar_horarios(contexto):
    ruta = CARPETA_DATOS / "horarios_completos.json"
    if not ruta.exists():
        return []
    with ruta.open(encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if type(registros) != list:
        raise ValueError("horarios_completos.json debe contener una lista.")
    horarios = []
    for datos in registros:
        carrera = buscar_carrera_horario(datos["carrera"], contexto)
        paralelo = buscar_paralelo_horario(datos, contexto)
        horario = paralelo.asignarParHorario(
            datos["idHorario"], datos["periodo"], datos["nivel"], carrera
        )
        comprobar_horario_repetido(horario, horarios)
        if type(datos["materias"]) != list:
            raise ValueError("Las materias de un horario deben ser una lista.")
        for registro in datos["materias"]:
            if (registro["carrera"] != datos["carrera"]
                    or registro["nivel"] != datos["nivel"]
                    or registro["periodo"] != datos["periodo"]
                    or registro["paralelo"] != datos["paralelo"]):
                raise ValueError("Una clase tiene un contexto distinto al de su horario.")
            materia = recuperar_materia(registro, contexto)
            horario.agregarMateria(
                materia.idClase, materia.asignatura, materia.docente,
                materia.salon, materia.franjaHoraria, horarios
            )
        horarios.append(horario)
    comprobar_materias_sueltas(horarios, contexto)
    return horarios


def comprobar_horario_repetido(nuevo, horarios):
    for horario in horarios:
        if horario.idHorario.lower() == nuevo.idHorario.lower():
            raise ValueError("Ese código de horario ya está registrado.")
        if (horario.carrera.nombre == nuevo.carrera.nombre
                and horario.nivel == nuevo.nivel
                and horario.periodo.lower() == nuevo.periodo.lower()
                and horario.paralelo.letraParalelo == nuevo.paralelo.letraParalelo):
            raise ValueError("Ya existe un horario para esa carrera, nivel, período y paralelo.")


def guardar_horarios(horarios, contexto):
    comprobar_materias_sueltas(horarios, contexto)
    CARPETA_DATOS.mkdir(parents=True, exist_ok=True)
    ruta = CARPETA_DATOS / "horarios_completos.json"
    temporal = CARPETA_DATOS / "horarios_completos.json.tmp"
    registros = []
    for horario in horarios:
        registros.append(horario.anadirDiccionario())
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(registros, archivo, ensure_ascii=False, indent=4)
            archivo.write("\n")
        temporal.replace(ruta)
    finally:
        if temporal.exists():
            temporal.unlink()


def elegir_horario(horarios):
    opciones = []
    for horario in horarios:
        opciones.append(
            f"{horario.idHorario} | {horario.carrera.nombre} | Nivel {horario.nivel} | "
            f"{horario.periodo} | Paralelo {horario.paralelo.letraParalelo}"
        )
    return seleccionar("Seleccione el horario", opciones)


def agregar_clase_menu(horario, horarios, contexto):
    asignaturas = horario.carrera.mostrarMallaCurricular().consultarAsignaturasNivel(horario.nivel)
    opciones = []
    for asignatura in asignaturas:
        opciones.append(asignatura.idAsignatura + " - " + asignatura.nombreAsignatura)
    indice = seleccionar("Seleccione la asignatura", opciones)
    if indice is None:
        return False
    asignatura = asignaturas[indice]
    docentes = []
    opciones = []
    for docente in contexto["docentes"]:
        for registro in docente.asignaturasImparte:
            if (registro["carrera"].nombre == horario.carrera.nombre
                    and registro["asignatura"].idAsignatura == asignatura.idAsignatura):
                docentes.append(docente)
                opciones.append(docente.idDocente + " - " + docente.nombreDocente)
    if not docentes:
        print("Primero vincule esta asignatura a un docente y registre su disponibilidad.")
        return False
    indice = seleccionar("Seleccione el docente", opciones)
    if indice is None:
        return False
    docente = docentes[indice]
    espacios = contexto["espacios"]
    if not espacios or not contexto["franjas"]:
        print("Primero registre espacios y franjas horarias.")
        return False
    opciones = []
    for espacio in espacios:
        opciones.append(espacio.idSalon + " - " + espacio.nombreSalon)
    indice = seleccionar("Seleccione el salón o laboratorio", opciones)
    if indice is None:
        return False
    salon = espacios[indice]
    opciones = []
    for franja in contexto["franjas"]:
        opciones.append(franja.generarBloqueHorario())
    indice = seleccionar("Seleccione la franja", opciones)
    if indice is None:
        return False
    franja = contexto["franjas"][indice]
    codigo = input("Código único de la clase (0 para volver): ").strip()
    if codigo == "0":
        return False
    horario.agregarMateria(codigo, asignatura, docente, salon, franja, horarios)
    return True


def gestionar_horarios():
    while True:
        try:
            contexto = cargar_contexto_horarios()
            horarios = cargar_horarios(contexto)
        except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
            print(f"No se pudieron cargar los horarios y sus recursos: {error}")
            return
        opcion = seleccionar("Horarios", [
            "Crear horario vacío", "Añadir clase", "Quitar clase", "Consultar horario"
        ])
        if opcion is None:
            return
        try:
            if opcion == 0:
                registros = contexto["paralelos"]
                if not registros:
                    print("Primero registre un paralelo con su carrera, nivel y período.")
                    continue
                opciones = []
                for registro in registros:
                    opciones.append(
                        f"{registro['carrera']} | Nivel {registro['nivel']} | "
                        f"{registro['periodo']} | Paralelo {registro['paralelo'].letraParalelo}"
                    )
                indice = seleccionar("Seleccione el paralelo y su contexto", opciones)
                if indice is None:
                    continue
                registro = registros[indice]
                codigo = input("Código del horario (0 para volver): ").strip()
                if codigo == "0":
                    continue
                carrera = buscar_carrera_horario(registro["carrera"], contexto)
                nuevo = registro["paralelo"].asignarParHorario(
                    codigo, registro["periodo"], registro["nivel"], carrera
                )
                comprobar_horario_repetido(nuevo, horarios)
                horarios.append(nuevo)
                guardar_horarios(horarios, contexto)
                print("Horario vacío guardado. Ya puede añadir clases.")
                continue
            if not horarios:
                print("Primero cree un horario.")
                continue
            indice = elegir_horario(horarios)
            if indice is None:
                continue
            horario = horarios[indice]
            if opcion == 1:
                if agregar_clase_menu(horario, horarios, contexto):
                    guardar_horarios(horarios, contexto)
                    print("Clase añadida y horario guardado.")
            elif opcion == 2:
                materias = horario.materias
                if not materias:
                    print("Este horario todavía no tiene clases.")
                    continue
                opciones = []
                for materia in materias:
                    opciones.append(
                        materia.idClase + " - " + materia.asignatura.nombreAsignatura
                        + " | " + materia.franjaHoraria.generarBloqueHorario()
                    )
                indice = seleccionar("Seleccione la clase que desea quitar", opciones)
                if indice is None:
                    continue
                horario.quitarMateria(materias[indice].idClase)
                guardar_horarios(horarios, contexto)
                print("Clase retirada del horario.")
            elif opcion == 3:
                print(horario.verHorarioCompleto())
        except ValueError as error:
            print(f"No se realizó el cambio: {error}")
        except (OSError, UnicodeError) as error:
            print(f"No se pudo guardar el cambio: {error}")


def menu_anadir_datos():
    indice = seleccionar("¿En qué clase desea añadir datos?", CLASES)
    if indice == 0:
        registrar_carrera()
    elif indice == 1 or indice == 2:
        # Las asignaturas siempre se registran en la malla de una carrera.
        gestionar_malla()
    elif indice == 3:
        gestionar_docentes()
    elif indice == 4:
        gestionar_salones()
    elif indice == 5:
        gestionar_laboratorios()
    elif indice == 6:
        gestionar_paralelos()
    elif indice == 7:
        gestionar_franjas()
    elif indice == 8 or indice == 9:
        gestionar_horarios()
    elif indice is not None:
        print(f"Clase seleccionada: {CLASES[indice]}.")
        print("El registro de esta clase se implementará más adelante.")


def menu_mostrar_horarios():
    try:
        contexto = cargar_contexto_horarios()
        horarios = cargar_horarios(contexto)
    except (OSError, ValueError, UnicodeError, KeyError, TypeError, AttributeError) as error:
        print(f"No se pudieron cargar los horarios: {error}")
        return
    if not horarios:
        print("Todavía no hay horarios creados.")
        return
    carreras = contexto["carreras"]
    nombres = []
    for carrera in carreras:
        nombres.append(carrera.nombre)
    indice = seleccionar("Primero, seleccione la carrera", nombres)
    if indice is None:
        return
    carrera = carreras[indice]
    niveles = carrera.mostrarMallaCurricular().niveles
    if not niveles:
        print("Esta carrera todavía no tiene niveles registrados.")
        return
    opciones = []
    for nivel in niveles:
        opciones.append("Nivel " + str(nivel))
    indice = seleccionar("Seleccione el nivel", opciones)
    if indice is None:
        return
    nivel = niveles[indice]
    seleccionados = []
    for horario in horarios:
        if horario.carrera.nombre == carrera.nombre and horario.nivel == nivel:
            seleccionados.append(horario)
    if not seleccionados:
        print("No hay horarios para esa carrera y nivel.")
        return
    indice = elegir_horario(seleccionados)
    if indice is not None:
        print(seleccionados[indice].verHorarioCompleto())


def main():
    while True:
        opcion = seleccionar("CHRONOMIND v1", ["Añadir datos", "Mostrar horarios creados"])
        if opcion is None:
            print("Hasta pronto.")
            break
        if opcion == 0:
            menu_anadir_datos()
        else:
            menu_mostrar_horarios()


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nPrograma finalizado.")
