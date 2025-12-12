# Plan de migración Nuke 15 → Nuke 16 (PySide2 → PySide6) — ToolPack-B

## Estrategia
- Usar helper de compatibilidad (`qt_compat` ya usado en ToolPack/ToolPack-Layout) con fallback PySide6 → PySide2 y alias de QtWidgets/QtGui/QtCore/QAction/QGuiApplication.
- Sustituir APIs Qt5 deprecadas: `QDesktopWidget`, `QFontMetrics.width`, `QtGui.QWidget` legacy, mezclas QtGui/QtWidgets.
- Mantener compatibilidad Nuke 15/16 con imports protegidos (`try/except`) o helper único.

## Archivos que requieren migración
- [ ] `AnimationMaker.py` — UI extensa con imports PySide/PySide2 y alias `QtGuiWidgets`; unificar imports via `qt_compat`, revisar señales/timers/QGraphics para Qt6.
- [ ] `default/default_main.py` — PySide2/PySide directo; depende de `helper.center` (usa `QDesktopWidget`), dialogs Qt5; mover a `qt_compat` y geometry con `QGuiApplication`.
- [ ] `default/default/helper.py` — PySide2/PySide directo; `center()` usa `QtWidgets.QDesktopWidget`; migrar a `QGuiApplication.primaryScreen()/screenAt`, actualizar imports y `QMessageBox`.
- [ ] `default/default/about.py` — PySide2/PySide directo; migrar imports a `qt_compat`.
- [ ] `LGA_mediaPathReplacer.py` — PySide2 UI (QApplication global), usa `QFontMetrics.width` (deprecado en Qt6), QDialog/QTableWidget; mover a `qt_compat`, cambiar a `horizontalAdvance`, asegurar primaryScreen.
- [ ] `LGA_mediaMissingFrames.py` — PySide2 UI (QTableWidget), usa `QScreen`/`QApplication.primaryScreen`; migrar a `qt_compat` y evitar `QDesktopWidget`.
- [ ] `shortcuteditor.py` — Usa Qt.py o PySide2/PySide; `undercursor()` usa `QDesktopWidget`; normalizar imports via `qt_compat`, revisar `QKeySequence`, timers y señales en Qt6.
- [ ] `wbMultiKnobEdit.py` — PySide/PySide2 fallback; reemplazar imports por `qt_compat`, validar flags de ventana en Qt6.

## Scripts sin cambios de migración (solo Nuke/Python, sin Qt)
- `menu.py`, `perf_time.py`
- `LGA_CDL_CC_IP.py`, `LGA_DasGrain_Kronos_Comp.py`, `LGA_fr_Read_to_FrameRange.py`, `LGA_fr_Read_to_Write.py`, `LGA_fr_TimeClip_to_Write.py`, `LGA_LC_CDLpy`
- `LGA_OCIOFileTransform_IP.py`, `LGA_reloadAllReads.py`, `LGA_renameWritesFromReads.py`

## Notas rápidas
- Reutilizar el mismo `qt_compat.py` ya presente en ToolPack/ToolPack-Layout.
- Reemplazar `QDesktopWidget` por `QGuiApplication.primaryScreen()` y `screenAt(pos) or primaryScreen()`; usar `availableGeometry()` sin argumentos en Qt6.
- Cambiar `QFontMetrics.width` → `horizontalAdvance` con fallback.
- Garantizar una sola instancia de `QApplication` (AnimationMaker, mediaMissingFrames, mediaPathReplacer).***
