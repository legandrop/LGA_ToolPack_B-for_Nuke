> **Regla de documentacion**: este archivo describe el estado actual del codigo. No es un historial de cambios, changelog ni bitacora temporal.
> **Regla de documentacion**: este archivo debe incluir una seccion de referencias tecnicas con rutas completas a los archivos mas importantes relacionados, y para cada archivo nombrar las funciones, clases o metodos clave vinculados a este tema.

# AMF (Apply AMF) — LGA ToolPack-B

Entrada `AMF` del menu NODE BUILDS (key `ApplyAMF`, modulo `LGA_ApplyAMF`). Crea en el Node Graph la cadena de color del shot a partir de lo que hay en `<shot>/_input/Look_Files`. Es la contraparte en Nuke del boton Apply AMF de HieroTools, que hace lo mismo con soft effects sobre los clips del timeline.

La tool NO es un toggle: cada corrida crea nodos nuevos debajo del nodo seleccionado y no reconoce ni saca los de corridas anteriores. El ciclo de poner y sacar (con la deteccion por la ruta de `Look_Files`) es de la version de HieroTools.

## Que archivos entiende

| Archivo | Nodo | De donde sale el working space |
|---|---|---|
| `.amf` | uno por cada `lookTransform` con `applied="false"` | del propio `.amf`; si no declara, ACES2065-1 |
| `.cdl` | `OCIOCDLTransform` | del `<cdlWorkingSpace>` del `.amf`; sin `.amf`, el default del nodo |
| `.clf` | `OCIOFileTransform` | ACES2065-1 (un LMT `.clf` entra y sale en AP0) |
| `.cube` | `OCIOFileTransform` | del nombre del archivo; sin pista, ACEScct (ver abajo) |

## Prioridad entre formatos

1. **El `.amf` manda.** Si hay uno, el plan sale de el: orden, `applied`, working space y archivos. El `.cdl` es el hermano del `.amf` elegido.
2. Sin `.amf`, plan fijo por extension: un `.cdl` y un `.clf` (el primero si hay varios, con aviso en el log).
3. **El `.cube` solo entra cuando `Look_Files` no tiene NINGUN `.amf`, `.cdl` ni `.clf`.** Es el look de los shows que no usan esos formatos, no un agregado a ellos: apilar un `.cube` sobre la cadena de un `.amf` aplicaria el look dos veces. Consecuencia buscada: con un `.amf` cuyo plan queda vacio (todo ya aplicado en el plate) NO se cae al `.cube`; sale el cartel de "Nothing to apply".
4. Un `.cube` que un `.amf` nombra en su `<file>` entra por el camino del `.amf` (con ACES2065-1, el espacio de la cadena del `.amf`), no por este.

## Varios `.cube`

Se queda la version mas alta de cada LUT (`scan_look_entries`). A diferencia de un `.amf`, donde el token anterior a `_vNNN` es el plate, en un `.cube` ese token no identifica nada: `PROJA_Preview_LMT_v001.cube` y `PROJA_Final_LMT_v001.cube` son dos LUT distintos aunque los dos terminen en `LMT`. Por eso la clave de agrupado es el nombre ENTERO sin el `_vNNN` final (`parse_lut_name`): `X_LMT_v001.cube` y `X_LMT_v002.cube` son una sola entrada (la v002) y los dos anteriores son dos entradas. Los nombres sin `_vNNN` final son cada uno su propia entrada. Si queda una sola, se usa sin preguntar; si quedan varias, el cartel de eleccion de los `.amf` (`pick_plate`) se reutiliza con titulo "Select LUT". No hay ventana nueva. Esc cancela la corrida entera.

## Working space de un `.cube`

Un `.cube` es un LUT 1D/3D pelado: no trae metadata y no declara en que espacio espera su entrada. El knob `working_space` de `OCIOFileTransform` no dice "la entrada esta en", dice "aplicalo en": el nodo convierte de `scene_linear` a ese espacio, aplica el archivo y vuelve. Entonces hay que elegir un espacio, y se elige asi:

1. Si el **nombre** lo dice, ese: `ACEScct`, `ACEScc`, `ACEScg` (o `AP1`), `ACES2065` (o `AP0` o `Linear`, que se leen como lineal ACES). Sin distinguir mayusculas, con cualquier separador (`_`, `-`, `.`, espacio) y sin exigirlo antes de un numero (`ACEScct65` sirve). No matchea adentro de otra palabra: `acescc` no se encuentra dentro de `acescct` ni `linear` dentro de `nonlinear`.
2. Si el nombre menciona varios (`ACEScg_to_ACEScct`), gana el **primero**, que por convencion es el de entrada. Queda un aviso en el log.
3. Si no dice nada, **ACEScct**. Es la convencion de los LMT en ACES (el `OCIOFileTransform` del look del shot en los templates de comp corre en ACEScct) y por eso no se usa el ACES2065-1 de los `.clf`, que si declaran su espacio.

El nombre que sale de esa regla es **logico** (`ACEScct`). El nombre real del colorspace lo resuelve `match_colorspace_option` contra las opciones del knob del config OCIO activo, que cambian de config en config (en aces_1.2 es `ACES - ACEScct`). Nunca se hardcodea un string de colorspace.

Si el config activo no expone ese espacio (proyecto sin color management ACES), pasa lo mismo que hoy con un `.clf`: el nodo queda en el default `scene_linear`, el `OCIOFileTransform` se crea igual y sube un cartel que dice que la cadena NO es correcta porque el config no tiene ese colorspace. El mismo cartel avisa si un nodo no pudo cargar su archivo (`.cube` vacio, corrupto o que dejo de existir). Un look aplicado en el espacio equivocado, informado como exito, es el peor final.

## Que se puede equivocar la regla

Es una **convencion**, no una lectura del archivo. Un `.cube` hecho para ACEScg que no lo diga en el nombre corre en ACEScct y sale mal sin avisar. La salvaguarda es el log (`logs/DebugPy_LGA_ApplyAMF.log` dice `working space: X, segun nombre|default`) y que el nombre del LUT diga el espacio. Si un show tiene un LUT sin pista que no es ACEScct, la solucion es renombrarlo, no cambiar la tool.

El `OCIOFileTransform` queda con `interpolation=linear` (el default del nodo), igual que con un `.clf`.

## Trampas medidas

- **Las opciones del enum `working_space` traen campos separados por TAB, y solo el primero es el nombre del colorspace.** En aces_1.2 es `ACES - ACEScct<TAB>Colorspaces/ACES/ACES - ACEScct`; en los configs v2 de Foundry de Nuke 17 (`fn-nuke_cg-config-v2.2.0_aces-v1.3`, `fn-nuke_studio-config-v2.2.0...`, los v3.0.0 de ACES 2.0) es `ACEScct<TAB>Colorspaces/ACES/ACEScct<TAB><TAB>ACES - ACEScct,acescct_ap1`. El knob ACEPTA la cadena entera y hasta la lee de vuelta como `ACEScct`, pero el nodo queda con `hasError=True`, el LUT no se aplica (pixel 0.0) y no sale ningun aviso. Medido en v2.2.0 con la cadena entera: `hasError=True`; con el nombre corto: `False` y pixel 0.014609. `match_colorspace_option` matchea contra el nombre corto y devuelve ese. Afecta a los `.clf`, `.cdl` y al camino del `.amf`, no solo al `.cube`.
- **aces_1.2 trae una familia `Utility/Aliases`** (`acescct`, `acescg`, `acescc`, `acescct_ap1`...) en minuscula. Matcheando por nombre corto ganarian por igualdad exacta antes que `ACES - ACEScct`, y el nodo quedaria con `acescct` (funciona, pero cambia el nombre que ve el usuario). Los alias se dejan para la ultima pasada.
- **Un nodo con archivo vacio, corrupto o inexistente queda con `hasError=True` sin avisar**: el `setValue` del knob `file` sale bien igual. `configure_node` mira `node.hasError()` despues de configurar y suma un motivo al cartel "NOT correct". Para medirlo, ojo: despues de un nodo con error `nuke.sample` devuelve 0.0 dentro del mismo envio al host, asi que los casos con error y los sanos se miden en envios separados.

- **OCIO cachea el LUT por ruta.** Reescribir un `.cube` en el mismo path y volver a crear el nodo en la misma sesion de Nuke devuelve el LUT viejo (medido: identidad tras x0.5 sobre el mismo archivo dio 0.0146 en vez de 0.18). No es un problema de la tool, pero un bench que regenere el LUT tiene que usar nombres distintos o el boton `reload` del nodo.
- Con un `.cube` x0.5 en ACEScct sobre gris 0.18 el resultado es 0.014609 (calculo independiente: 0.014609); en ACEScg, 0.09. Sirve para confirmar de un vistazo en que espacio esta corriendo.

## Referencias tecnicas

- `C:\Users\leg4-pc\.nuke\LGA_ToolPack-B\py\LGA_ApplyAMF.py`
  - `_main_interno`: flujo completo; la rama del `.cube` va despues de `build_effect_plan`.
  - `has_primary_look_files`: condicion de "no hay `.amf`, `.cdl` ni `.clf`".
  - `scan_look_entries` / `scan_amf_entries`: agrupado por plate y version.
  - `pick_cube`, `build_cube_plan`, `cube_working_space`: eleccion del `.cube` y su working space (`_CUBE_SPACE_HINTS`, `CUBE_DEFAULT_SPACE`).
  - `match_colorspace_option`, `configure_node`: resolucion del nombre corto contra el config OCIO, chequeo de `hasError` y cartel de "NOT correct".
  - `parse_lut_name`: clave de agrupado de los `.cube`.
  - `insert_chain`: ubicacion en el arbol (debajo del nodo seleccionado, reconecta lo que venia abajo).
- `C:\Users\leg4-pc\.nuke\LGA_ToolPack-B\py\LGA_ApplyAMF_Dialogs.py`
  - `pick_plate(parent, entries, extension)`, `_PickPlateDialog`: cartel de eleccion, textos segun `.amf` o `.cube`.
  - `ask_actions`: crear nodos / crear suelto como Input Process.
- Contraparte en HieroTools: `C:\Users\leg4-pc\.nuke\Python\Startup\LGA_HieroTools\LGA_NKS_Edit_Panel_py\LGA_NKS_ApplyAMF.py`.
