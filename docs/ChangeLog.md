# Changelog

## v1.09

- Nuevo `py/LGA_UI_Style_ToolPackB.py`: fuente unica de la paleta, las medidas y el QSS de las ventanas del pack. Es codigo identico al modulo de los otros dos packs a proposito: son repos independientes y un usuario puede tener instalado uno solo, asi que no pueden importarse entre si, pero un color cambiado tiene que cambiar en los tres. Trae ademas el coloreado de paths por nivel de directorio, con la misma paleta que usan las apps Qt/C++ de LGA. [ ToolPack B - Agregar el modulo de estilo unificado ]

- Los titulos de grupo de `Enable Tools` con un `&` salian con el `&` comido y un espacio de mas: Qt lo lee como marca de mnemonico. Con el grupo sin marco pasaba desapercibido; ahora que el titulo va enmarcado se nota. Ademas, el CSS del tooltip lo aplicaba un helper que vive solo en el ToolPack, asi que este pack dependia de tener ese otro instalado para que sus tooltips se vieran bien: si falta, ahora los pinta con los mismos valores desde su propio modulo de estilo. [ ToolPack B - Corregir el & de los titulos y los tooltips sin el helper ]

- `Enable Tools` pasa a ese modulo. Antes no aplicaba ninguna hoja de estilo, asi que heredaba el tema de Nuke y era la ventana del pack que menos se parecia a las demas: ahora cada grupo de herramientas tiene marco y titulo propios, el boton `Save` es el violeta del pack y el resto van grises, y el path del archivo de configuracion va coloreado por nivel de directorio. [ ToolPack B - Unificar el estilo de Enable Tools ]

## v1.08

- Las herramientas que el usuario apagaba se perdian en cada actualizacion: el estado vivia adentro del pack, en `_LGA_ToolPack-B_Enabled.ini`, y el instalador renombra esa carpeta y copia la version nueva limpia. Ese archivo pasa a ser `Enabled.default.ini`, solo el manifiesto de fabrica, y la eleccion del usuario se guarda afuera: `%APPDATA%\LGA\ToolPack_B\Enabled.ini`, o bajo `~/Library/Application Support` en macOS. Ahi se guarda unicamente lo que difiere del manifiesto, asi agregar o borrar tools entre versiones no deja claves muertas. Se agrega el menu **TP2 > Enable Tools**, con un checkbox por herramienta. La config existente se migra sola en el primer arranque y el ini viejo de `.nuke` no se toca. `CopyCat_Cleaner` y `Paste_To_Selected` se heredan del ini historico de LGA_ToolPack, donde vivian antes. [ ToolPack-B - Mover la config de tools fuera del pack y agregar Enable Tools ]

## v1.07
- El `install.pdf` se reemplaza por `install_es.pdf` e `install_en.pdf`. La hoja vieja salia de exportar un Google Doc a mano y quedo congelada en el metodo manual: no menciona los instaladores que el ZIP trae desde hace varias versiones, y ademas daba el backup del `init.py` como `init.py.bak`, un nombre que los motores ya no usan: hoy guardan una copia numerada en `~/.nuke/LGA_init_backups/`. Las dos hojas se generan ahora desde una plantilla unica en el repo de release, con la version leida del `VERSION` del repo, asi que el texto comun deja de mantenerse por separado en cada producto. Se documenta tambien que en macOS el instalador va con `bash installer_mac.sh`: los `.sh` pierden el permiso de ejecucion dentro del `.zip` y `./installer_mac.sh` da `Permission denied`. [ ToolPack-B - Reemplazar install.pdf por las hojas en castellano e ingles ]

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
