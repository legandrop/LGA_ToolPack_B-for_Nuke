"""
_____________________________________________________________________________________________

  LGA_fr_TimeClip_to_Write v1.01 | Lega
  Sets the frame range of the write noded to match the frame range of the selected TimeClip

  v1.01: Los carteles salen del helper de carteles del pack
         (show_warning) en vez de nuke.message, con fallback.
  v1.00: Version anterior (v1.0), sin changelog interno.
_____________________________________________________________________________________________

"""

import nuke

# Carteles estilados del pack. Con fallback al cartel de Nuke: este script
# tiene que correr aunque el helper no este instalado.
try:
    from LGA_UI_MessageBox_ToolPackB import show_warning
except ImportError:

    def show_warning(parent, title, text):
        nuke.message(text)


def set_write_from_timeclip():
    # Obtener nodos seleccionados
    selected_nodes = nuke.selectedNodes()

    # Verificar si solo hay dos nodos seleccionados
    if len(selected_nodes) != 2:
        show_warning(None, "TimeClip -> Write", "You must select exactly two nodes: a Write and a TimeClip.")
        return

    # Inicializar variables para los nodos
    write_node = None
    timeclip_node = None

    # Identificar los nodos
    for node in selected_nodes:
        if node.Class() == "Write":
            write_node = node
        elif node.Class() == "TimeClip":
            timeclip_node = node

    # Verificar si ambos nodos necesarios estan presentes
    if not write_node or not timeclip_node:
        show_warning(None, "TimeClip -> Write", "You must select exactly one Write node and one TimeClip node.")
        return

    # Copiar el rango de frames del TimeClip al Write
    write_node["use_limit"].setValue(True)
    write_node["first"].setValue(timeclip_node["first"].value())
    write_node["last"].setValue(timeclip_node["last"].value())


# set_write_from_timeclip()
