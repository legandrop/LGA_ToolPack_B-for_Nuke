# Changelog

## v1.06
- El instalador dejaba el `init.py` roto en cualquier equipo que tuviera sus `pluginAddPath` adentro de un bloque `if` —por ejemplo para discriminar por version de Nuke— y ademas reportaba exito. Al reordenar los paths se llevaba tambien las lineas indentadas, dejando el bloque sin cuerpo, y Nuke no arrancaba con un `IndentationError`. Ahora solo toca las lineas en columna 0 y respeta las indentadas donde estan. Suma ademas deduplicacion de paths repetidos, preservacion del BOM del archivo original y una validacion del resultado: si el `init.py` quedaria invalido, no lo modifica y aborta la instalacion. [ ToolPack-B - Corregir el manejo del init.py del instalador ]

## v1.05
- Se corrigen los comandos de menú de `default_main` (set as new knobDefault, show knob list, reset) y `perf_time.show_panel`, que fallaban con `NameError`. Al mover la implementación de `menu.py` a `LGA_ToolPackB_menu.py`, los imports pasaron a vivir en el namespace del módulo, pero Nuke evalúa los comandos pasados como string dentro de `__main__`, donde esos nombres ya no existían. Se agrega el helper `_export_to_main()` y se publica ahí cada módulo usado por un comando string. [ ToolPack B - Reparar comandos de menu tras mover la implementacion ]

- El instalador ordena `~/.nuke/init.py` de forma canónica en Windows y macOS: recolecta todos los bloques `pluginAddPath` de LGA, los reordena según el orden oficial (Layout, ToolPack-B, ToolPack, NodePack, OpenInNukeX, Defaults, CollectedTools), elimina duplicados y deja intactos los paths ajenos. Antes cada plataforma resolvía el orden de una manera distinta y macOS simplemente agregaba al final. [ ToolPack B - Unificar el orden del init.py ]

- Se agregan instaladores transaccionales para Windows y macOS, con validación del payload, backup de la carpeta previa, actualización idempotente de `init.py` y restauración ante fallos. Los generadores de release incluyen ambos instaladores y aplican exclusiones seguras aunque no exista un `+exclude.lst` local. [ ToolPack B - Agregar instaladores multiplataforma ]

- El `menu.py` del pack se convierte en un wrapper mínimo que detecta los flags oficiales de Hiero y Nuke Studio antes de importar la implementación completa desde `LGA_ToolPackB_menu.py`. El pack mantiene una instalación simple mediante `pluginAddPath`, pero deja de crear paths, imports o menús dentro de los hosts de timeline. [ ToolPack B - Evitar carga en Hiero y Nuke Studio ]

- Se incorpora `VERSION` como fuente única de la versión publicada y el menú obtiene desde allí su label de documentación. Se normaliza el changelog dentro de `docs/`, se agregan reglas de desarrollo espejadas y se reserva el bump real para el generador manual de `LGA_Release`. [ ToolPack B - Unificar reglas, changelog y versión publicada ]

## v1.04
- Changelog inicial creado para alinear la repo con la version actual visible en `README.md`. [ ToolPack B - Crear changelog inicial ]
