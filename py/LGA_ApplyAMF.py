"""
____________________________________________________________________

  LGA_ApplyAMF v0.13 | Lega

  Crea en el Node Graph la cadena de color que declara el .amf del shot.

  Es la contraparte en Nuke del boton Apply AMF de HieroTools, que hace
  lo mismo con soft effects sobre los clips del timeline. Aca no hace
  falta seleccionar nada: el shot sale del .nk abierto.

  El .amf (ACES Metadata File) describe la cadena entera del plate y es
  la fuente de verdad. De ahi salen tres cosas:

    - QUE aplicar: cada <lookTransform> trae applied="true|false". Los
      que ya vienen horneados en el plate (IDT, Reference Gamut
      Compress) se saltean; solo se crean los que estan en false.
    - EN QUE ORDEN: los <lookTransform> vienen en orden de cadena. El
      primero del plan es el que se aplica primero, asi que queda ARRIBA,
      pegado al nodo del que cuelga la cadena. Es al reves que en el
      timeline de Hiero, donde el primero va al subtrack de mas abajo.
    - CON QUE PARAMETROS: la cadena corre en ACES2065-1, y el
      <cdlWorkingSpace> es la excepcion que saca al CDL a ACEScct.
      Ninguno de los dos es el scene_linear que trae el nodo por
      defecto. El <file> del LMT nombra el .clf a cargar, que entra
      y sale en ACES2065-1.

  Nodos que sabe crear:
    OCIOCDLTransform  <- el .cdl del plate (grade)
    OCIOFileTransform <- el .clf que nombra el .amf (LMT)

  Si el shot no trae .amf se cae a un plan fijo por extension: un .cdl y
  un .clf, sin tocar el working space.

  Flujo:
    1. Ruta del .nk abierto -> carpeta del shot (la que tiene _input).
    2. <shot>/_input/Look_Files/
    3. Barrido de .amf, agrupados POR PLATE. Un shot suele tener un .amf
       por plate y varias versiones de cada uno; se ofrece la version
       mas alta de cada plate.
    4. Cartel para elegir el plate (si hay mas de uno).
    5. Cartel para elegir que hacer con la cadena.
    6. Crear los nodos, setear sus knobs e insertarlos debajo del nodo
       seleccionado.

  Ejemplo de estructura esperada:
    T:/VFX-PROJA/101/PROJA_1013_0800_VND/_input/Look_Files/
        PROJA_1013_0800_VND_aPlate_v001.amf
        PROJA_1013_0800_VND_aPlate_v001.cdl
        PROJA_1013_0800_VND_cbPlate_v004.amf
        PROJA_1013_0800_VND_cbPlate_v004.cdl

  v0.13: Los textos visibles dicen "AMF" y no "Apply AMF", como la
         entrada del menu. Incluye el nombre del undo, que es lo que se
         lee en el Edit del host. El nombre del modulo y el key del menu
         NO cambian: el key es el que mira Enable Tools contra el
         Enabled.ini, y renombrarlo daria la tool por deshabilitada en
         toda instalacion que ya la tenga configurada.
  v0.12: El .clf del LMT pasa a procesarse en ACES2065-1. El nodo quedaba
         con su default `scene_linear`, que no es un espacio sino un ROL
         del config OCIO, y en los configs ACES apunta a ACEScg (AP1); el
         .clf entra y sale en AP0, asi que recibia el gamut equivocado. La
         cadena de un .amf corre en ACES2065-1 y el <cdlWorkingSpace> del
         CDL es la EXCEPCION, no la regla. Ademas el matcheo contra el enum
         del knob deja afuera los ROLES, y si el config no expone el espacio
         pedido eso sube a un cartel en vez de quedar en un WARN del log.
         Mismo criterio que Apply AMF de HieroTools.
  v0.11: La cadena se INSERTA en el stream en vez de quedar suelta al
         costado. Antes se creaban los nodos desconectados y ademas
         apilados hacia arriba, que en Nuke es al reves del sentido del
         flujo. Ahora sigue la convencion de las otras tools de build del
         pack (LGA_build_Grade): cuelga del nodo seleccionado, apila hacia
         abajo, le reconecta el input al nodo que venia debajo en la misma
         columna, y centra la cadena en el hueco. Sin seleccion crea un
         NoOp temporal en la posicion del cursor, como hace esa tool. La
         cadena de Input Process sigue yendo suelta, que es lo que
         corresponde: no cuelga del arbol del comp.
  v0.10: Version inicial.
____________________________________________________________________

"""

import os
import re
import xml.etree.ElementTree as ET

import nuke

# ============================
# Configuracion
# ============================

DEBUG = False

# Nombres de carpeta donde viven los archivos de look, colgando del shot.
INPUT_DIR_NAME = "_input"
LOOK_DIR_NAME = "Look_Files"

# El espacio en el que corre la cadena de un .amf.
#
# La pipeline ACES que describe un .amf opera en ACES2065-1, y por eso el CDL
# necesita declarar su <cdlWorkingSpace>: salirse a ACEScct es la EXCEPCION,
# no la regla. Un lookTransform que no declara nada corre en ACES2065-1.
#
# Sin esto, el nodo se queda con su default `scene_linear`, que es un ROL del
# config OCIO y no un espacio: en los configs ACES apunta a ACEScg (AP1). Un
# .clf de LMT entra y sale en AP0 -lo declara en su propio InputDescriptor y
# arranca con una matriz AP0 a AP1-, asi que alimentarlo con AP1 le mete una
# conversion de gamut de mas y corre la LUT sobre datos que no le corresponden.
#
# El knob no dice "la entrada esta en", dice "aplicalo en": el nodo convierte
# de scene_linear a este espacio, aplica el archivo y vuelve. Por eso pedir
# ACES2065-1 es correcto sea cual sea el working space del script.
AMF_WORKING_SPACE = "ACES2065-1"

# Plan de respaldo, para cuando el shot no trae .amf. Mismo orden que el .amf
# de referencia: primero el grade, despues el LMT.
FALLBACK_EFFECTS = (
    {"type": "OCIOCDLTransform", "extension": ".cdl"},
    {"type": "OCIOFileTransform", "extension": ".clf"},
)

# La corrida SIEMPRE deja su log, este o no prendido el debug por consola. Sin
# esto la tool es una caja negra: si no hace nada, no hay donde mirar por que.
LOG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "logs", "DebugPy_LGA_ApplyAMF.log"
)

_LOG_LINES = []


def debug_print(*message):
    """Acumula para el .log y, si DEBUG, ademas escribe en la consola."""
    linea = " ".join(str(m) for m in message)
    _LOG_LINES.append(linea)
    if DEBUG:
        print(linea)


def _volcar_log():
    """Escribe el log de la corrida, pisando el anterior. Nunca rompe la tool."""
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        with open(LOG_PATH, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(_LOG_LINES) + "\n")
    except Exception:
        pass
    del _LOG_LINES[:]


# ============================
# Helpers genericos
# ============================


def _find_subdir(parent_dir, wanted_name):
    """Busca una subcarpeta por nombre sin distinguir mayusculas.

    En Windows daria igual, pero este repo tambien corre en macOS, donde el
    filesystem si distingue.
    """
    if not parent_dir or not os.path.isdir(parent_dir):
        return None
    wanted = wanted_name.lower()
    try:
        for entry in os.scandir(parent_dir):
            if entry.is_dir() and entry.name.lower() == wanted:
                return entry.path
    except OSError as e:
        debug_print("  [WARN] No se pudo listar '%s': %s" % (parent_dir, e))
    return None


def _local_tag(element):
    """Nombre del tag sin el namespace.

    Los XML de ACES declaran namespace (urn:ampas:aces:amf:v2.0,
    urn:ASC:CDL:v1.01), asi que los tags vienen como '{urn:...}lookTransform'.
    """
    return element.tag.split("}")[-1]


def _normalize(text):
    """Deja solo letras y numeros en minuscula, para comparar nombres de espacios."""
    return re.sub(r"[^a-z0-9]", "", str(text).lower())


def _slash(path):
    """Barras hacia adelante, que es lo que espera Nuke en los knobs de archivo."""
    return re.sub(r"[\\/]+", "/", str(path))


# ============================
# Resolucion de rutas
# ============================


def get_script_path():
    """Ruta del .nk abierto, o None si el script nunca se guardo."""
    try:
        name = nuke.root().name()
    except Exception as e:
        debug_print("  [WARN] No se pudo leer el nombre del script: %s" % e)
        return None
    if not name or name == "Root":
        return None
    return _slash(name)


def resolve_shot_dir(script_path):
    """Carpeta del shot a partir de la ruta del .nk.

    Se sube por la ruta hasta el primer directorio que tenga `_input` adentro.
    Se hace por ESTRUCTURA y no por nombre a proposito: el .nk puede estar
    nombrado con otro vendor code que la carpeta del shot (por ejemplo un
    ..._SUP_comp_v012.nk dentro de PROYECTO_1029_0100_BOA), asi que matchear
    por nombre daria falso negativo.
    """
    if not script_path:
        return None

    current = os.path.dirname(_slash(script_path))
    while current and current != os.path.dirname(current):
        if _find_subdir(current, INPUT_DIR_NAME):
            return _slash(current)
        current = os.path.dirname(current)

    return None


def resolve_look_dir(shot_dir):
    """<shot>/_input/Look_Files"""
    if not shot_dir:
        return None
    input_dir = _find_subdir(shot_dir, INPUT_DIR_NAME)
    if not input_dir:
        debug_print("  [ERROR] No existe '%s' en %s" % (INPUT_DIR_NAME, shot_dir))
        return None
    look_dir = _find_subdir(input_dir, LOOK_DIR_NAME)
    if not look_dir:
        debug_print("  [ERROR] No existe '%s' en %s" % (LOOK_DIR_NAME, input_dir))
        return None
    return _slash(look_dir)


def find_look_file(look_dir, extension, quiet=False):
    """El unico archivo de esa extension en la carpeta de look.

    Solo se usa para el plan de respaldo (shots sin .amf) y para buscar un
    .clf suelto. Cuando hay .amf, los archivos se resuelven contra el nombre
    del .amf elegido, que es mucho mas preciso.
    """
    if not look_dir:
        return None

    try:
        candidates = sorted(
            entry.path
            for entry in os.scandir(look_dir)
            if entry.is_file() and entry.name.lower().endswith(extension)
        )
    except OSError as e:
        debug_print("  [ERROR] No se pudo listar '%s': %s" % (look_dir, e))
        return None

    if not candidates:
        if not quiet:
            debug_print("  [ERROR] No hay ningun '*%s' en %s" % (extension, look_dir))
        return None

    if len(candidates) > 1:
        debug_print(
            "  [AVISO] Hay %d archivos '%s', se usa el primero: %s"
            % (len(candidates), extension, os.path.basename(candidates[0]))
        )

    return _slash(candidates[0])


# ============================
# Barrido de plates
# ============================

# Nombre tipico: PROYECTO_SEQ_SHOT_VENDOR_aPlate_v001.amf. El plate es el
# anteultimo bloque y la version el ultimo. Se acepta cualquier token de
# plate (aPlate, bPlate, cbPlate, gpPlate...) porque cada proyecto usa los
# suyos, y se agrupa sin distinguir mayusculas: el mismo shot puede traer
# 'cbPlate' en un archivo y 'cbPLATE' en otro.
_PLATE_RE = re.compile(r"^(?P<base>.*)_(?P<plate>[A-Za-z0-9]+)_v(?P<version>\d+)$")


def parse_plate_name(basename):
    """Devuelve (plate, version) del nombre de archivo, o (None, None)."""
    stem = os.path.splitext(basename)[0]
    match = _PLATE_RE.match(stem)
    if not match:
        return None, None
    return match.group("plate"), int(match.group("version"))


def scan_amf_entries(look_dir):
    """Los .amf de la carpeta, agrupados por plate y con la version mas alta.

    Un shot tipico trae un .amf por version de cada plate
    (aPlate_v001, cbPlate_v001..v004). Ofrecer las cinco versiones no ayuda:
    lo que se aplica es el plate, y de cada plate la ultima version. Los
    .amf cuyo nombre no matchea el patron se ofrecen igual, cada uno como su
    propia entrada, para no esconderlos.

    Devuelve una lista de dicts {plate, version, path, name}, ordenada por
    nombre de plate.
    """
    if not look_dir:
        return []

    try:
        amf_files = [
            entry.path
            for entry in os.scandir(look_dir)
            if entry.is_file() and entry.name.lower().endswith(".amf")
        ]
    except OSError as e:
        debug_print("  [ERROR] No se pudo listar '%s': %s" % (look_dir, e))
        return []

    por_plate = {}
    sueltos = []
    for path in sorted(amf_files):
        nombre = os.path.basename(path)
        plate, version = parse_plate_name(nombre)
        if plate is None:
            sueltos.append(
                {
                    "plate": os.path.splitext(nombre)[0],
                    "version": None,
                    "path": _slash(path),
                    "name": nombre,
                }
            )
            continue
        clave = plate.lower()
        anterior = por_plate.get(clave)
        if anterior is None or version > anterior["version"]:
            por_plate[clave] = {
                "plate": plate,
                "version": version,
                "path": _slash(path),
                "name": nombre,
            }

    entradas = sorted(por_plate.values(), key=lambda e: e["plate"].lower())
    entradas.extend(sueltos)
    return entradas


def sibling_look_file(amf_path, extension):
    """El archivo hermano del .amf con la misma base y otra extension.

    Es la forma precisa de resolver el .cdl cuando el shot trae varios
    plates: 'SHOT_aPlate_v001.amf' -> 'SHOT_aPlate_v001.cdl'. La busqueda
    'el unico archivo de esa extension' que usa HieroTools no sirve aca,
    porque en Nuke se elige el plate y en la carpeta hay uno por plate.
    """
    candidato = os.path.splitext(amf_path)[0] + extension
    if os.path.isfile(candidato):
        return _slash(candidato)

    # Fallback sin distinguir mayusculas: hay carpetas donde el .amf dice
    # 'cbPLATE' y el .cdl 'cbPlate'.
    carpeta = os.path.dirname(amf_path)
    buscado = os.path.basename(candidato).lower()
    try:
        for entry in os.scandir(carpeta):
            if entry.is_file() and entry.name.lower() == buscado:
                return _slash(entry.path)
    except OSError:
        pass
    return None


def read_cccid(cdl_path):
    """Atributo id del primer <ColorCorrection> del .cdl.

    Es lo que el OCIOCDLTransform espera en el knob cccid para elegir que
    correccion aplicar dentro del archivo. No se arma con el nombre del
    plate: el archivo puede declarar otra version que la media.
    """
    try:
        root = ET.parse(cdl_path).getroot()
    except Exception as e:
        debug_print("  [WARN] No se pudo parsear el .cdl: %s" % e)
        return None

    ids = [
        element.get("id")
        for element in root.iter()
        if _local_tag(element) == "ColorCorrection" and element.get("id")
    ]

    if not ids:
        debug_print("  [WARN] El .cdl no declara ningun ColorCorrection id")
        return None

    if len(ids) > 1:
        debug_print("  [INFO] El .cdl tiene %d ids, se usa el primero" % len(ids))
    return ids[0]


# ============================
# Lectura del .amf
# ============================


def _target_space_from_transform_id(transform_id):
    """Espacio destino de un ACEScsc.

    'urn:ampas:aces:transformId:v1.5:ACEScsc.Academy.ACES_to_ACEScct.a1.0.3'
    devuelve 'ACEScct'.
    """
    if not transform_id:
        return None
    match = re.search(r"ACES_to_([A-Za-z0-9]+)", transform_id)
    return match.group(1) if match else None


def _target_space_from_description(description):
    """Espacio destino de una descripcion tipo 'ACES2065-1 to ACEScct'."""
    if not description or " to " not in description:
        return None
    return description.split(" to ")[-1].strip() or None


def _read_look_transform(element):
    """Interpreta un <lookTransform> del .amf.

    Devuelve un dict con lo que se pudo reconocer: si es el CDL (trae
    cdlWorkingSpace), si es un LMT de archivo (trae file), y si ya viene
    aplicado en el plate.
    """
    info = {
        "applied": (element.get("applied") or "").strip().lower() == "true",
        "description": None,
        "working_space": None,
        "file": None,
        "has_cdl": False,
    }

    for child in element.iter():
        tag = _local_tag(child)
        text = (child.text or "").strip() if child.text else ""

        if tag == "description" and not info["description"]:
            info["description"] = text
        elif tag == "file" and text:
            info["file"] = text
        elif tag in ("SOPNode", "SatNode", "SATNode", "cdlWorkingSpace"):
            info["has_cdl"] = True

    # El working space del CDL: se prefiere el transformId, que es estructurado.
    for child in element.iter():
        if _local_tag(child) != "toCdlWorkingSpace":
            continue
        for sub in child.iter():
            sub_tag = _local_tag(sub)
            sub_text = (sub.text or "").strip() if sub.text else ""
            if sub_tag == "transformId":
                info["working_space"] = _target_space_from_transform_id(sub_text)
            elif sub_tag == "description" and not info["working_space"]:
                info["working_space"] = _target_space_from_description(sub_text)

    return info


def read_amf(amf_path):
    """Lee el .amf y devuelve la lista de <lookTransform> en orden de cadena."""
    try:
        root = ET.parse(amf_path).getroot()
    except Exception as e:
        debug_print("  [WARN] No se pudo parsear el .amf: %s" % e)
        return []

    return [
        _read_look_transform(element)
        for element in root.iter()
        if _local_tag(element) == "lookTransform"
    ]


def build_effect_plan(look_dir, amf_path=None):
    """Arma la lista de nodos a crear, en orden.

    Con .amf: se respeta el orden y el applied de cada lookTransform, y se
    toman working space y nombre de archivo de ahi. El .cdl se resuelve como
    hermano del .amf elegido. Sin .amf: plan fijo por extension.
    """
    if not amf_path:
        debug_print("  [AVISO] El shot no trae .amf: se usa el plan fijo por extension.")
        return _fallback_plan(look_dir)

    debug_print("  amf                  : %s" % amf_path)
    look_transforms = read_amf(amf_path)
    if not look_transforms:
        debug_print("  [AVISO] El .amf no declara lookTransform: se usa el plan fijo.")
        return _fallback_plan(look_dir)

    plan = []
    for index, info in enumerate(look_transforms, start=1):
        etiqueta = info["description"] or "<sin descripcion>"

        if info["applied"]:
            debug_print("    %d. [YA APLICADO] %s" % (index, etiqueta))
            continue

        if info["has_cdl"]:
            cdl_path = sibling_look_file(amf_path, ".cdl")
            if not cdl_path:
                debug_print(
                    "    %d. [ERROR] El .amf pide un CDL y no hay .cdl hermano" % index
                )
                continue
            debug_print(
                "    %d. [APLICAR] CDL -> %s (working space: %s)"
                % (
                    index,
                    os.path.basename(cdl_path),
                    info["working_space"] or "sin declarar",
                )
            )
            plan.append(
                {
                    "type": "OCIOCDLTransform",
                    "file": cdl_path,
                    "cccid": read_cccid(cdl_path),
                    "working_space": info["working_space"] or AMF_WORKING_SPACE,
                    "label": "CDL",
                }
            )
            continue

        if info["file"]:
            # El .amf nombra el archivo; se resuelve contra la carpeta de look.
            lmt_path = os.path.join(look_dir, info["file"])
            if not os.path.isfile(lmt_path):
                debug_print(
                    "    %d. [AVISO] El .amf nombra '%s' y no esta en la carpeta"
                    % (index, info["file"])
                )
                lmt_path = find_look_file(
                    look_dir, os.path.splitext(info["file"])[1]
                )
                if not lmt_path:
                    debug_print(
                        "    %d. [ERROR] Tampoco hay otro archivo de esa extension"
                        % index
                    )
                    continue
            lmt_path = _slash(lmt_path)
            espacio_lmt = info["working_space"] or AMF_WORKING_SPACE
            debug_print(
                "    %d. [APLICAR] LMT -> %s (working space: %s)"
                % (index, os.path.basename(lmt_path), espacio_lmt)
            )
            plan.append(
                {
                    "type": "OCIOFileTransform",
                    "file": lmt_path,
                    "cccid": None,
                    "working_space": espacio_lmt,
                    "label": "LMT",
                }
            )
            continue

        # Transforms que el .amf declara solo por transformId (built-in del
        # config OCIO, sin archivo). No se pueden cargar en un nodo de archivo.
        debug_print("    %d. [SALTEADO] Sin archivo asociado: %s" % (index, etiqueta))

    return plan


def _fallback_plan(look_dir):
    """Plan fijo por extension, para shots sin .amf.

    Sin .amf el unico working space que se puede afirmar es el del .clf: un LMT
    de ACES entra y sale en ACES2065-1 por convencion, y el archivo mismo lo
    declara. El del .cdl queda sin tocar a proposito: un .cdl suelto puede estar
    hecho para ACEScct, ACEScc o lineal, y no hay de donde saberlo. Adivinarlo
    seria peor que dejar el default y que el log lo diga.
    """
    plan = []
    for spec in FALLBACK_EFFECTS:
        file_path = find_look_file(look_dir, spec["extension"])
        if not file_path:
            continue
        es_cdl = spec["type"] == "OCIOCDLTransform"
        plan.append(
            {
                "type": spec["type"],
                "file": file_path,
                "cccid": read_cccid(file_path) if es_cdl else None,
                "working_space": None if es_cdl else AMF_WORKING_SPACE,
                "label": "CDL" if es_cdl else "LMT",
            }
        )
    return plan


# ============================
# Creacion de nodos
# ============================


def _set_knob(node, knob_name, value):
    """setValue con log. True si se pudo."""
    try:
        node[knob_name].setValue(value)
        debug_print("    [OK] %s = %r" % (knob_name, value))
        return True
    except Exception as e:
        debug_print("    [ERROR] No se pudo setear %s: %s" % (knob_name, e))
        return False


def match_colorspace_option(node, knob_name, wanted):
    """Encuentra en el enum del knob la opcion que corresponde a `wanted`.

    El nombre exacto del espacio depende del OCIO config del proyecto: el
    mismo ACEScct puede figurar como 'ACEScct' o 'ACES - ACEScct'. Por eso no
    se hardcodea el string, se busca contra las opciones reales del knob.
    """
    if not wanted:
        return None

    try:
        options = list(node[knob_name].values())
    except Exception as e:
        debug_print("    [WARN] No se pudieron leer las opciones de %s: %s" % (knob_name, e))
        return None

    target = _normalize(wanted)

    # Dos pasadas: primero contra los espacios nombrados DIRECTO, y recien
    # despues contra la lista entera. Los ROLES del config aparecen en el enum
    # con formato 'scene_linear (ACES - ACEScg)' y son una INDIRECCION: pidiendo
    # ACES2065-1 matchean 'ACES - ACES2065-1' y 'default (ACES - ACES2065-1)', y
    # cual gana depende del orden del enum. La segunda pasada no es un adorno:
    # hay colorspaces directos con parentesis en su propio nombre -en aces_1.2
    # hay 34, del tipo 'Input - ARRI - V3 LogC (EI160) - Wide Gamut'-, y
    # descartarlos de una dejaria sin resolver a quien pida uno de esos. Con las
    # dos pasadas, un rol solo puede ganar si NADA directo sirve.
    directas = [o for o in options if "(" not in str(o)]

    for candidatas in (directas, options):
        # De mas estricto a mas laxo. El orden importa: buscando 'ACEScc'
        # primero por igualdad y sufijo se evita que matchee 'ACEScct' por
        # contencion.
        for opcion in candidatas:
            if _normalize(opcion) == target:
                return opcion
        for opcion in candidatas:
            if _normalize(opcion).endswith(target):
                return opcion
        for opcion in candidatas:
            if target in _normalize(opcion):
                return opcion

    debug_print("    [WARN] '%s' no figura entre las opciones de %s" % (wanted, knob_name))
    return None


def configure_node(node, spec):
    """Carga el archivo de look y los parametros del .amf en el nodo.

    Devuelve (ok, motivo), donde `motivo` es el texto para el cartel del
    usuario cuando algo quedo mal, o None si salio todo bien.
    """
    if not node:
        debug_print("    [ERROR] No hay nodo que configurar.")
        return False, "the node could not be configured"

    ok = True
    motivo = None

    if spec["type"] == "OCIOCDLTransform":
        # read_from_file va PRIMERO: con el knob en False, file y cccid quedan
        # deshabilitados y el nodo ignora el archivo.
        ok = _set_knob(node, "read_from_file", True) and ok
        ok = _set_knob(node, "file", spec["file"]) and ok
        if spec.get("cccid"):
            ok = _set_knob(node, "cccid", spec["cccid"]) and ok
        else:
            debug_print("    [WARN] Sin cccid: el nodo toma la primera correccion del archivo.")
    else:
        ok = _set_knob(node, "file", spec["file"]) and ok

    # El working space sale del .amf, o de AMF_WORKING_SPACE si el .amf no lo
    # declara. El default del nodo, `scene_linear`, es un rol que en los configs
    # ACES cae en ACEScg: no es el espacio en el que corre la cadena.
    wanted = spec.get("working_space")
    if wanted:
        opcion = match_colorspace_option(node, "working_space", wanted)
        if opcion:
            ok = _set_knob(node, "working_space", opcion) and ok
        else:
            # NO es cosmetico y no puede pasar en silencio: el nodo se queda en
            # `scene_linear`, que en los configs ACES es ACEScg, y el archivo de
            # look termina corriendo sobre el gamut equivocado. La cadena queda
            # creada pero MAL, asi que el motivo sube al cartel. Un resultado
            # incorrecto informado como exito es el peor final.
            debug_print(
                "    [ERROR] El OCIO config del script no expone '%s': el "
                "working_space queda en el default del nodo y el look sale mal."
                % wanted
            )
            motivo = "the project OCIO config has no '%s' colorspace" % wanted
            ok = False

    return ok, motivo


def create_chain(plan, label_suffix=None, avisos=None):
    """Crea los nodos del plan, configurados, sin posicionar ni conectar.

    Los nodos se crean con nuke.nodes.<Clase>() y no con nuke.createNode():
    createNode engancha el nodo a lo que este seleccionado -y aca la
    conexion la maneja el llamador, que sabe donde va la cadena- y ademas
    abre el panel de propiedades de cada uno.

    Devuelve la lista de nodos creados, en el orden del plan. El orden del
    plan es el de la cadena: el primero se aplica primero, o sea que va
    ARRIBA en el Node Graph.

    `avisos` es una lista opcional donde se juntan los motivos por los que un
    nodo quedo mal configurado, para mostrarlos DESPUES en un solo cartel. Un
    motivo repetido no se agrega dos veces: las dos cadenas -la del comp y la
    del Input Process- salen del MISMO plan, asi que fallarian por lo mismo y
    verlo duplicado no aporta.
    """
    nodos = []
    for spec in plan:
        debug_print("\n  --- %s ---" % spec["type"])
        debug_print("    archivo   : %s" % spec["file"])
        if spec.get("cccid"):
            debug_print("    cccid     : %s" % spec["cccid"])
        try:
            node = getattr(nuke.nodes, spec["type"])()
        except Exception as e:
            debug_print("    [ERROR] No se pudo crear el nodo: %s" % e)
            continue

        _ok, motivo = configure_node(node, spec)
        if motivo and avisos is not None and motivo not in avisos:
            avisos.append(motivo)

        etiqueta = spec.get("label") or ""
        if label_suffix:
            etiqueta = ("%s\n%s" % (etiqueta, label_suffix)).strip()
        if etiqueta:
            _set_knob(node, "label", etiqueta)

        nodos.append(node)

    return nodos


def connect_chain(nodos):
    """Encadena los nodos entre si: el primero del plan alimenta al segundo.

    La cadena queda armada pero sin input externo, lista para engancharla a
    mano donde corresponda.
    """
    for anterior, siguiente in zip(nodos, nodos[1:]):
        try:
            siguiente.setInput(0, anterior)
        except Exception as e:
            debug_print("  [WARN] No se pudo conectar %s: %s" % (siguiente.name(), e))


def assign_input_process(node):
    """Asigna el nodo como Input Process de todos los Viewers. True si pudo.

    Se le prende ademas el flag de Input Process al Viewer: sin eso el nodo
    queda asignado pero apagado, y la tool parece no haber hecho nada.
    """
    asignado = False
    for viewer in nuke.allNodes("Viewer"):
        try:
            viewer["input_process_node"].setValue(node.name())
            try:
                viewer["input_process"].setValue(True)
            except Exception:
                pass
            asignado = True
            debug_print(
                "  [OK] %s asignado como Input Process en %s"
                % (node.name(), viewer.name())
            )
        except Exception as e:
            debug_print("  [WARN] No se pudo asignar el Input Process: %s" % e)
    if not asignado:
        debug_print("  [WARN] No hay ningun Viewer al que asignarle el Input Process.")
    return asignado


# ============================
# Posicion en el Node Graph
# ============================


# Las mismas medidas que usan las tools de build del pack
# (LGA_ToolPack/py/LGA_build_Grade.py). Van iguales a proposito: la cadena
# que arma esta tool tiene que quedar con el mismo aire que las demas.
DISTANCIA_X = 130
DISTANCIA_Y = 20


def _simulate_dag_click():
    """Click sintetico en el DAG, en la posicion del cursor.

    Es el truco que usa LGA_build_Grade para que el NoOp temporal nazca
    donde el usuario esta mirando y no en el 0,0 del Node Graph. El import
    de Qt va adentro de la funcion para que este modulo se pueda importar
    -y testear- sin PySide.
    """
    try:
        from LGA_QtAdapter_ToolPackB import QtGui, QtWidgets, QtCore

        widget = QtWidgets.QApplication.widgetAt(QtGui.QCursor.pos())
        if not widget:
            return
        local_pos = widget.mapFromGlobal(QtGui.QCursor.pos())
        for tipo in (
            QtCore.QEvent.MouseButtonPress,
            QtCore.QEvent.MouseButtonRelease,
        ):
            evento = QtGui.QMouseEvent(
                tipo,
                local_pos,
                QtCore.Qt.LeftButton,
                QtCore.Qt.LeftButton,
                QtCore.Qt.NoModifier,
            )
            QtWidgets.QApplication.sendEvent(widget, evento)
    except Exception as e:
        debug_print("  [WARN] No se pudo simular el click en el DAG: %s" % e)


def get_anchor_node():
    """El nodo del que cuelga la cadena. Devuelve (nodo, noop_temporal).

    Mismo contrato que get_selected_node() de LGA_build_Grade: si no hay
    nada seleccionado se crea un NoOp en la posicion del cursor para tener
    de donde colgar, y el llamador lo borra al terminar.
    """
    try:
        node = nuke.selectedNode()
        debug_print("  ancla                : %s (%s)" % (node.name(), node.Class()))
        return node, None
    except ValueError:
        _simulate_dag_click()
        no_op = nuke.createNode("NoOp")
        debug_print("  ancla                : <nada seleccionado>, NoOp temporal")
        return no_op, no_op


def find_next_node_in_column(current_node, tolerance_x=120):
    """El primer nodo que esta DEBAJO del ancla en la misma columna.

    Es el que hay que reconectar para que la cadena quede INSERTADA en el
    stream y no colgando al costado. Copiado de LGA_build_Grade para que las
    dos tools decidan igual que es "la misma columna".
    """
    cx = current_node.xpos() + (current_node.screenWidth() / 2)
    cy = current_node.ypos() + (current_node.screenHeight() / 2)

    siguiente = None
    distancia_min = float("inf")

    for node in nuke.allNodes():
        if node is current_node or node.Class() in ("Root", "BackdropNode"):
            continue
        nx = node.xpos() + (node.screenWidth() / 2)
        ny = node.ypos() + (node.screenHeight() / 2)
        if abs(nx - cx) <= tolerance_x and ny > cy:
            distancia = ny - cy
            if 0 < distancia < distancia_min:
                distancia_min = distancia
                siguiente = node

    if siguiente:
        debug_print(
            "  siguiente en columna : %s (%s)" % (siguiente.name(), siguiente.Class())
        )
    else:
        debug_print("  siguiente en columna : <ninguno>")
    return siguiente


def insert_chain(nodos, anchor, es_noop=False):
    """Cuelga la cadena del ancla, la apila hacia abajo y la mete en el stream.

    En Nuke el flujo va de arriba hacia abajo, asi que el PRIMER eslabon del
    plan -el que el .amf aplica primero- va pegado al ancla y los siguientes
    van bajando. Es al reves que en el timeline de Hiero, donde el primero
    queda en el subtrack de mas abajo.

    Si debajo del ancla habia otro nodo alimentado por el, se le reconecta el
    input al ULTIMO de la cadena: la cadena queda INSERTADA y no colgando al
    costado, que es lo que hacen el resto de las tools de build del pack.
    """
    if not nodos:
        return

    siguiente = find_next_node_in_column(anchor)

    # Apilado hacia abajo, centrado en el ancla.
    y = anchor.ypos() + anchor.screenHeight() + DISTANCIA_Y
    if es_noop:
        # El NoOp es un nodo fantasma que se borra enseguida: sin este ajuste
        # la cadena queda flotando su alto mas abajo de donde apunta el cursor.
        y = anchor.ypos() + anchor.screenHeight() - DISTANCIA_Y * 2
    for node in nodos:
        node.setXpos(
            int(
                anchor.xpos()
                + (anchor.screenWidth() // 2)
                - (node.screenWidth() // 2)
            )
        )
        node.setYpos(int(y))
        y += node.screenHeight() + DISTANCIA_Y

    # Conexiones: ancla -> primero -> ... -> ultimo -> lo que venia abajo.
    try:
        nodos[0].setInput(0, anchor)
    except Exception as e:
        debug_print("  [WARN] No se pudo conectar la cadena al ancla: %s" % e)
    connect_chain(nodos)

    if siguiente is not None:
        _centrar_en_el_hueco(nodos, anchor, siguiente)
        for i in range(siguiente.inputs()):
            if siguiente.input(i) is anchor:
                siguiente.setInput(i, nodos[-1])
                debug_print(
                    "  [OK] %s ahora toma su input de %s"
                    % (siguiente.name(), nodos[-1].name())
                )
                break


def _centrar_en_el_hueco(nodos, anchor, siguiente):
    """Centra la cadena en el espacio libre entre el ancla y el nodo de abajo.

    Mismo criterio que LGA_build_Grade: si entra, se centra; si no entra, se
    prioriza que el primer eslabon quede pegado al ancla y la cadena se pasa
    hacia abajo lo que haga falta.
    """
    hueco_arriba = anchor.ypos() + anchor.screenHeight()
    hueco_abajo = siguiente.ypos()
    hueco = hueco_abajo - hueco_arriba

    alto = (nodos[-1].ypos() + nodos[-1].screenHeight()) - nodos[0].ypos()

    if alto <= hueco:
        destino = hueco_arriba + (hueco - alto) / 2
    else:
        destino = hueco_arriba + DISTANCIA_Y

    offset = int(destino - nodos[0].ypos())
    debug_print(
        "  hueco=%d alto_cadena=%d offset=%d" % (hueco, alto, offset)
    )
    # Solo se sube: en un hueco grande no hay por que empujar la cadena.
    if offset < 0:
        for node in nodos:
            node.setYpos(node.ypos() + offset)


# ============================
# Entrada
# ============================


def _aviso(titulo, texto):
    """Cartel de aviso del pack, con fallback al de Nuke."""
    debug_print("[AVISO AL USUARIO] %s" % texto)
    try:
        from LGA_UI_MessageBox_ToolPackB import show_warning

        show_warning(None, titulo, texto)
    except Exception as e:
        debug_print("  [WARN] No se pudo mostrar el cartel: %s" % e)
        nuke.message(texto)


def _main_interno():
    debug_print("=" * 70)
    debug_print("  LGA_ApplyAMF - cadena de color segun el .amf del shot")
    debug_print("=" * 70)

    titulo = "AMF"

    script_path = get_script_path()
    debug_print("  script               : %s" % script_path)
    if not script_path:
        _aviso(
            titulo,
            "The script has not been saved yet.\n\n"
            "AMF finds the shot from the .nk path, so the script has to "
            "live inside the shot folder first.",
        )
        return

    shot_dir = resolve_shot_dir(script_path)
    debug_print("  shot dir             : %s" % shot_dir)
    if not shot_dir:
        _aviso(
            titulo,
            "Could not resolve the shot folder from the script path:\n\n"
            "%s\n\n"
            "AMF walks up the path looking for a folder that contains "
            "'%s'." % (script_path, INPUT_DIR_NAME),
        )
        return

    look_dir = resolve_look_dir(shot_dir)
    debug_print("  look dir             : %s" % look_dir)
    if not look_dir:
        _aviso(
            titulo,
            "There is no %s/%s folder in this shot:\n\n%s"
            % (INPUT_DIR_NAME, LOOK_DIR_NAME, shot_dir),
        )
        return

    # ---- Que plate ----
    entradas = scan_amf_entries(look_dir)
    debug_print("  amf encontrados      : %d" % len(entradas))
    for entrada in entradas:
        debug_print("      %s (v%s)" % (entrada["plate"], entrada["version"]))

    amf_path = None
    if len(entradas) == 1:
        # Un solo plate: no hay nada que preguntar.
        amf_path = entradas[0]["path"]
        debug_print("  [INFO] Un solo .amf, se usa sin preguntar.")
    elif len(entradas) > 1:
        from LGA_ApplyAMF_Dialogs import pick_plate

        elegido = pick_plate(None, entradas)
        if elegido is None:
            debug_print("  [INFO] El usuario cancelo la eleccion de plate.")
            return
        amf_path = elegido["path"]
        debug_print("  [INFO] Plate elegido: %s" % elegido["name"])

    debug_print("  [PLAN SEGUN EL AMF]")
    plan = build_effect_plan(look_dir, amf_path)
    if not plan:
        _aviso(
            titulo,
            "Nothing to apply.\n\n"
            "The look files live in <shot>/%s/%s (.amf, .cdl and .clf)."
            % (INPUT_DIR_NAME, LOOK_DIR_NAME),
        )
        return

    # ---- Que hacer con la cadena ----
    from LGA_ApplyAMF_Dialogs import ask_actions

    acciones = ask_actions(None)
    if acciones is None:
        debug_print("  [INFO] El usuario cancelo la eleccion de acciones.")
        return
    crear_nodos, como_input_process = acciones
    debug_print(
        "  acciones             : crear=%s input_process=%s"
        % (crear_nodos, como_input_process)
    )

    # ---- Crear ----
    # Los motivos por los que un nodo queda mal configurado se juntan aca y se
    # muestran en UN cartel al final, ya cerrado el Undo: primero se termina el
    # trabajo sobre el Node Graph, despues se le habla al usuario.
    avisos = []
    nuke.Undo().begin("AMF")
    try:
        # El ancla se resuelve ANTES de deseleccionar: es el nodo seleccionado.
        anchor, no_op = get_anchor_node()

        for node in nuke.allNodes():
            try:
                node["selected"].setValue(False)
            except Exception:
                pass

        creados = []

        if crear_nodos:
            debug_print("\n[CADENA PARA EL COMP]")
            cadena = create_chain(plan, avisos=avisos)
            insert_chain(cadena, anchor, es_noop=bool(no_op))
            creados.extend(cadena)

        if como_input_process:
            debug_print("\n[CADENA DE INPUT PROCESS]")
            # Esta cadena va SUELTA a proposito: el Input Process no cuelga
            # del arbol del comp, lo lee el Viewer por su cuenta. Se planta a
            # la derecha del ancla para no encimarse con la otra.
            cadena_ip = create_chain(plan, label_suffix="Input Process", avisos=avisos)
            connect_chain(cadena_ip)
            x_ip = anchor.xpos() + DISTANCIA_X * 2
            y_ip = anchor.ypos() + anchor.screenHeight() + DISTANCIA_Y
            for node in cadena_ip:
                node.setXpos(int(x_ip))
                node.setYpos(int(y_ip))
                y_ip += node.screenHeight() + DISTANCIA_Y
            creados.extend(cadena_ip)
            if cadena_ip:
                # El ultimo del plan es el final de la cadena: ese es el que
                # ve el Viewer.
                assign_input_process(cadena_ip[-1])
            else:
                debug_print("  [ERROR] No se creo ningun nodo para el Input Process.")

        # El NoOp temporal se borra recien aca: hasta que la cadena no quedo
        # colgada de el, sigue siendo el ancla.
        if no_op:
            try:
                nuke.delete(no_op)
                debug_print("  [OK] NoOp temporal borrado.")
            except Exception as e:
                debug_print("  [WARN] No se pudo borrar el NoOp temporal: %s" % e)

        for node in creados:
            try:
                node["selected"].setValue(True)
            except Exception:
                pass

        debug_print("\n[LISTO] nodos creados: %d" % len(creados))
    finally:
        nuke.Undo().end()

    # La cadena quedo creada, pero si algun nodo no pudo tomar su working space
    # el look sale MAL. Callarlo es el peor final: el usuario ve los nodos en el
    # Node Graph y da por hecho que estan bien.
    if avisos:
        _aviso(
            titulo,
            "The color chain was created, but it is NOT correct:\n\n"
            "    %s\n\n"
            "The nodes kept their default working space, so the look is being "
            "applied in the wrong color space." % "\n    ".join(avisos),
        )


def main():
    """Punto de entrada de la tool. Siempre deja su log."""
    try:
        _main_interno()
    except Exception:
        import traceback

        debug_print("[ERROR NO CONTROLADO]\n%s" % traceback.format_exc())
        raise
    finally:
        _volcar_log()
