import PyQt5
import PyQt5.QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QIcon


def WrapLayout(items, direct = "V"):
    """
    wrap items into a layout
    `items`: `list[QWidget | QVBoxLayout | QHBoxLayout]`
    `direct`: "V" for wrapping into a QVBoxLayout, "H" for wrapping into a QHBoxLayout
    """
    layout = QVBoxLayout() if direct == "V" else QHBoxLayout()
    for item in items:
        if isinstance(item, QWidget):
            layout.addWidget(item)
        elif isinstance(item, QVBoxLayout) or isinstance(item, QHBoxLayout):
            layout.addLayout(item)
    return layout

def WrapGroup(parent, group_title, items, direct = "V", w = "Auto", h = "Auto"):
    """
    wrap items into a group
    `items`: `list[QWidget | QVBoxLayout | QHBoxLayout]`
    `direct`: "V" for wrapping into a QVBoxLayout, "H" for wrapping into a QHBoxLayout
    `w` `h`: width and height of the group, otherwise not fixed if "Auto", 
    """
    group = QGroupBox(group_title, parent)
    if w != "Auto": group.setFixedWidth(w)
    if h != "Auto": group.setFixedHeight(h)

    layout = QVBoxLayout() if direct == "V" else QHBoxLayout()
    for item in items:
        if isinstance(item, QWidget):
            layout.addWidget(item)
        elif isinstance(item, QVBoxLayout) or isinstance(item, QHBoxLayout):
            layout.addLayout(item)
    group.setLayout(layout)
    return group

def Label(parent, text = "label", p_x = 0, p_y = 0, w = "Auto", h = "Auto",
              tip = "label", halign = "left", valign = "center",
              color = "#000", bg_color = None, font_style = "Default", font_size = 9,
              href = None, on_activated = "Auto", on_hovered = None
              ):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `on_activated`: `(url) -> None`
    if use "Auto", open with default browser for web url,
    open with default app for file path(only supports absolute path)
    `on_hovered`: `(url) -> None`
    """
    label = QLabel("", parent)
    # handle hyperlink
    if href == None:
        on_activated = None
        on_hovered = None
    elif on_activated == "Auto":
        on_activated = lambda url: PyQt5.QtGui.QDesktopServices.openUrl(PyQt5.QtCore.QUrl(url))
    if on_activated != None: label.linkActivated.connect(on_activated)
    if on_hovered != None: label.linkHovered.connect(on_hovered)
    # color and background color
    label.setText(f'<a href="{href if href != None else ""}">{text}</a>')
    if bg_color != None: label.setStyleSheet(f"background-color: {bg_color}; color: {color};")
    else: label.setStyleSheet(f"color: {color};")
    # alignment
    match halign:
        case "left":   qt_halign = PyQt5.QtCore.Qt.AlignLeft
        case "right":  qt_halign = PyQt5.QtCore.Qt.AlignRight
        case "center": qt_halign = PyQt5.QtCore.Qt.AlignHCenter
    match valign:
        case "top":    qt_valign = PyQt5.QtCore.Qt.AlignTop
        case "bottom": qt_valign = PyQt5.QtCore.Qt.AlignBottom
        case "center": qt_valign = PyQt5.QtCore.Qt.AlignVCenter
    label.setAlignment(qt_halign | qt_valign)
    # font
    label.setFont(PyQt5.QtGui.QFont(font_style, font_size))
    # tooltip
    label.setToolTip(tip)
    # geometry
    label.move(p_x, p_y)
    label.adjustSize()
    if w != "Auto": label.setFixedWidth(w)
    if h != "Auto": label.setFixedHeight(h)

    return label

def ImageLabel(parent, src, p_x = 0, p_y = 0, w = "Auto", h = "Auto", fit_scale = True,
              tip = "image label", halign = "center", valign = "center",
              ):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `w` `h`: if both "Auto", use image size; if one "Auto", calculate the other one with image aspect ratio
    `fit_scale`: if True, scale image to fit button size; if False, use original size
    """
    label = QLabel(None, parent)
    pixmap = QPixmap(src)
    # geometry
    label.move(p_x, p_y)
    if w == "Auto" and h == "Auto":
        w = pixmap.width()
        h = pixmap.height()
    elif w == "Auto": w = h * pixmap.width() // pixmap.height()
    elif h == "Auto": h = w * pixmap.height() // pixmap.width()
    label.resize(w, h)
    # image
    if fit_scale: pixmap = pixmap.scaled(w, h)
    label.setPixmap(pixmap)
    # alignment
    match halign:
        case "left":   qt_halign = PyQt5.QtCore.Qt.AlignLeft
        case "right":  qt_halign = PyQt5.QtCore.Qt.AlignRight
        case "center": qt_halign = PyQt5.QtCore.Qt.AlignHCenter
    match valign:
        case "top":    qt_valign = PyQt5.QtCore.Qt.AlignTop
        case "bottom": qt_valign = PyQt5.QtCore.Qt.AlignBottom
        case "center": qt_valign = PyQt5.QtCore.Qt.AlignVCenter
    label.setAlignment(qt_halign | qt_valign)
    # tooltip
    label.setToolTip(tip)

    return label

def Button(parent, text = "button", tip = "", p_x = 0, p_y = 0, w = "Auto", h = "Auto",
           color = "#000", bg_color = None, font_style = "Default", font_size = 9,
           on_click = None):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `on_click`: `() -> None`
    """
    button = QPushButton(text, parent)
    # color and background color
    if bg_color != None: button.setStyleSheet(f"background-color: {bg_color}; color: {color};")
    else: button.setStyleSheet(f"color: {color};")
    # font
    button.setFont(PyQt5.QtGui.QFont(font_style, font_size))
    # tooltip
    if tip != "": button.setToolTip(tip)
    # geometry
    button.move(p_x, p_y)
    button.adjustSize()
    if w != "Auto": button.setFixedWidth(w)
    if h != "Auto": button.setFixedHeight(h)
    # on_click event
    if on_click != None:
        button.clicked.connect(on_click)

    return button

def ImageButton(parent, src, tip = "", p_x = 0, p_y = 0, w = "Auto", h = "Auto",
                frame_gap = 4, fit_scale = True, on_click = None):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `w` `h`: if both "Auto", use image size; if one "Auto", calculate the other one with image aspect ratio
    `frame_gap`: width of gap between image and button frame
    `fit_scale`: if True, scale image to fit button size; if False, use original size
    `on_click`: `() -> None`
    """
    button = QPushButton(parent)
    pixmap = QPixmap(src)
    # geometry & handle frame gap
    button.move(p_x, p_y)
    if w == "Auto" and h == "Auto":
        w_img = pixmap.width()
        h_img = pixmap.height()
        w = w_img + frame_gap * 2
        h = h_img + frame_gap * 2
    elif w == "Auto":
        h_img = h - frame_gap * 2
        w_img = h_img * pixmap.width() // pixmap.height()
        w = w_img + frame_gap * 2
    elif h == "Auto":
        w_img = w - frame_gap * 2
        h_img = w_img * pixmap.height() // pixmap.width()
        h = h_img + frame_gap * 2
    else:
        w_img = w - frame_gap * 2
        h_img = h - frame_gap * 2
    button.resize(w, h)
    # image
    if fit_scale:
        pixmap = pixmap.scaled(w_img, h_img)
        button.setIcon(QIcon(pixmap))
        button.setIconSize(PyQt5.QtCore.QSize(w_img, h_img))
    else:
        button.setIcon(QIcon(pixmap))
        button.setIconSize(pixmap.size())
    # tooltip
    if tip != "": button.setToolTip(tip)
    # on_click event
    if on_click != None:
        button.clicked.connect(on_click)

    return button

def Textbox(parent, init_text = "", placeholder = "", p_x = 0, p_y = 0, w = "Auto", h = "Auto", on_change = None):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `on_change`: `(text) -> None`
    """
    textbox = QLineEdit(parent)
    # on_change event
    if on_change != None:
        textbox.textChanged.connect(on_change)
    # init text
    textbox.setText(init_text)
    # placeholder
    textbox.setPlaceholderText(placeholder)
    # geometry
    textbox.move(p_x, p_y)
    textbox.adjustSize()
    if w != "Auto": textbox.setFixedWidth(w)
    if h != "Auto": textbox.setFixedHeight(h)

    return textbox

def MultiLineTextbox(parent, init_text = "", placeholder = "", p_x = 0, p_y = 0, w = "Auto", h = "Auto", on_change = None):
    """
    This is a multi-line textbox WITH text formatting
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `on_change`: `(text) -> None`
    """
    textbox = QTextEdit(parent)
    # on_change event
    if on_change != None:
        textbox.textChanged.connect(lambda: on_change(textbox.toPlainText()))
    # init text
    textbox.setPlainText(init_text)
    # placeholder
    textbox.setPlaceholderText(placeholder)
    # geometry
    textbox.move(p_x, p_y)
    textbox.adjustSize()
    if w != "Auto": textbox.setFixedWidth(w)
    if h != "Auto": textbox.setFixedHeight(h)

    return textbox

def MultiLinePlainTextbox(parent, init_text = "", placeholder = "", p_x = 0, p_y = 0, w = "Auto", h = "Auto", on_change = None):
    """
    This is a multi-line textbox WITHOUT text formatting
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `on_change`: `(text) -> None`
    """
    textbox = QPlainTextEdit(parent)
    # on_change event
    if on_change != None:
        textbox.textChanged.connect(lambda: on_change(textbox.toPlainText()))
    # init text
    textbox.setPlainText(init_text)
    # placeholder
    textbox.setPlaceholderText(placeholder)
    # geometry
    textbox.move(p_x, p_y)
    textbox.adjustSize()
    if w != "Auto": textbox.setFixedWidth(w)
    if h != "Auto": textbox.setFixedHeight(h)

    return textbox

def Table(parent, p_x = 0, p_y = 0, w = "Auto", h = "Auto", row = "Auto", column = "Auto",
          color = "#000", bg_color = None, font_style = "Default", font_size = 9,
          header = "Auto", columns_width = "Auto", content = []):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `w`: if "Auto", sum of width of vertical header, each column and vertical scrollbar 
    `h`: if "Auto", sum of height of horizontal header, each row and horizontal scrollbar
    `row`: if "Auto", calculated from `content` 
    `column`: if "Auto", calculated from `content`
    `header`: `list[str]`
    `columns_width`: `list[int]`
    `content`: `[[r1], [r2], ...]` first row, then column
    """
    table = QTableWidget(parent)
    # row & column
    if row == "Auto": row = len(content)
    if column == "Auto": column = max(len(row) for row in content) if len(content) > 0 else 0
    table.setRowCount(row)
    table.setColumnCount(column)
    # header
    if header == "Auto": header = [f"C {i}" for i in range(column)]
    table.setHorizontalHeaderLabels(header)
    # content
    for i in range(len(content)):
        for j in range(len(content[i])):
            table.setItem(i, j, QTableWidgetItem(content[i][j]))
    # color and background color
    if bg_color != None: table.setStyleSheet(f"QTableWidget {{background-color: {bg_color}; color: {color};}}")
    else: table.setStyleSheet(f"QTableWidget {{color: {color};}}")
    # font
    table.setFont(PyQt5.QtGui.QFont(font_style, font_size))
    # column width
    table.resizeColumnsToContents()
    if columns_width != "Auto":
        for i in range(len(columns_width)):
            table.setColumnWidth(i, columns_width[i])
    # geometry
    table.move(p_x, p_y)
    if w == "Auto":
        w = sum([table.columnWidth(i) for i in range(column)]) + table.verticalHeader().width() + table.verticalScrollBar().width()
    if h == "Auto":
        h = (table.rowHeight(0) * row if row > 0 else 0) + table.horizontalHeader().height() + table.horizontalScrollBar().height()
    table.resize(w, h)

    return table

def ComboBox(parent, items = [], p_x = 0, p_y = 0, w = "Auto", h = "Auto", on_change = None):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `on_change`: `(index) -> None`
    """
    combobox = QComboBox(parent)
    # on_change event
    if on_change != None:
        combobox.currentIndexChanged.connect(on_change)
    # items
    combobox.addItems(items)
    # geometry
    combobox.move(p_x, p_y)
    combobox.adjustSize()
    if w != "Auto": combobox.setFixedWidth(w)
    if h != "Auto": combobox.setFixedHeight(h)

    return combobox

def CheckBox(parent, text, p_x = 0, p_y = 0, w = "Auto", h = "Auto", on_change = None):
    """
    `parent`: parent QWidget. If put in a layout, you can use `None` and then call `layout.addWidget`
    `on_change`: `(checked) -> None`
    """
    checkbox = QCheckBox(text, parent)
    # on_change event
    if on_change != None:
        checkbox.stateChanged.connect(on_change)
    # geometry
    checkbox.move(p_x, p_y)
    checkbox.adjustSize()
    if w != "Auto": checkbox.setFixedWidth(w)
    if h != "Auto": checkbox.setFixedHeight(h)

    return checkbox

def GetChoiceFromMessageBox(title, text, choices, tips, return_idx = False):
    """
    `choices`: `list[str]`
    `tips`: `list[str]`
    `return_idx`: if True, return index of choice in `choices`, otherwise return choice
    """
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(text)
    for i in range(len(choices)):
        if i < len(tips): msg.addButton(Button(msg, choices[i], tips[i]), QMessageBox.YesRole)
        else: msg.addButton(Button(msg, choices[i]), QMessageBox.YesRole)
    idx = msg.exec_()
    return idx if return_idx else choices[idx]

