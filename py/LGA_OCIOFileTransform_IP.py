"""
_____________________________________________________________________________________________

  LGA_OCIOFileTransform_IP v1.0 | Lega
  Duplica un OCIOFileTransform seleccionado, configura labels y asigna Input Process
_____________________________________________________________________________________________

"""

import nuke


def setup_ocio_file_transform():
    """
    Configura un OCIOFileTransform seleccionado como Input Process y crea una copia para render MOV
    """

    # Obtener nodos seleccionados
    selected_nodes = nuke.selectedNodes()

    # Verificar que hay exactamente un nodo seleccionado
    if len(selected_nodes) != 1:
        nuke.message("Debes seleccionar exactamente un nodo OCIOFileTransform.")
        return

    selected_node = selected_nodes[0]

    # Verificar que es un OCIOFileTransform
    if selected_node.Class() != "OCIOFileTransform":
        nuke.message("El nodo seleccionado debe ser un OCIOFileTransform.")
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
        nuke.message(f"Error al duplicar el nodo: {str(e)}")
        print(f"Error: {str(e)}")
        return


# Llamar a la funcion si el script se ejecuta directamente
if __name__ == "__main__":
    setup_ocio_file_transform()
