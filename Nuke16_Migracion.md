# Plan de migración Nuke 15 → Nuke 16 (PySide2 → PySide6) — ToolPack-B

## Estrategia
- Usar helper de compatibilidad (`LGA_QtAdapter_ToolPackB.py`) con funciones helper avanzadas y fallback PySide6 → PySide2.
- Funciones helper automatizan cambios de API: `horizontal_advance()`, `primary_screen_geometry()`, `set_layout_margin()`.
- Sustituir APIs Qt5 deprecadas: `QDesktopWidget`, `QFontMetrics.width`, `QtGui.QWidget` legacy, mezclas QtGui/QtWidgets.
- Mantener compatibilidad Nuke 15/16 con imports protegidos (`try/except`) o helper único.

## Archivos que requieren migración
- [ ] `AnimationMaker.py` — UI extensa con imports PySide/PySide2 y alias `QtGuiWidgets`; unificar imports via `LGA_QtAdapter_ToolPackB`, revisar señales/timers/QGraphics para Qt6.
- [ ] `default/default_main.py` — PySide2/PySide directo; depende de `helper.center` (usa `QDesktopWidget`), dialogs Qt5; mover a `LGA_QtAdapter_ToolPackB` y geometry con `QGuiApplication`.
- [ ] `default/default/helper.py` — PySide2/PySide directo; `center()` usa `QtWidgets.QDesktopWidget`; migrar a `QGuiApplication.primaryScreen()/screenAt`, actualizar imports y `QMessageBox`.
- [ ] `default/default/about.py` — PySide2/PySide directo; migrar imports a `LGA_QtAdapter_ToolPackB`.
- [ ] `LGA_mediaPathReplacer.py` — PySide2 UI (QApplication global), usa `QFontMetrics.width` (deprecado en Qt6), QDialog/QTableWidget; mover a `LGA_QtAdapter_ToolPackB`, cambiar a `horizontalAdvance`, asegurar primaryScreen.
- [ ] `LGA_mediaMissingFrames.py` — PySide2 UI (QTableWidget), usa `QScreen`/`QApplication.primaryScreen`; migrar a `LGA_QtAdapter_ToolPackB` y evitar `QDesktopWidget`.
- [ ] `shortcuteditor.py` — Usa Qt.py o PySide2/PySide; `undercursor()` usa `QDesktopWidget`; normalizar imports via `LGA_QtAdapter_ToolPackB`, revisar `QKeySequence`, timers y señales en Qt6.
- [ ] `wbMultiKnobEdit.py` — PySide/PySide2 fallback; reemplazar imports por `LGA_QtAdapter_ToolPackB`, validar flags de ventana en Qt6.

## Scripts sin cambios de migración (solo Nuke/Python, sin Qt)
- `menu.py`, `perf_time.py`
- `LGA_CDL_CC_IP.py`, `LGA_DasGrain_Kronos_Comp.py`, `LGA_fr_Read_to_FrameRange.py`, `LGA_fr_Read_to_Write.py`, `LGA_fr_TimeClip_to_Write.py`, `LGA_LC_CDLpy`
- `LGA_OCIOFileTransform_IP.py`, `LGA_reloadAllReads.py`, `LGA_renameWritesFromReads.py`

## Notas rápidas
- `LGA_QtAdapter_ToolPackB.py` incluye funciones helper avanzadas unificadas en todos los ToolPacks.
- Para geometría de pantalla usar `LGA_QtAdapter_ToolPackB.primary_screen_geometry(pos)` (maneja automáticamente QDesktopWidget vs QGuiApplication).
- Para ancho de texto usar `LGA_QtAdapter_ToolPackB.horizontal_advance(metrics, text)` (compatible Qt5/Qt6 automáticamente).
- Para márgenes de layout usar `LGA_QtAdapter_ToolPackB.set_layout_margin(layout, margin)` (compatible Qt5/Qt6 automáticamente).
- Garantizar una sola instancia de `QApplication` (AnimationMaker, mediaMissingFrames, mediaPathReplacer).
