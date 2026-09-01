"""
____________________________________________________________________

  LGA_ApplyAMF_Dialogs v1.01 | Lega

  Los dos carteles de LGA_ApplyAMF: elegir el plate y elegir que hacer
  con la cadena. Van en su propio modulo porque LGA_ApplyAMF.py es
  logica pura (sin Qt) y estos dos dialogos son la unica parte de la
  tool que necesita PySide.

  pick_plate(parent, entries) -> entry|None
      Cartel 1. Filas numeradas, una por plate (scan_amf_entries). Elegir
      con la tecla o con click confirma al toque -no hay boton de accion,
      la fila ES la accion-. Si hay un solo plate no se muestra cartel:
      se devuelve directo. Esc o cerrar la ventana cancela (None).

  ask_actions(parent) -> (bool, bool)|None
      Cartel 2. Dos opciones checkbox, las dos activadas por default,
      cada una con su atajo numerico. Enter confirma, Esc cancela. Con
      las dos desmarcadas el boton de accion queda deshabilitado.

  Las dos ventanas copian la estructura de los dialogos de LGA Shot
  Player (ImportClipDialog / ShotReviewImportDialog en
  LGA_MediaTools_v2/apps/player/src): header con titulo y subtitulo,
  fila numerada con badge violeta, hairline entre filas, hint de
  atajos abajo, Cancel(esc) a la izquierda y la accion (si la hay) a
  la derecha. Lo que NO copian: los iconos de header/hint -el pack no
  usa iconos de sistema en sus carteles, ver LGA_UI_MessageBox_
  ToolPackB- y el ancho fijo de 360px -el modulo de estilo define un
  unico ancho minimo de cartel (Metric.DIALOG_MIN_WIDTH) para que
  todas las ventanas salten al mismo tamano-.

  El badge numerado es SIEMPRE violeta en los dos carteles: numera la
  tecla que hay que apretar, no representa un estado. En el cartel 2 el
  estado (tildado/destildado) lo da el QCheckBox real de Style.CHECKBOX,
  y no una segunda variante de color del badge. Se evita asi que el pack
  termine con dos lenguajes visuales distintos para "esto esta activo".

  v1.01: El separador entre filas deja de tener hoja propia -Style.FORM ya
         pinta el QFrame(HLine) por cascada, y el bloque repetia sus mismos
         valores a mano-. El hint pasa a usar de verdad
         Metric.FORM_PATH_FONT_SIZE: el comentario lo declaraba pero nadie
         lo aplicaba, y salia del mismo tamano que el cuerpo. Y el numero
         del badge pide el peso 600 por QFont en vez de semibold(): en
         Nuke 16 los tres archivos de Inter caen en una sola familia, asi
         que semibold() no cambiaba nada (medido: 252 pixeles con tinta
         contra 252; con weight 600, 341).
  v1.00: Version inicial.
____________________________________________________________________
"""

from LGA_QtAdapter_ToolPackB import QtWidgets, QtGui, Qt
from LGA_UI_Style_ToolPackB import Style, Color, Metric, apply_ui_font

# El adapter del pack (LGA_QtAdapter_ToolPackB.py) expone QtWidgets/QtGui/
# QtCore pero NO un QShortcut ya resuelto: en PySide6 vive en QtGui, en
# PySide2 en QtWidgets, y el adapter de ToolPack-B -a diferencia del de
# HieroTools, que si trae este shim- no lo unifica. Se resuelve aca, con el
# mismo fallback que ya usa LGA_QtAdapter_HieroTools.py.
_QShortcut = getattr(QtGui, "QShortcut", None) or getattr(
    QtWidgets, "QShortcut", None
)


# ============================
# Badge numerado (1, 2, 3...)
# ============================
# No hay hoja en el modulo para un "chip numerado": Style cubre botones,
# campos, tabla y checkbox, pero no un indicador de atajo como este. Se arma
# aca con tokens Color.*/Metric.* -nunca un hex- y queda anotado en la
# propuesta como candidato a Style.BADGE_NUMBER si aparece un tercer cartel
# que lo necesite.
_BADGE_SIZE = 22

_BADGE_STYLE = """
QLabel#lgaAmfBadge {
    background-color: %(accent)s;
    color: %(on_accent)s;
    border: 1px solid %(accent)s;
    border-radius: %(radius)dpx;
}
""" % {
    "accent": Color.ACCENT,
    "on_accent": Color.TEXT_ON_ACCENT,
    "radius": Metric.RADIUS_SMALL,
}

# Fila clickeable: transparente en reposo, un escalon de hover -el mismo
# SURFACE_HOVER que ya usa el resto del pack para hover de controles y fila
# seleccionada de tabla- y no el blanco translucido de ShotPlayer, que no
# tiene token y seria un hex nuevo sin motivo de DATA.
_ROW_STYLE = """
#lgaAmfRow { background-color: transparent; border: none; }
#lgaAmfRow:hover { background-color: %(hover)s; }
""" % {"hover": Color.SURFACE_HOVER}

# Caja que agrupa las filas. RADIUS_CARD es el token que el modulo ya reserva
# para "caja de una tabla o de una tarjeta informativa": es exactamente esto.
_LIST_FRAME_STYLE = """
#lgaAmfListFrame {
    background-color: %(surface)s;
    border: 1px solid %(border)s;
    border-radius: %(radius)dpx;
}
""" % {
    "surface": Color.SURFACE,
    "border": Color.BORDER,
    "radius": Metric.RADIUS_CARD,
}


def _make_badge(number, parent=None):
    """QLabel cuadrado con el numero de atajo, siempre en violeta."""
    badge = QtWidgets.QLabel(str(number), parent)
    badge.setObjectName("lgaAmfBadge")
    badge.setAlignment(Qt.AlignCenter)
    badge.setFixedSize(_BADGE_SIZE, _BADGE_SIZE)
    badge.setStyleSheet(_BADGE_STYLE)
    # No intercepta el click: la fila entera confirma, no solo el numerito.
    badge.setAttribute(Qt.WA_TransparentForMouseEvents, True)
    # Ni el tamano ni el peso se ponen aca: apply_ui_font() corre DESPUES y
    # le fija la fuente a todos los hijos. Los pone _finalize_fonts().
    return badge


# Peso del numero del badge. Va por QFont y no por `font-weight` en una hoja
# -que la regla del pack prohibe- y NO por semibold(): en Nuke 16 los tres
# archivos de Inter del pack se registran bajo UNA sola familia "Inter", asi
# que semibold_family() devuelve lo mismo que font_family() y semibold_css()
# termina emitiendo `font-weight: normal`. Medido renderizando el mismo texto
# y contando pixeles con tinta: regular 252, semibold() 252 -o sea, ninguna
# diferencia-, weight 600 341, bold 366. El 600 pedido por QFont es el unico
# camino que da un peso intermedio real en esta version.
_BADGE_WEIGHT = 600
_BADGE_FONT_SIZE = 11


def _finalize_fonts(dialog):
    """Repone tamano y peso de badges y hints DESPUES de apply_ui_font.

    apply_ui_font(dialog) recorre TODOS los hijos y les fija la fuente del
    pack, sin excepcion -es necesario para que la ventana no salga con la del
    host-, pero de paso pisa lo que cada label hubiera pedido por su cuenta.
    Por eso esto va DESPUES y no antes: invertido, el badge queda del tamano
    del cuerpo y el hint deja de leerse como dato secundario, y no se nota
    mirando el codigo -solo la captura-.

    Se buscan por objectName en vez de recibir la lista de filas: asi alcanza
    tambien a los hints, que no cuelgan de ninguna fila.
    """
    peso = QtGui.QFont.Weight(_BADGE_WEIGHT)
    for badge in dialog.findChildren(QtWidgets.QLabel, "lgaAmfBadge"):
        font = badge.font()
        font.setPixelSize(_BADGE_FONT_SIZE)
        font.setWeight(peso)
        badge.setFont(font)

    for hint in dialog.findChildren(QtWidgets.QLabel, "lgaAmfHint"):
        font = hint.font()
        font.setPixelSize(Metric.FORM_PATH_FONT_SIZE)
        hint.setFont(font)


def _make_hairline(parent=None):
    """Separador de 1 px entre filas.

    Sin hoja propia a proposito: Style.FORM ya trae la regla
    `QFrame[frameShape="4"], QFrame[frameShape="5"]` con el color y el alto
    que corresponden, y le cae a este QFrame por cascada. Un bloque QSS
    propio aca seria exactamente el patron que el AGENTS.md marca como el
    error mas comun -repetir a mano lo que la hoja ya define-, ademas de
    quedar desincronizado si algun dia cambia el color del separador.
    """
    line = QtWidgets.QFrame(parent)
    line.setObjectName("lgaAmfDivider")
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFixedHeight(1)
    return line


def _make_hint_label(text, parent=None):
    """Texto de atajos, gris y un escalon mas chico que el cuerpo.

    El tamano lo pone _finalize_fonts() con Metric.FORM_PATH_FONT_SIZE -el
    escalon que el modulo reserva para un dato de referencia, que es
    exactamente el rol de este hint-, y no una hoja: un `font-size` dentro de
    un setStyleSheet esta prohibido por las reglas del pack.
    """
    label = QtWidgets.QLabel(parent)
    label.setObjectName("lgaAmfHint")
    label.setWordWrap(True)
    label.setTextFormat(Qt.RichText)
    label.setText(text)
    label.setStyleSheet("color: %s;" % Color.TEXT_DIM)
    return label


def _fit_height(dialog):
    """Fija el alto de apertura DESPUES de que el layout se activo.

    No se puede calcular antes: con setWordWrap el alto de los labels
    depende del ancho final, que recien se conoce cuando el layout corrio
    una pasada. Ver la trampa de "alto de ventana con numeros fijos" en
    Docu_UI_Style.md.
    """
    layout = dialog.layout()
    if layout is None:
        return
    layout.activate()
    if layout.hasHeightForWidth():
        height = layout.totalHeightForWidth(dialog.width())
    else:
        height = dialog.sizeHint().height()
    dialog.setFixedHeight(height)


def _match_button_widths(*buttons):
    """El Cancel y el de accion miden lo mismo, como en ShotPlayer."""
    ancho = max(b.sizeHint().width() for b in buttons)
    for b in buttons:
        b.setMinimumWidth(ancho)


# ============================
# Cartel 1: elegir el plate
# ============================


class _RowWidget(QtWidgets.QWidget):
    """Una fila clickeable con badge + nombre. El click y el Enter/tecla
    numerica llaman al mismo callback: no hay dos caminos que puedan
    desincronizarse."""

    def __init__(self, index, text, on_activate, parent=None):
        super(_RowWidget, self).__init__(parent)
        self._on_activate = on_activate
        self.setObjectName("lgaAmfRow")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(_ROW_STYLE)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 11)
        layout.setSpacing(10)

        self.badge = _make_badge(index + 1, self)
        layout.addWidget(self.badge, 0, Qt.AlignVCenter)

        label = QtWidgets.QLabel(text, self)
        label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        layout.addWidget(label, 1, Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self._on_activate:
            event.accept()
            self._on_activate()
            return
        super(_RowWidget, self).mousePressEvent(event)


class _PickPlateDialog(QtWidgets.QDialog):
    def __init__(self, parent, entries):
        super(_PickPlateDialog, self).__init__(parent)
        self.selected_entry = None
        self._entries = entries
        self._height_fitted = False
        self._rows = []

        self.setWindowTitle("Select Plate")
        self.setModal(True)
        self.setStyleSheet(Style.FORM)
        self.setMinimumWidth(Metric.DIALOG_MIN_WIDTH)

        self._build_ui()
        self._install_shortcuts()
        apply_ui_font(self)
        _finalize_fonts(self)

    # -- UI --------------------------------------------------------------
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(
            Metric.DIALOG_MARGIN,
            Metric.DIALOG_MARGIN,
            Metric.DIALOG_MARGIN,
            Metric.DIALOG_MARGIN,
        )
        root.setSpacing(Metric.SPACING + 4)

        title = QtWidgets.QLabel("Select plate", self)
        title.setProperty("lgaTitle", True)
        root.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "This shot has more than one plate. Choose which one to apply.",
            self,
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: %s;" % Color.TEXT_DIM)
        root.addWidget(subtitle)

        list_frame = QtWidgets.QFrame(self)
        list_frame.setObjectName("lgaAmfListFrame")
        list_frame.setAttribute(Qt.WA_StyledBackground, True)
        list_frame.setStyleSheet(_LIST_FRAME_STYLE)
        list_layout = QtWidgets.QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        for index, entry in enumerate(self._entries):
            row = _RowWidget(
                index,
                _plate_label(entry),
                self._make_activator(entry),
                list_frame,
            )
            list_layout.addWidget(row)
            self._rows.append(row)
            if index < len(self._entries) - 1:
                list_layout.addWidget(_make_hairline(list_frame))

        root.addWidget(list_frame)

        shortcut_count = min(9, len(self._entries))
        hint = _make_hint_label(
            "Press <span style='color:%s'><b>1</b></span>-"
            "<span style='color:%s'><b>%d</b></span> to choose a plate.<br/>"
            "Press <span style='color:%s'><b>Esc</b></span> to cancel."
            % (
                Color.ACCENT_HOVER,
                Color.ACCENT_HOVER,
                shortcut_count,
                Color.ACCENT_HOVER,
            ),
            self,
        )
        root.addWidget(hint)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addStretch(1)
        cancel_button = QtWidgets.QPushButton("Cancel (esc)", self)
        cancel_button.setStyleSheet(Style.BTN_SECONDARY)
        cancel_button.setAutoDefault(False)
        cancel_button.setDefault(False)
        cancel_button.clicked.connect(self.reject)
        button_row.addWidget(cancel_button)
        root.addLayout(button_row)

    def _make_activator(self, entry):
        def _activar():
            self.selected_entry = entry
            self.accept()

        return _activar

    def _install_shortcuts(self):
        limit = min(9, len(self._entries))
        for i in range(limit):
            shortcut = _QShortcut(QtGui.QKeySequence(str(i + 1)), self)
            shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut.activated.connect(self._make_activator(self._entries[i]))

    # -- alto --------------------------------------------------------------
    def showEvent(self, event):
        super(_PickPlateDialog, self).showEvent(event)
        if self._height_fitted:
            return
        self._height_fitted = True
        _fit_height(self)


def _plate_label(entry):
    """'aPlate v001', o el nombre pelado si el .amf no matcheo el patron de
    plate (ver parse_plate_name en LGA_ApplyAMF.py)."""
    if entry.get("version") is None:
        return entry["plate"]
    return "%s v%03d" % (entry["plate"], entry["version"])


def pick_plate(parent, entries):
    """Cartel 1. Devuelve la entrada elegida, o None si se cancelo.

    Con 0 o 1 entradas no hay nada que elegir: se devuelve directo y el
    cartel no se llega a construir.
    """
    if not entries:
        return None
    if len(entries) == 1:
        return entries[0]

    dialog = _PickPlateDialog(parent, entries)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        return dialog.selected_entry
    return None


# ============================
# Cartel 2: elegir que hacer
# ============================

_ACTION_LABELS = (
    "Create the nodes",
    "Create loose nodes and set as Input Process",
)


class _ActionRow(QtWidgets.QWidget):
    """Badge numerado + QCheckBox real. El click en cualquier parte de la
    fila que no sea el propio indicador del checkbox lo tilda/destilda: el
    checkbox conserva su click nativo porque no es transparente al mouse,
    solo el badge lo es -mismo patron que ImportClipDialog.cpp en
    ShotPlayer, ahi con WA_TransparentForMouseEvents en badge y label."""

    def __init__(self, index, text, checked, parent=None):
        super(_ActionRow, self).__init__(parent)
        self.setObjectName("lgaAmfRow")
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(_ROW_STYLE)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(12, 11, 12, 11)
        layout.setSpacing(10)

        self.badge = _make_badge(index + 1, self)
        layout.addWidget(self.badge, 0, Qt.AlignVCenter)

        self.checkbox = QtWidgets.QCheckBox(text, self)
        self.checkbox.setProperty("lgaLabeled", True)
        self.checkbox.setStyleSheet(Style.CHECKBOX)
        self.checkbox.setChecked(checked)
        layout.addWidget(self.checkbox, 1, Qt.AlignVCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            event.accept()
            self.checkbox.toggle()
            return
        super(_ActionRow, self).mousePressEvent(event)

    def toggle(self):
        self.checkbox.toggle()


class _AskActionsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(_AskActionsDialog, self).__init__(parent)
        self._height_fitted = False
        self._rows = []

        self.setWindowTitle("Apply AMF")
        self.setModal(True)
        self.setStyleSheet(Style.FORM)
        self.setMinimumWidth(Metric.DIALOG_MIN_WIDTH)

        self._build_ui()
        self._install_shortcuts()
        apply_ui_font(self)
        _finalize_fonts(self)
        self._refresh_action_enabled()

    # -- UI --------------------------------------------------------------
    def _build_ui(self):
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(
            Metric.DIALOG_MARGIN,
            Metric.DIALOG_MARGIN,
            Metric.DIALOG_MARGIN,
            Metric.DIALOG_MARGIN,
        )
        root.setSpacing(Metric.SPACING + 4)

        title = QtWidgets.QLabel("Apply AMF", self)
        title.setProperty("lgaTitle", True)
        root.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "Choose what to do with the color chain.", self
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: %s;" % Color.TEXT_DIM)
        root.addWidget(subtitle)

        list_frame = QtWidgets.QFrame(self)
        list_frame.setObjectName("lgaAmfListFrame")
        list_frame.setAttribute(Qt.WA_StyledBackground, True)
        list_frame.setStyleSheet(_LIST_FRAME_STYLE)
        list_layout = QtWidgets.QVBoxLayout(list_frame)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        for index, text in enumerate(_ACTION_LABELS):
            row = _ActionRow(index, text, True, list_frame)
            row.checkbox.stateChanged.connect(self._refresh_action_enabled)
            list_layout.addWidget(row)
            self._rows.append(row)
            if index < len(_ACTION_LABELS) - 1:
                list_layout.addWidget(_make_hairline(list_frame))

        root.addWidget(list_frame)

        hint = _make_hint_label(
            "Press <span style='color:%s'><b>1</b></span>, "
            "<span style='color:%s'><b>2</b></span> to toggle.<br/>"
            "Press <span style='color:%s'><b>Enter</b></span> to apply, "
            "<span style='color:%s'><b>Esc</b></span> to cancel."
            % (
                Color.ACCENT_HOVER,
                Color.ACCENT_HOVER,
                Color.ACCENT_HOVER,
                Color.ACCENT_HOVER,
            ),
            self,
        )
        root.addWidget(hint)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addStretch(1)
        self.cancel_button = QtWidgets.QPushButton("Cancel (esc)", self)
        self.cancel_button.setStyleSheet(Style.BTN_SECONDARY)
        self.cancel_button.setAutoDefault(False)
        self.cancel_button.setDefault(False)
        self.cancel_button.clicked.connect(self.reject)
        button_row.addWidget(self.cancel_button)

        self.action_button = QtWidgets.QPushButton("Apply (enter)", self)
        self.action_button.setStyleSheet(Style.BTN_PRIMARY)
        self.action_button.setAutoDefault(True)
        self.action_button.setDefault(True)
        self.action_button.clicked.connect(self.accept)
        button_row.addWidget(self.action_button)

        _match_button_widths(self.cancel_button, self.action_button)
        root.addLayout(button_row)

    def _install_shortcuts(self):
        for i, row in enumerate(self._rows):
            shortcut = _QShortcut(QtGui.QKeySequence(str(i + 1)), self)
            shortcut.setContext(Qt.WidgetWithChildrenShortcut)
            shortcut.activated.connect(self._make_toggler(row))

    def _make_toggler(self, row):
        def _toggle():
            row.toggle()

        return _toggle

    def _refresh_action_enabled(self, *_args):
        any_checked = any(row.checkbox.isChecked() for row in self._rows)
        self.action_button.setEnabled(any_checked)

    def result_tuple(self):
        return tuple(row.checkbox.isChecked() for row in self._rows)

    # -- alto --------------------------------------------------------------
    def showEvent(self, event):
        super(_AskActionsDialog, self).showEvent(event)
        if self._height_fitted:
            return
        self._height_fitted = True
        _fit_height(self)


def ask_actions(parent):
    """Cartel 2. Devuelve (create_nodes, create_input_process), o None si
    se cancelo. Las dos arrancan tildadas."""
    dialog = _AskActionsDialog(parent)
    if dialog.exec_() == QtWidgets.QDialog.Accepted:
        return dialog.result_tuple()
    return None
