"""
_____________________________________________________________________________________________

  LGA_OCIOFileTransform_IP v1.01 | Lega
  Duplica un OCIOFileTransform seleccionado, configura labels y asigna Input Process

  v1.01: Los carteles salen del helper de carteles del pack (warning
         para seleccion invalida, error para fallos), con fallback.
  v1.00: Version anterior (v1.0), sin changelog interno.
_____________________________________________________________________________________________

"""

import nuke

# Carteles estilados del pack. Con fallback al cartel de Nuke: este script
# tiene que correr aunque el helper no este instalado.
try:
    from LGA_UI_MessageBox_ToolPackB import show_warning, show_error
except ImportError:

    def show_warning(parent, title, text):
        nuke.message(text)

    def show_error(parent, title, text):
        nuke.message(text)


def setup_ocio_file_transform():
    """
    Configura un OCIOFileTransform seleccionado como Input Process y crea una copia para render MOV
    """

    # Obtener nodos seleccionados
    selected_nodes = nuke.selectedNodes()

    # Verificar que hay exactamente un nodo seleccionado
    if len(selected_nodes) != 1:
        show_warning(None, "OCIOFileTransform Setup", "Debes seleccionar exactamente un nodo OCIOFileTransform.")
        return

    selected_node = selected_nodes[0]

    # Verificar que es un OCIOFileTransform
    if selected_node.Class() != "OCIOFileTransform":
        show_warning(None, "OCIOFileTransform Setup", "El nodo seleccionado debe ser un OCIOFileTransform.")
        return

    print(f"Procesando OCIOFileTransform: {selected_node.name()}")

    # Deseleccionar todos los nodos
    for node in nuke.allNodes():
        node["selected"].setValue(False)

    # Duplicar el nodo OCIOFileTransform
    try:
        duplicate_node = nuke.createNode("OCIOFileTransform")

        # Copiar todos los valores del nodo original
        for knob_name in selected_node.knobs():
            if knob_name in duplicate_node.knobs():
                try:
                    if knob_name not in ["name", "selected", "xpos", "ypos"]:
                        original_value = selected_node[knob_name].value()
                        duplicate_node[knob_name].setValue(original_value)
                except Exception as e:
                    print(f"No se pudo copiar knob '{knob_name}': {str(e)}")

        # Configurar el label del duplicado como "MOV Render"
        duplicate_node["label"].setValue("MOV Render")

        # Posicionar el duplicado debajo del original
        original_x = selected_node.xpos()
        original_y = selected_node.ypos()
        duplicate_node.setXYpos(original_x, original_y + 100)

        print(f"Nodo duplicado creado: {duplicate_node.name()}")

        # Seleccionar el nodo original
        selected_node["selected"].setValue(True)

        # Asignar el nodo original como Input Process al viewer activo
        input_process_assigned = False
        for viewer in nuke.allNodes("Viewer"):
            viewer["input_process_node"].setValue(selected_node.name())
            input_process_assigned = True
            print(
                f"Nodo '{selected_node.name()}' asignado como Input Process en {viewer.name()}"
            )

        if not input_process_assigned:
            print(
                "Advertencia: No se encontro ningun nodo Viewer activo para asignar Input Process"
            )

        # Seleccionar ambos nodos para que el usuario los vea
        selected_node["selected"].setValue(True)
        duplicate_node["selected"].setValue(True)

        print(
            """
=== CONFIGURACION COMPLETA ==="""
        )
        print(f"✓ Nodo original: {selected_node.name()} - Input Process")
        print(f"✓ Nodo duplicado: {duplicate_node.name()} - MOV Render")
        print("✓ Ambos nodos seleccionados para visualizacion")

    except Exception as e:
        show_error(None, "OCIOFileTransform Setup", f"Error al duplicar el nodo: {str(e)}")
        print(f"Error: {str(e)}")
        return


# Llamar a la funcion si el script se ejecuta directamente
if __name__ == "__main__":
    setup_ocio_file_transform()
