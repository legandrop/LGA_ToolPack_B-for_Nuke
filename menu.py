"""
_____________________________________

  LGA_ToolPack B v2.4 | Lega
  Colección de herramientas de Nuke
_____________________________________

"""

import nuke
import nukescripts
import os
import importlib
import configparser
import webbrowser

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
PY_DIR = os.path.join(ROOT_DIR, "py")
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

# Carga los modulos runtime desde py/
nuke.pluginAddPath(PY_DIR.replace("\\", "/"))


# --- Config loader & helpers (igual que ToolPack) ----------------------------


def _ini_paths():
    home = os.path.expanduser("~")
    user_ini = os.path.join(home, ".nuke", "_LGA_ToolPack-B_Enabled.ini")
    pkg_ini = os.path.join(ROOT_DIR, "_LGA_ToolPack-B_Enabled.ini")
    return user_ini, pkg_ini


_TOOL_FLAGS = None


def load_tool_flags():
    """Lee el INI (user pisa a package). Si falta/rompe => todo True."""
    global _TOOL_FLAGS
    if _TOOL_FLAGS is not None:
        return _TOOL_FLAGS

    cfg = configparser.ConfigParser()
    cfg.optionxform = str
    user_ini, pkg_ini = _ini_paths()
    read_ok = False
    for path in [pkg_ini, user_ini]:
        if os.path.isfile(path):
            try:
                cfg.read(path, encoding="utf-8")
                read_ok = True
            except Exception:
                pass

    flags = {}
    if read_ok and cfg.has_section("Tools"):
        for key, val in cfg.items("Tools"):
            v = str(val).strip().lower()
            flags[key] = v in ("1", "true", "yes", "on")
    _TOOL_FLAGS = flags
    return _TOOL_FLAGS


def is_enabled(key: str) -> bool:
    return load_tool_flags().get(key, True)


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
#                                 NODE BUILDS
# -----------------------------------------------------------------------------
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
        lambda: nuke.message(
            "Right click on any knob and select Animation Maker"
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

TPB_pdf_path = os.path.join(DOCS_DIR, "LGA_ToolPack-B.pdf")

n2.addCommand("Documentation v2.3", lambda: webbrowser.open("file://" + TPB_pdf_path))
