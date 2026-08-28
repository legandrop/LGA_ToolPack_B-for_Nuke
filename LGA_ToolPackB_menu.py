"""
_____________________________________

  LGA_ToolPackB_menu v1.01 | Lega
  Colección de herramientas de Nuke

  v1.01: El cartel de Animation Maker sale del helper de carteles del
         pack (show_info) en vez de nuke.message, con fallback.
  v1.00: Version anterior, sin changelog interno.
_____________________________________

"""

import nuke
import nukescripts
import os
import importlib
import webbrowser

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
PY_DIR = os.path.join(ROOT_DIR, "py")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")


def _read_product_version():
    """Lee la version publicada desde la fuente unica VERSION."""
    version_path = os.path.join(ROOT_DIR, "VERSION")
    try:
        with open(version_path, "r", encoding="utf-8") as version_file:
            return version_file.read().strip()
    except (OSError, UnicodeError) as error:
        nuke.warning("No se pudo leer VERSION de LGA_ToolPack-B: %s" % error)
        return "unknown"


PRODUCT_VERSION = _read_product_version()

# Carga los modulos runtime desde py/
nuke.pluginAddPath(PY_DIR.replace("\\", "/"))

# Carteles estilados del pack. Con fallback al cartel de Nuke: el menu tiene
# que armarse aunque falte el helper. Va despues del pluginAddPath, que es lo
# que hace importable a py/.
try:
    from LGA_UI_MessageBox_ToolPackB import show_info
except ImportError:

    def show_info(parent, title, text):
        nuke.message(text)


# --- Config loader & helpers (igual que ToolPack) ----------------------------


# El estado de las tools lo resuelve LGA_ToolPackB_Enabled, que lo lee de la
# carpeta de datos del usuario y no de adentro del pack. Vive en py/ para que
# el panel de Enable Tools use exactamente la misma logica que el menu.
# `except Exception` y no `except ImportError`: un SyntaxError o un fallo de
# encoding al importar no son ImportError, se propagarian y Nuke arrancaria sin
# el menu entero, que es exactamente lo que se quiere evitar.
try:
    import LGA_ToolPackB_Enabled as _enabled_config
except Exception as _enabled_error:
    # Si el modulo falta, el menu tiene que armarse igual y con todo visible:
    # es preferible mostrar de mas a dejar al usuario sin herramientas.
    nuke.warning("No se pudo cargar LGA_ToolPackB_Enabled: %s" % _enabled_error)
    _enabled_config = None
else:
    # Siembra la config del usuario la primera vez, rescatando lo que hubiera
    # configurado antes de que esa ubicacion existiera. Va en su propio try
    # por el mismo motivo: sembrar es una comodidad, no una condicion para
    # que exista el menu.
    try:
        _enabled_config.ensure_user_ini()
    except Exception as _seed_error:
        nuke.warning("No se pudo sembrar la config de LGA ToolPack-B: %s" % _seed_error)


def load_tool_flags():
    """Estado efectivo de las tools. {} si el modulo de config no cargo."""
    if _enabled_config is None:
        return {}
    return _enabled_config.load_flags()


def is_enabled(key: str) -> bool:
    """Si no está en ninguna capa => True (default)."""
    if _enabled_config is None:
        return True
    return _enabled_config.is_enabled(key)


def add_tool(menu, label, key, module, attr, shortcut=None, icon=None, context=2):
    """Registra una tool si está habilitada. Import lazy."""
    if not is_enabled(key):
        nuke.warning(f"Tool disabled: {key}")
        return

    def _runner():
        # Sin try/except para que falle si hay error
        m = importlib.import_module(module)
        func = getattr(m, attr)
        return func()

    kwargs = {}
    if shortcut:
        kwargs["shortcut"] = shortcut
    if icon:
        kwargs["icon"] = icon
    if context is not None:
        kwargs["shortcutContext"] = context

    menu.addCommand(label, _runner, **kwargs)


def _export_to_main(**objects):
    """Publica los objetos recibidos en el namespace __main__.

    Nuke evalua los comandos de menu pasados como string dentro de __main__.
    Mientras la implementacion vivia en menu.py eso funcionaba solo, porque Nuke
    ejecuta menu.py en ese mismo namespace. Ahora el codigo vive en este modulo,
    asi que sus imports quedan en el namespace del modulo y los comandos string
    fallarian con NameError si no se publican explicitamente.
    """
    import __main__

    for name, obj in objects.items():
        setattr(__main__, name, obj)


def _get_icon(name):
    icons_root = os.path.join(PY_DIR, "icons")
    path = os.path.join(icons_root, name) + ".png"
    return path.replace("\\", "/")


# Crea el menu "TP2" (ToolPack-B)
n2 = nuke.menu("Nuke").addMenu("TP2", icon=_get_icon("LGA2"))


# -----------------------------------------------------------------------------
#                              READ n WRITE TOOLS
# -----------------------------------------------------------------------------
n2.addCommand("READ n WRITE", lambda: None)
icon_RnW = _get_icon("TP_RnW")

add_tool(
    n2,
    label="  Media Missing Frames",
    key="Media_Missing_Frames",
    module="LGA_mediaMissingFrames",
    attr="main",
    shortcut="ctrl+alt+shift+m",
    icon=icon_RnW,
    context=2,
)

add_tool(
    n2,
    label="  Reload all Reads",
    key="Reload_All_Reads",
    module="LGA_reloadAllReads",
    attr="main",
    shortcut="ctrl+alt+shift+r",
    icon=icon_RnW,
    context=2,
)

add_tool(
    n2,
    label="  Rename Writes from Reads",
    key="Rename_Writes_From_Reads",
    module="LGA_renameWritesFromReads",
    attr="renameWrite",
    shortcut="F2",
    icon=icon_RnW,
    context=2,
)

add_tool(
    n2,
    label="  CopyCat Cleaner",
    key="CopyCat_Cleaner",
    module="LGA_CopyCat_Cleaner",
    attr="run_copycat_cleaner",
    icon=icon_RnW,
)

add_tool(
    n2,
    label="  Update Folder Favs",
    key="Update_Folder_Favs",
    module="LGA_UpdateFolderFavs",
    attr="main",
    icon=icon_RnW,
)


# -----------------------------------------------------------------------------
#                              FRAME RANGE TOOLS
# -----------------------------------------------------------------------------
n2.addSeparator()
n2.addCommand("FRAME RANGE", lambda: None)
icon_FR = _get_icon("TP_FR")

add_tool(
    n2,
    label="  Read -> FrameRange",
    key="FR_Read_to_FrameRange",
    module="LGA_fr_Read_to_FrameRange",
    attr="set_frame_range_from_read",
    shortcut="ctrl+alt+f",
    icon=icon_FR,
    context=2,
)

add_tool(
    n2,
    label="  Read -> Write",
    key="FR_Read_to_Write",
    module="LGA_fr_Read_to_Write",
    attr="Writes_FrameRange",
    icon=icon_FR,
    context=2,
)

add_tool(
    n2,
    label="  TimeClip -> Write",
    key="FR_TimeClip_to_Write",
    module="LGA_fr_TimeClip_to_Write",
    attr="set_write_from_timeclip",
    shortcut="ctrl+t",
    icon=icon_FR,
    context=2,
)


# -----------------------------------------------------------------------------
#                              COPY n PASTE TOOLS
# -----------------------------------------------------------------------------
n2.addSeparator()
n2.addCommand("COPY n PASTE", lambda: None)
icon_CnP = _get_icon("TP_CnP")

add_tool(
    n2,
    label="  Paste To Selected",
    key="Paste_To_Selected",
    module="pasteToSelected",
    attr="pasteToSelected",
    shortcut="ctrl+shift+v",
    icon=icon_CnP,
    context=2,
)

add_tool(
    n2,
    label="  Copy with inputs",
    key="Copy_with_inputs",
    module="duplicateWithInputs",
    attr="copyWithInputs",
    shortcut="ctrl+alt+c",
    icon=icon_CnP,
    context=2,
)
add_tool(
    n2,
    label="  Paste with inputs",
    key="Paste_with_inputs",
    module="duplicateWithInputs",
    attr="pasteWithInputs",
    shortcut="ctrl+alt+v",
    icon=icon_CnP,
    context=2,
)
add_tool(
    n2,
    label="  Duplicate with inputs",
    key="Duplicate_with_inputs",
    module="duplicateWithInputs",
    attr="duplicateWithInputs",
    shortcut="ctrl+alt+k",
    icon=icon_CnP,
    context=2,
)


# -----------------------------------------------------------------------------
#                                 NODE BUILDS
# -----------------------------------------------------------------------------
n2.addSeparator()
n2.addCommand("NODE BUILDS", lambda: None)
icon_Knobs = _get_icon("TP_Knobs")

add_tool(
    n2,
    label="  DasGrain Kronos Comp",
    key="DasGrain_Kronos_Comp",
    module="LGA_DasGrain_Kronos_Comp",
    attr="main",
    icon=icon_Knobs,
)

if is_enabled("AnimationMaker"):
    # Importar AnimationMaker para que se registre el menú contextual
    import AnimationMaker

    n2.addCommand(
        "  Animation Maker",
        lambda: show_info(
            None, "Animation Maker", "Right click on any knob and select Animation Maker"
        ),
        icon=icon_Knobs,
    )

add_tool(
    n2,
    label="  Multi Knob Edit",
    key="MultiKnobEdit",
    module="wbMultiKnobEdit",
    attr="multiEditExec",
    shortcut="F12",
    icon=icon_Knobs,
)

if is_enabled("Default_KnobDefaults"):
    # Sin try/except para que falle si hay error
    from default.default import default_main, helper

    _export_to_main(default_main=default_main)

    n2.addCommand(
        "  Edit Default Knobs Values",
        default_main.show_defaults_window,
        icon=icon_Knobs,
    )
    nuke.menu("Animation").addCommand(
        "default/set as new knobDefault", "default_main.create_default()"
    )
    nuke.menu("Animation").addCommand(
        "default/show knob list", "default_main.show_knob_list()"
    )
    nuke.menu("Animation").addCommand(
        "default/reset", "default_main.reset_to_default()"
    )
    helper.load_knob_defaults(init=True)


# -----------------------------------------------------------------------------
#                                 VA TOOLS
# -----------------------------------------------------------------------------
n2.addSeparator()
n2.addCommand("VA", lambda: None)
icon_VA = _get_icon("TP_VA")

add_tool(
    n2,
    label="  OCIOFileTransform Setup",
    key="OCIOFileTransform_IP",
    module="LGA_OCIOFileTransform_IP",
    attr="setup_ocio_file_transform",
    shortcut="ctrl+alt+shift+i",
    icon=icon_VA,
    context=2,
)

add_tool(
    n2,
    label="  CDL -> CC Input Process",
    key="CDL_CC_IP",
    module="LGA_CDL_CC_IP",
    attr="main",
    icon=icon_VA,
)

if is_enabled("Perf_Time"):
    # Sin try/except para que falle si hay error
    import perf_time

    _export_to_main(perf_time=perf_time)

    n2.addCommand("  Performance Timers", "perf_time.show_panel()", icon=icon_VA)
    pane_m = nuke.menu("Pane")
    pane_m.addCommand("Performance Timers", perf_time.add_perf_time_panel)
    nukescripts.registerPanel("com.lega.perfTime", perf_time.add_perf_time_panel)


if is_enabled("Shortcut_Editor"):
    # Sin try/except para que falle si hay error
    import shortcuteditor
    from shortcuteditor import gui

    shortcuteditor.nuke_setup()
    n2.addCommand("  Edit Keyboard Shortcuts", gui, icon=icon_VA)


# -----------------------------------------------------------------------------
#                                 Version
# -----------------------------------------------------------------------------
n2.addSeparator()


def _enable_tools_runner():
    import LGA_ToolPackB_EnabledPanel

    LGA_ToolPackB_EnabledPanel.main()


# A proposito NO pasa por is_enabled(): si el usuario apaga todo, este es el
# unico camino de vuelta. Un panel que se puede desactivar a si mismo deja al
# usuario sin forma de reactivar nada sin editar archivos a mano.
n2.addCommand("Enable Tools", _enable_tools_runner)

n2.addCommand(
    "Documentation v%s" % PRODUCT_VERSION,
    lambda: webbrowser.open("https://github.com/legandrop/LGA_ToolPack_B-for_Nuke"),
)
