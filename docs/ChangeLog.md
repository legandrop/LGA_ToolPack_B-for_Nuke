# Changelog

## v1.05
- El `menu.py` del pack se convierte en un wrapper mínimo que detecta los flags oficiales de Hiero y Nuke Studio antes de importar la implementación completa desde `LGA_ToolPackB_menu.py`. El pack mantiene una instalación simple mediante `pluginAddPath`, pero deja de crear paths, imports o menús dentro de los hosts de timeline. [ ToolPack B - Evitar carga en Hiero y Nuke Studio ]

- Se incorpora `VERSION` como fuente única de la versión publicada y el menú obtiene desde allí su label de documentación. Se normaliza el changelog dentro de `docs/`, se agregan reglas de desarrollo espejadas y se reserva el bump real para el generador manual de `LGA_Release`. [ ToolPack B - Unificar reglas, changelog y versión publicada ]

## v1.04
- Changelog inicial creado para alinear la repo con la version actual visible en `README.md`. [ ToolPack B - Crear changelog inicial ]
