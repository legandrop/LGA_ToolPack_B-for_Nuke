<p>
  <img src="Doc_Media/image1.png" alt="LGA Tool Pack logo" width="56" height="56" align="left" style="margin-right:8px;">
  <span style="font-size:1.6em;font-weight:700;line-height:1;">LGA TOOL PACK B</span><br>
  <span style="font-style:italic;line-height:1;">Lega | v2.4</span>
</p>
<br clear="left">





## Instalación

- Copiar la carpeta **LGA_ToolPack-B** que contiene todos los
  archivos **.py** a **%USERPROFILE%/.nuke**.

- Con un editor de texto, agregar esta línea de código al archivo
  **init.py** que está dentro de la carpeta **.nuke**:

  ```
  nuke.pluginAddPath('./LGA_ToolPack-B')
  ```

- El ToolPack permite **activar/desactivar** herramientas sin tocar
  código editando el archivo **\_LGA_ToolPack-B_Enabled.ini**
  (dentro de **LGA_ToolPack-B**/).\
  Por defecto todas las herramientas están en **True**. Cambiar a
  **False** las oculta y evita cargar su script.\
  Para conservar la configuración en futuras actualizaciones, se puede
  copiar el archivo a **\~/.nuke/\_LGA_ToolPack-B_Enabled.ini**. Si
  existen ambos, tiene prioridad el de **\~/.nuke/.**

<br><br>

## <span style="color:#a9ab13;">READ n WRITE</span>



## <img src="Doc_Media/image7.png" alt="" width="7" height="12"> Media Missing Frames v1.1 - Lega | *Ctrl + Alt + Shift + M*

Escanea todos los nodos Read del script y detecta secuencias EXR con frames faltantes.

Muestra una tabla con la ruta del archivo, el nombre del Read, el rango detectado y los frames ausentes para localizar rápidamente problemas de media antes de renderizar o publicar.





<br><br>

## <img src="Doc_Media/image7.png" alt="" width="7" height="12"> Reload all Reads v1.0 - Lega | *Ctrl + Alt + Shift + R*

Ejecuta el comando **reload** sobre todos los nodos Read del script actual.

Útil cuando se actualizó media en disco y se quiere refrescar todo el proyecto de una sola vez.





<br><br>

## <img src="Doc_Media/image7.png" alt="" width="7" height="12"> Rename Writes from Reads v1.0 - Lega | *F2*

Renombra los nodos Write seleccionados usando el nombre del archivo del Read conectado aguas arriba.

Elimina el padding final después del último guion bajo para dejar un nombre más limpio y consistente en los Writes.





<br><br>

## <img src="Doc_Media/image7.png" alt="" width="7" height="12"> Media path replacer v1.6 - Lega

Para cuando hay missing media porque se cambió la ubicación del proyecto y su media.

Permite buscar y reemplazar rutas en los nodos Read y Write. Da la opción de filtrar listas, incluir sólo nodos Read o Write, y tiene un sistema de presets para guardar y cargar configuraciones frecuentes.

Útil para actualizar rutas de archivos cuando se mueven proyectos a otras carpetas o discos.





<br><br>

## <span style="color:#135eab;">FRAME RANGE</span>

## <img src="Doc_Media/image8.png" alt="" width="7" height="12"> Read -> FrameRange v1.0 - Lega | *Ctrl + Alt + F*

Copia el rango de frames de un nodo Read seleccionado a uno o más nodos FrameRange seleccionados.

La herramienta requiere seleccionar exactamente un Read y al menos un FrameRange.





<br><br>

## <img src="Doc_Media/image8.png" alt="" width="7" height="12"> Read -> Write v1.0 - Lega

Activa **use limit** en todos los nodos Write del script y ajusta su rango para que coincida con el frame range detectado en su contexto actual.

Sirve para dejar los Writes limitados al rango correcto sin editar cada nodo manualmente.





<br><br>

## <img src="Doc_Media/image8.png" alt="" width="7" height="12"> TimeClip -> Write v1.0 - Lega | *Ctrl + T*

Copia el rango de frames de un nodo TimeClip al nodo Write seleccionado.

La herramienta requiere seleccionar exactamente un Write y un TimeClip.





<br><br>

## <span style="color:#4dcb9d;">COPY n PASTE</span>

## <img src="Doc_Media/image18.png" alt="" width="7" height="12"> Paste to selected v1.1 - Frank Rueter | *Ctrl + Shift + V*

[http://www.nukepedia.com/python/nodegraph/pastetoselected](http://www.nukepedia.com/python/nodegraph/pastetoselected)

Pega los nodos del portapapeles a todos los nodos seleccionados.

![](Doc_Media/image30.png)

![](Doc_Media/image26.png)





<br><br>

## <img src="Doc_Media/image18.png" alt="" width="7" height="12"> Duplicate with inputs v1.3 - Marcel Pichert

[http://www.nukepedia.com/python/nodegraph/duplicate-with-inputs](http://www.nukepedia.com/python/nodegraph/duplicate-with-inputs)

Duplica los nodos seleccionados y mantiene todas sus conexiones con nodos que no están en la selección. Se pueden duplicar los nodos directamente o copiarlos primero y pegarlos en otro lugar del script más tarde.

![](Doc_Media/image20.png)

![](Doc_Media/image10.png)



**Shortcut**

Ctrl + Alt + C Copy with inputs

Ctrl + Alt + V Paste with inputs

Ctrl + Alt + K Duplicate with inputs

<br><br>

## <span style="color:#cb944d;">NODE BUILDS</span>

Esta sección agrupa herramientas para construir setups, editar knobs o acelerar tareas repetitivas dentro del script.



## <img src="Doc_Media/image5.png" alt="" width="7" height="12"> DasGrain Kronos Comp v1.1 - Lega

Sincroniza la intensidad del grano de un nodo **DasGrain** con la interpolación de un nodo **Kronos**.

Agrega un tab **KroComp** al DasGrain seleccionado, crea knobs de control y modifica la expresión del knob **luminance** para compensar el grano en frames interpolados.





<br><br>

## <img src="Doc_Media/image5.png" alt="" width="7" height="12"> Animation Maker v1.4 - David Emeny 2021

Agrega un editor visual para construir expresiones de animación con eases, loops y waves sobre knobs animables.

Se accede desde el menú contextual de cualquier knob animable con **Right click > Animation Maker**.





<br><br>

## <img src="Doc_Media/image5.png" alt="" width="7" height="12"> Multi Knob Edit - Thorsten Loeffler | *F12*

Permite editar un mismo knob sobre múltiples nodos al mismo tiempo desde una sola interfaz.

Es útil para cambios masivos rápidos cuando hay que igualar parámetros entre varios nodos seleccionados.





<br><br>

## <img src="Doc_Media/image5.png" alt="" width="7" height="12"> Edit Default Knobs Values

Abre una ventana para definir, listar y resetear valores por defecto de knobs en Nuke.

Incluye integración con el menú **Animation** para crear nuevos `knobDefault`, revisar la lista activa y restaurar valores.





<br><br>

## <span style="color:#cb4d82;">VA</span>

## <img src="Doc_Media/image13.png" alt="" width="7" height="12"> OCIOFileTransform Setup v1.0 - Lega | *Ctrl + Alt + Shift + I*

Duplica un nodo **OCIOFileTransform** seleccionado, conserva su configuración y prepara una copia rotulada como **MOV Render**.

Además asigna el nodo original como **Input Process** en los viewers disponibles para acelerar el setup de visualización y render.





<br><br>

## <img src="Doc_Media/image13.png" alt="" width="7" height="12"> CDL -> CC Input Process v1.0 - Lega

Lee un archivo CDL desde un nodo **Read** u **OCIOCDLTransform**, genera un archivo **.cc** y crea nodos **OCIOFileTransform** para usarlo tanto en render como en el Input Process del viewer.

Sirve para convertir grades CDL en un setup práctico de visualización y salida dentro del script.





<br><br>

## <img src="Doc_Media/image13.png" alt="" width="7" height="12"> Performance Timers

Abre un panel con controles para iniciar, detener y resetear los performance timers de Nuke.

También registra el panel dentro del menú **Pane** para dejarlo disponible como panel acoplable.





<br><br>

## <img src="Doc_Media/image13.png" alt="" width="7" height="12"> Edit Keyboard Shortcuts - shortcuteditor v1.2

Abre una interfaz para revisar y editar shortcuts del menú de Nuke.

La herramienta se integra al arranque del ToolPack-B y permite redefinir teclas sin editar manualmente `menu.py`.





<br><br>

## Referencias técnicas

- [/Users/leg4/.nuke/LGA_ToolPack-B/menu.py](/Users/leg4/.nuke/LGA_ToolPack-B/menu.py): `load_tool_flags()`, `is_enabled()`, `add_tool()`, registro del menú `TP2` y agrupación por categorías.
- [/Users/leg4/.nuke/LGA_ToolPack-B/_LGA_ToolPack-B_Enabled.ini](/Users/leg4/.nuke/LGA_ToolPack-B/_LGA_ToolPack-B_Enabled.ini): flags de activación y desactivación por herramienta.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_mediaMissingFrames.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_mediaMissingFrames.py): clase `ReadNodeInfo`, métodos `load_data()` y `adjust_window_size()`, entrada `main()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_reloadAllReads.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_reloadAllReads.py): función `main()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_renameWritesFromReads.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_renameWritesFromReads.py): función `renameWrite()`, helpers `get_file_name_without_extension()`, `remove_padding()`, `find_top_read_node()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_mediaPathReplacer.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_mediaPathReplacer.py): UI principal del buscador/reemplazador de paths y manejo de presets.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_fr_Read_to_FrameRange.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_fr_Read_to_FrameRange.py): función `set_frame_range_from_read()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_fr_Read_to_Write.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_fr_Read_to_Write.py): función `Writes_FrameRange()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_fr_TimeClip_to_Write.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_fr_TimeClip_to_Write.py): función `set_write_from_timeclip()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/pasteToSelected.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/pasteToSelected.py): función `pasteToSelected()` y helper `toggleSelection()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/duplicateWithInputs.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/duplicateWithInputs.py): funciones `copyWithInputs()`, `pasteWithInputs()` y `duplicateWithInputs()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_DasGrain_Kronos_Comp.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_DasGrain_Kronos_Comp.py): funciones `add_amount_knobs()` y `main()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/AnimationMaker.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/AnimationMaker.py): `showWindow()`, `remove_tab()` y registro de menú contextual para knobs animables.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/wbMultiKnobEdit.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/wbMultiKnobEdit.py): función `multiEditExec()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/default/default/default_main.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/default/default/default_main.py): `show_defaults_window()`, `create_default()`, `show_knob_list()`, `reset_to_default()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/default/default/helper.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/default/default/helper.py): `load_knob_defaults()` y helpers del sistema de defaults.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_OCIOFileTransform_IP.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_OCIOFileTransform_IP.py): función `setup_ocio_file_transform()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_CDL_CC_IP.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_CDL_CC_IP.py): función `main()`, `read_cdl_values()` y generación de archivo `.cc`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/perf_time.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/perf_time.py): clase `PerfTime`, funciones `show_panel()` y `add_perf_time_panel()`.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/shortcuteditor.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/shortcuteditor.py): `nuke_setup()`, `gui()` y widgets del editor de shortcuts.
- [/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_QtAdapter_ToolPackB.py](/Users/leg4/.nuke/LGA_ToolPack-B/py/LGA_QtAdapter_ToolPackB.py): compatibilidad Qt entre Nuke 15 y Nuke 16, helpers `primary_screen_geometry()`, `horizontal_advance()` y `set_layout_margin()`.




