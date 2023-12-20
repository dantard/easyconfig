import base64
import sys
import traceback
from enum import Enum

import yaml
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QRectF, QRect, QTimer, pyqtSignal, QLocale
from PyQt5.QtGui import QIcon, QFont, QIntValidator, QDoubleValidator, QValidator
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLineEdit,
    QLabel,
    QDialog,
    QCheckBox,
    QDialogButtonBox,
    QComboBox,
    QFrame,
    QSizePolicy,
    QTreeWidget,
    QTreeWidgetItem,
    QAbstractItemView,
    QScrollArea,
    QHeaderView,
    QTextEdit, QSlider, QStyle, QListWidget, QFrame, QInputDialog
)


class EasyConfig:
    class ConfigWidget(QWidget):
        def get_expanded(self):
            res = []

            def traver(node):
                res.append(1 if node.isExpanded() else 0)
                for i in range(node.childCount()):
                    traver(node.child(i))

            traver(self.list.invisibleRootItem())
            return res

        def set_expanded(self, val):
            def traver(node, vec):
                if len(vec) > 0:
                    node.setExpanded(vec.pop() == 1)
                    for i in range(node.childCount()):
                        traver(node.child(i), vec)

            val.reverse()
            traver(self.list.invisibleRootItem(), val)

        class InteractorWidget(QWidget):
            value_changed = pyqtSignal()

            def __init__(self, name, value, **kwargs):
                super().__init__(None)
                self.kwargs = kwargs

                if not self.check_kwargs():
                    sys.exit(0)

                self.name = name
                self.pretty = kwargs.get("pretty", name)
                self.layout = QHBoxLayout()
                ql = QLabel(self.pretty)
                ql.setMinimumWidth(100)
                self.layout.setContentsMargins(2, 2, 2, 2)
                self.setLayout(self.layout)
                self.setFocusPolicy(Qt.TabFocus)
                ql.setAlignment(Qt.AlignLeft)
                self.ed = None
                self.emit_cb = True
                self.add_specific(value)

            def set_emit_callback(self, value):
                self.emit_cb = value

            def update(self, **kwargs) -> None:
                pass

            def get_valid(self):
                return self.get_common()

            def get_common(self):
                return set(["default", "save", "fmt", "pretty", "callback", "editable"])

            def check_kwargs(self):
                for arg in self.kwargs:
                    if arg not in self.get_valid():
                        print("Parameter", arg, "not valid for ", type(self))
                        return False
                return True
        class String(InteractorWidget):

            def __init__(self, name, value, **kwargs):
                super().__init__(name, value, **kwargs)
                self.prev_value = value
                # print("name", name, kwargs)
                self.ed.setReadOnly(not self.kwargs.get('editable', True))

            def get_valid(self):
                return self.get_common()

            def return_pressed(self):
                self.setStyleSheet("color: black")
                if self.get_value() != self.prev_value:
                    self.value_changed.emit()
                    self.prev_value = self.get_value()

            def text_changed(self):
                self.setStyleSheet("color: red")

            class MyLineEdit(QLineEdit):
                focusout = pyqtSignal()

                def focusOutEvent(self, a0) -> None:
                    super().focusOutEvent(a0)
                    self.focusout.emit()

            def validate(self):
                if (validator := self.ed.validator()) is not None:
                    res, _, _ = validator.validate(self.ed.text(), 0)
                    if res == QValidator.Acceptable:
                        self.return_pressed()
                else:
                    self.return_pressed()

            def add_specific(self, value):
                self.ed = self.MyLineEdit()
                self.ed.returnPressed.connect(self.return_pressed)
                self.ed.focusout.connect(self.validate)
                self.ed.textEdited.connect(self.text_changed)
                fmt = self.kwargs.get("fmt", "{}")
                if value is not None:
                    self.ed.setText(fmt.format(value))
                    self.ed.home(True)
                    self.ed.setSelection(0, 0)
                self.layout.addWidget(self.ed)

            def get_value(self):
                return self.ed.text() if self.ed.text() != "" else None

            def set_value(self, value):
                self.ed.setText(str(value))

            def get_name(self):
                return self.name

        class DoubleLabel(InteractorWidget):
            def add_specific(self, value):
                self.ed = QLabel()
                fmt = self.kwargs.get("fmt", "{}")
                if value is not None and value[0] is not None:
                    self.ed.setText(fmt.format(value[0]))

                self.ed2 = QLabel()
                layout = QHBoxLayout()
                layout.addWidget(self.ed)
                layout.addWidget(self.ed2)

                self.layout.addLayout(layout)
                if value is not None and value[1] is not None:
                    self.ed2.setText(fmt.format(value[1]))

            def set_value(self, value):
                if value is not None:
                    if value[0] is not None:
                        self.ed.setText(str(value[0]))
                    if value[1] is not None:
                        self.ed2.setText(str(value[1]))



        class List(InteractorWidget):

            def add_specific(self, value):
                self.ed = QListWidget()
                #                self.ed.setEditable(False)
                # self.ed.currentIndexChanged.connect(lambda: self.value_changed.emit())
                self.ed.addItems(self.kwargs.get("items", []))
                self.layout.addWidget(self.ed)
                self.ed.setMaximumHeight(self.kwargs.get("height", 100))
                self.ed.setFont(QFont("Courier New", 10))
                # self.ed.setStyleSheet("QListWidget { background-color: transparent; }")
                # self.ed.setStyleSheet("QListWidget { border: 1px solid lightgray; }")
                # if not self.kwargs.get("frame", True):
                # self.ed.setFrameStyle(QFrame.Box | QFrame.Plain)

            def get_valid(self):
                return self.get_common().union(["items", "height", "frame"])

            def set_value(self, value):
                self.ed.clear()
                self.ed.addItems(value)

            def update(self, **kwargs) -> None:
                if "items" in kwargs:
                    self.ed.clear()
                    self.ed.addItems(kwargs["items"])

                if "on_selection" in kwargs:
                    self.ed: QListWidget
                    self.ed.doubleClicked.connect(kwargs["on_selection"])

        class EditBox(String):

            def add_specific(self, value):
                self.ed = QTextEdit()
                self.ed.textChanged.connect(lambda: self.value_changed.emit())
                font = QFont(self.kwargs.get("font", "Monospace"))

                if self.kwargs.get("bold", False):
                    font.setBold(True)
                if self.kwargs.get("italic", False):
                    font.setItalic(True)
                if self.kwargs.get("typewriter", False):
                    font.setStyleHint(QFont.TypeWriter)

                font.setPointSize(self.kwargs.get("size", 10))

                self.ed.setFont(font)
                self.ed.setMaximumHeight(self.kwargs.get("height", 100))

                if value is not None:
                    self.ed.setText(str(value))

                self.layout.addWidget(self.ed)

            def get_valid(self):
                return self.get_common().union(["font", "bold", "italic", "typewriter", "size", "height"])

            def set_value(self, value):
                self.ed.setText(str(value).replace("&&", "\n"))

            def get_value(self):
                text = self.ed.toPlainText().replace("\n", "&&")
                return text if text != "" else None

        class Password(String):
            def __init__(self, name, value, **kwargs):
                value = base64.decodebytes(value.encode()).decode() if value else None
                super().__init__(name, value, **kwargs)
                self.ed.setEchoMode(QLineEdit.Password)

            def get_value(self):
                if self.ed.text() != "":
                    return (
                        base64.encodebytes(self.ed.text().encode())
                            .decode()
                            .replace("\n", "")
                    )
                else:
                    return None

        class ComboBox(InteractorWidget):

            class MyComboBox(QComboBox):
                def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
                    e.ignore()

            def add_specific(self, value):
                self.cb = self.MyComboBox()
                self.cb.currentIndexChanged.connect(lambda: self.value_changed.emit())
                self.cb.addItems(self.kwargs.get("items", []))
                self.cb.setEditable(self.kwargs.get("editable", False))
                self.layout.addWidget(self.cb, stretch=2)
                self.cb.setCurrentIndex(value if value is not None else 0)



            def update(self, **kwargs):
                items = kwargs.get("append")
                if items is not None:
                    self.cb.addItems(items)
                color = kwargs.get("color")
                if color is not None:
                    self.cb.setStyleSheet("QComboBox { color: %s }" % color)

            def get_valid(self):
                return self.get_common().union(["items"])

            def get_item_text(self):
                return self.cb.currentText()

            def get_value(self):
                return self.cb.currentIndex() if self.cb.currentText() != "" else None

            def set_value(self, value):
                if value is not None and value < self.cb.count():
                    self.cb.setCurrentIndex(value)
                else:
                    self.cb.setCurrentIndex(0)

        class Integer(String):
            def add_specific(self, value):
                super().add_specific(value)
                validator = QIntValidator()
                if self.kwargs.get("max") is not None:
                    validator.setTop(self.kwargs.get("max"))
                if self.kwargs.get("min") is not None:
                    validator.setBottom(self.kwargs.get("min"))
                self.ed.setValidator(validator)

            def get_valid(self):
                return super().get_common().union(["max", "min"])

            def get_value(self):
                return int(self.ed.text()) if self.ed.text().isnumeric() else None

        class Slider(InteractorWidget):

            class MySlider(QSlider):
                def wheelEvent(self, e: QtGui.QWheelEvent) -> None:
                    e.ignore()

            class MyLabel(QLabel):
                double_click = pyqtSignal()

                def mouseDoubleClickEvent(self, a0: QtGui.QMouseEvent) -> None:
                    self.double_click.emit()

            def update(self, **kwargs):
                if 'maximum' in kwargs:
                    self.ed.setMaximum(kwargs.get('maximum', 100))

            def add_specific(self, value):
                self.layout.setContentsMargins(6, 6, 6, 6)
                hbox = QHBoxLayout()
                self.lbl = self.MyLabel()

                def clicked():
                    min = self.kwargs.get('min', 0) / self.kwargs.get('den', 1)

                    num, ok = QInputDialog.getDouble(self, "Proportional gain", "Enter a gain", min=min, value=1)
                    if ok:
                        self.set_value(num)

                self.lbl.double_click.connect(clicked)

                self.lbl.setMinimumWidth(self.kwargs.get("label_width", 25))
                self.lbl.setMaximumWidth(self.kwargs.get("label_width", 25))
                self.ed = self.MySlider()
                self.ed.setOrientation(Qt.Horizontal)
                self.ed.setMinimum(self.kwargs.get('min', 0))
                self.ed.setMaximum(self.kwargs.get('max', 100))
                self.ed.valueChanged.connect(self.slider_moved)
                self.denom = self.kwargs.get('den', 1)
                self.ed.setContentsMargins(2, 2, 2, 2)
                # self.layout.addWidget(self.ed)
                hbox.addWidget(self.lbl)
                hbox.addWidget(self.ed)
                self.layout.addLayout(hbox)
                self.set_value(value)

            def get_valid(self):
                return self.get_common().union(["min", "max", "den", "label_width", "grow"])

            def slider_moved(self, value):
                fmt = self.kwargs.get("fmt", "{}")

                if self.emit_cb:
                    self.value_changed.emit()

                if type(fmt) == int:
                    self.lbl.setText(str(round(self.ed.value() / self.denom, int(fmt))).rstrip('0').rstrip('.'))
                else:
                    self.lbl.setText(fmt.format(self.ed.value() / self.denom))

            def set_value(self, value):
                self.ed: QSlider
                if self.kwargs.get("grow", False) and int(value * self.denom) > self.ed.maximum():
                    self.ed.setMaximum(int(value * self.denom))
                fmt = self.kwargs.get("fmt", "{}")
                self.ed.setValue(int(value * self.denom))
                if type(fmt) == int:
                    self.lbl.setText(str(round(self.ed.value() / self.denom, int(fmt))).rstrip('0').rstrip('.'))
                else:
                    self.lbl.setText(fmt.format(self.ed.value() / self.denom))

            def reset(self):
                self.ed.setMaximum(self.kwargs.get("max", 100))

            def get_value(self):
                return float(self.ed.value() / self.denom)

        class Label(InteractorWidget):
            def add_specific(self, value):
                self.ed = QLabel()
                self.ed.setContentsMargins(2, 2, 2, 2)
                self.layout.addWidget(self.ed)
                fmt = self.kwargs.get("fmt", "{}")
                if value is not None:
                    self.set_value(fmt.format(value))

            def set_value(self, value):
                fmt = self.kwargs.get("fmt", "{}")
                if value is not None:
                    self.ed.setText(fmt.format(value))
                else:
                    self.ed.setText("")
                # self.ed.setText(str(value))

            def get_value(self):
                return self.ed.text()

        class Float(String):
            def add_specific(self, value):
                super().add_specific(value)
                validator = QDoubleValidator()
                self.ed.setValidator(validator)

            def get_value(self):
                return (
                    float(self.ed.text())
                    if self.ed.text().replace(".", "").isnumeric()
                    else None
                )

        class Checkbox(InteractorWidget):
            def state_changed(self):
                self.value_changed.emit()

            def __init__(self, name, value, **kwargs):
                super().__init__(name, value, **kwargs)

            def add_specific(self, value):
                self.layout.setContentsMargins(6, 6, 6, 6)
                self.ed = QCheckBox()
                self.ed.stateChanged.connect(self.state_changed)
                self.layout.addWidget(self.ed)
                self.set_value(value)

            def get_name(self):
                return self.name

            def get_value(self):
                return self.ed.isChecked()

            def set_value(self, value):
                self.ed.setChecked(value if value is not None else False)

        class File(String):
            def __init__(self, name, value, **kwargs):
                super().__init__(name, value, **kwargs)
                self.btn = QPushButton()
                self.btn.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
                self.btn_discard = QPushButton()
                self.btn_discard.setMaximumWidth(25)
                self.btn_discard.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
                self.btn_discard.clicked.connect(self.discard)
                self.btn.setMaximumWidth(30)
                self.btn.clicked.connect(self.open_file)
                self.layout.addWidget(self.btn)
                self.layout.addWidget(self.btn_discard)
                self.ed.setReadOnly(True)

            def get_valid(self):
                return self.get_common().union(["extension", "extension_name"])

            def discard(self):
                self.ed.setText("")

            def open_file(self):
                extension = self.kwargs.get("extension", "txt")
                extension_name = self.kwargs.get("extension_name", extension if type(extension) == str else "")

                ext_filter = "("
                if type(extension) == list:
                    for ext in extension:
                        ext_filter += "*." + ext + " "
                else:
                    ext_filter += "*." + extension

                ext_filter = ext_filter.rstrip() + ")"

                file_name, _ = QFileDialog.getOpenFileName(
                    self,
                    "Open " + extension_name + " Document",
                    self.ed.text(),
                    extension_name.upper() + " Files " + ext_filter,
                )
                if file_name != "":
                    self.ed.setText(file_name)
                    self.value_changed.emit()

        class FolderChoice(File):
            def open_file(self):
                file_name = QFileDialog.getExistingDirectory(self, "Select Directory", "")
                if file_name != "":
                    self.ed.setText(file_name)
                    self.value_changed.emit()

        class SaveFile(File):
            def open_file(self):
                file_name, _ = QFileDialog.getSaveFileName(self, "Open " + self.extension.upper() + " Document", "",
                                                           self.extension.upper() + " Files (*." + self.extension + ")")
                if file_name != "":
                    self.ed.setText(file_name)
                    self.value_changed.emit()

        def __init__(self, node):
            super().__init__(None)
            self.setWindowTitle("EasyConfig")
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.list = QTreeWidget()
            # self.list.setStyleSheet('background: palette(window)')
            self.list.header().setVisible(False)
            self.list.setSelectionMode(QAbstractItemView.NoSelection)
            self.list.setColumnCount(2)
            self.widgets = []

            self.setMinimumHeight(300)
            # self.list.setMinimumWidth(500)

            scroll = QScrollArea()
            scroll.setWidget(self.list)
            scroll.setWidgetResizable(True)

            layout.addWidget(scroll)
            node.fill_tree_widget(self.list, self.list.invisibleRootItem())
            self.list.expanded.connect(lambda: self.list.resizeColumnToContents(0))
            # self.list.expand()
            proxy = self.list.model()

            for row in range(proxy.rowCount()):
                index = proxy.index(row, 0)
                self.list.expand(index)

            # layout.addStretch(30)

            self.setLayout(layout)
            self.installEventFilter(self)
            self.list.resizeColumnToContents(0)
            # self.setMinimumWidth(500)

        def eventFilter(self, a0, a1) -> bool:
            if a1.type() == QtCore.QEvent.KeyPress:
                if a1.key() in [Qt.Key_Return]:
                    return True
            return False

    class Dialog(QDialog):

        def __init__(self, widget):
            super().__init__()
            vbox = QVBoxLayout()
            self.setLayout(vbox)
            vbox.addWidget(widget)

            self.bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.bb.accepted.connect(self.accept)
            self.bb.rejected.connect(self.reject)

            vbox.addWidget(self.bb)

    class Elem:
        class Kind:
            def __init__(self):
                pass

            STR = 1
            INT = 2
            FILE = 3
            CHECKBOX = 4
            FLOAT = 5
            COMBOBOX = 6
            SECTION = 7
            SUBSECTION = 8
            PASSWORD = 9
            EDITBOX = 10
            LIST = 11
            FILE_SAVE = 12
            CHOSE_DIR = 13
            LABEL = 14
            SLIDER = 15
            DOUBLE_TEXT = 16
            DICTIONARY = 17
            ROOT = 254

            @staticmethod
            def type2Kind(value):
                if type(value) == int:
                    return 2
                elif type(value) == float:
                    return 5
                elif type(value) == list:
                    return 11
                else:
                    return 1

        def __init__(self, key, kind, parent=None, **kwargs):
            self.kind = kind
            self.kwargs = kwargs
            self.save = kwargs.get("save", True)
            self.hidden = kwargs.get("hidden", False)
            # self.callback = kwargs.get("callback", None)
            default = kwargs.get("default", None)
            self.value = kwargs.get("val", kwargs.get("value", default))
            # self.pretty = kwargs.get("pretty", key)
            self.default_params = {}
            self.key = key
            self.child = []
            self.parent = parent
            self.node = None
            self.w = None
            self.tree_view_item = None

        def set_visible(self, value):
            if self.tree_view_item is not None:
                self.tree_view_item.setHidden(not value)

        def set_default_params(self, params_dict, append=None, remove=[]):
            # print("setdef", self.key, params_dict, self.default_params)
            self.default_params = params_dict.copy()
            if append is not None:
                self.default_params.update(append)
            for p in remove:
                self.default_params.pop(p, None)

        def get_value(self):
            return self.value

        def update(self, **kwargs):
            if self.w is not None:
                self.w.update(**kwargs)

        def set_value(self, value, emit=True):
            self.value = value
            if self.w is not None:
                self.w.set_emit_callback(emit)
                self.w.set_value(value)
                self.w.set_emit_callback(True)

        def add(self, key, kind=Kind.STR, **kwargs):

            for k, v in self.default_params.items():
                if not k in kwargs:
                    kwargs[k] = v

            if '/' in key:
                if key.startswith("/") and self.kind != self.Kind.ROOT:
                    raise Exception("A key can begin with '/' only if adding from the root node")

                key = key if not key.startswith("/") else key[1:]
                fields = key.split("/")
                node, field_index = self, -1
                for i, field in enumerate(fields):
                    for child in node.child:  # type: EasyConfig.Elem
                        if child.key == field:
                            node = child
                            field_index = i
                            break
                for i in range(field_index + 1, len(fields) - 1):
                    node = node.addSubSection(fields[i])


                elem = EasyConfig.Elem(fields[-1], kind, self, **kwargs)
                elem.set_default_params(self.default_params)
                node.addChild(elem)

            else:
                elem = EasyConfig.Elem(key, kind, self, **kwargs)
                elem.set_default_params(self.default_params)
                self.addChild(elem)

            return elem

        def addString(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.STR, **kwargs)

        def addDict(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.DICTIONARY, **kwargs)

        def addList(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.LIST, **kwargs)

        def addEditBox(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.EDITBOX, **kwargs)

        def addPassword(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.PASSWORD, **kwargs)

        def addInt(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.INT, **kwargs)

        def addLabel(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.LABEL, **kwargs)

        def addSlider(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.SLIDER, **kwargs)

        def addFloat(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.FLOAT, **kwargs)

        def addFile(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.FILE, **kwargs)

        def addFileSave(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.FILE_SAVE, **kwargs)

        def addFolderChoice(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.CHOSE_DIR, **kwargs)

        def addCheckbox(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.CHECKBOX, **kwargs)

        def addCombobox(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.COMBOBOX, **kwargs)

        def addDoubleText(self, name, **kwargs):
            return self.add(name, EasyConfig.Elem.Kind.DOUBLE_TEXT, **kwargs)

        def addChild(self, elem):
            self.child.append(elem)

        def addSubSection(self, key, **kwargs):

            for k, v in self.default_params.items():
                if not k in kwargs:
                    kwargs[k] = v

            elem = EasyConfig.Elem(key, EasyConfig.Elem.Kind.SUBSECTION, self, **kwargs)
            elem.set_default_params(self.default_params, kwargs, ['pretty'])

            self.addChild(elem)
            return elem

        def addHidden(self, key, **kwargs):
            kwargs.update({'hidden': True})
            return self.addSubSection(key, **kwargs)

        def create(self, list, node):
            parent = node
            e = self
            if e.kind == EasyConfig.Elem.Kind.INT:
                self.w = EasyConfig.ConfigWidget.Integer(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.LABEL:
                self.w = EasyConfig.ConfigWidget.Label(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.SLIDER:
                self.w = EasyConfig.ConfigWidget.Slider(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.FILE:
                self.w = EasyConfig.ConfigWidget.File(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.FILE_SAVE:
                self.w = EasyConfig.ConfigWidget.SaveFile(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.CHOSE_DIR:
                self.w = EasyConfig.ConfigWidget.FolderChoice(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.CHECKBOX:
                self.w = EasyConfig.ConfigWidget.Checkbox(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.COMBOBOX:
                self.w = EasyConfig.ConfigWidget.ComboBox(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.FLOAT:
                self.w = EasyConfig.ConfigWidget.Float(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.PASSWORD:
                self.w = EasyConfig.ConfigWidget.Password(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.EDITBOX:
                self.w = EasyConfig.ConfigWidget.EditBox(e.key, e.value, **e.kwargs)
                self.w.set_value(e.value)
            elif e.kind == EasyConfig.Elem.Kind.LIST:
                self.w = EasyConfig.ConfigWidget.List(e.key, e.value, **e.kwargs)
            elif e.kind == EasyConfig.Elem.Kind.DICTIONARY:
                pass
            elif e.kind == EasyConfig.Elem.Kind.DOUBLE_TEXT:
                self.w = EasyConfig.ConfigWidget.DoubleLabel(e.key, e.value, **e.kwargs)
            else:
                self.w = EasyConfig.ConfigWidget.String(e.key, e.value, **e.kwargs)

            self.w.value_changed.connect(lambda: self.update_value(self.w.get_value()))

            child = QTreeWidgetItem()
            child.setText(0, self.kwargs.get("pretty", self.key))
            parent.addChild(child)
            # list.setItemWidget(child, 0, QLabel(self.pretty + "ss"))
            # print("add", self.key, child)
            list.setItemWidget(child, 1, self.w)
            self.tree_view_item = child
            # list.setItemWidget(child, 0, QLabel(self.pretty))

        def update_value(self, value):
            self.value = value
            callback = self.kwargs.get("callback")
            if callback is not None:
                if self.kind == EasyConfig.Elem.Kind.COMBOBOX:
                    callback(self.key, self.w.get_item_text())
                else:
                    callback(self.key, self.value)

        def getDictionary(self, dic):
            if self.kind == EasyConfig.Elem.Kind.ROOT:
                dic.clear()
                for c in self.child:
                    c.getDictionary(dic)
            elif self.kind == EasyConfig.Elem.Kind.SUBSECTION:
                if self.save:
                    dic[self.key] = {}
                    dic = dic[self.key]
                    for c in self.child:
                        c.getDictionary(dic)
            else:
                if self.save:
                    dic[self.key] = self.value

        def collect(self):
            if self.kind == EasyConfig.Elem.Kind.ROOT:
                for c in self.child:
                    c.collect()
            elif self.kind == EasyConfig.Elem.Kind.SUBSECTION:
                if not self.hidden:
                    for c in self.child:
                        c.collect()
            elif not self.hidden and not self.parent.hidden:
                self.value = self.w.get_value()
                self.w = None

        def load(self, dic, keys=None):
            if self.kind == EasyConfig.Elem.Kind.ROOT:
                keys = []
                for c in self.child:
                    c.load(dic, keys.copy())
            elif self.kind == EasyConfig.Elem.Kind.SUBSECTION:
                keys.append(self.key)
                for c in self.child:
                    c.load(dic, keys.copy())
            else:
                for k in keys:
                    dic = dic.get(k)

                    if dic is None:
                        break

                if dic is not None:
                    self.value = dic.get(self.key, self.value)
                    print("setting", self.key,self.value)

                    if self.w is not None:
                        self.w.set_value(self.value)

        def fill_tree_widget(self, list, node=None):
            if self.kind == EasyConfig.Elem.Kind.ROOT:
                node = list.invisibleRootItem()
            elif self.kind == EasyConfig.Elem.Kind.SUBSECTION:
                if not self.hidden:
                    qtw = QTreeWidgetItem()
                    node.addChild(qtw)
                    # qtw.setText(0, self.kwargs.get("Pretty", self.key))
                    label = QLabel(self.kwargs.get("Pretty", self.key))
                    label.setContentsMargins(2, 2, 2, 2)
                    list.setItemWidget(qtw, 0, label)
                    self.tree_view_item = qtw
                    node = qtw
            elif not self.hidden and not self.parent.hidden:
                self.create(list, node)

            for c in self.child:
                c.fill_tree_widget(list, node)

    def __init__(self, default_params={}):
        self.min_height = None
        self.min_width = None
        self.root_node = self.Elem("root", EasyConfig.Elem.Kind.ROOT, None)
        self.root_node.set_default_params(default_params)
        self.reserved = "main"
        self.expanded = None
        self.widget = None

    def tab(self):
        return self

    def root(self):
        return self.root_node

    def get_widget(self):
        self.widget = self.ConfigWidget(self.root_node)
        # dialog.bb.setVisible(False)
        if self.expanded:
            self.widget.set_expanded(self.expanded)
        return self.widget

    def set_dialog_minimum_size(self, width=None, height=None):
        self.min_width = width
        self.min_height = height

    def exec(self):
        return self.edit()

    def edit(self):

        widget = self.ConfigWidget(self.root_node)
        dialog = self.Dialog(widget)

        if self.min_width is not None:
            widget.setMinimumWidth(self.min_width)
        if self.min_height is not None:
            widget.setMinimumHeight(self.min_height)

        widget.list.collapseAll()
        if self.expanded:
            widget.set_expanded(self.expanded)

        res = dialog.exec()
        self.expanded = widget.get_expanded()

        if res == QDialog.Accepted:
            self.root_node.collect()

        return res

    def get(self, key, default=None, create=False):
        if key is None:
            return None  # , val=value)
        elif not key.startswith("/"):
            nodes = self.get_nodes(key)
            if len(nodes) > 0:
                return nodes[0].value if nodes[0].value is not None else default
            else:
                raise Exception("Key {} not found{}".format(key, ". Can create only from "
                                                                 "root node (add '/' at the "
                                                                 "beginning of the key)" if create else ""))
        else:
            path = key[1:].split("/")
            node = self.get_node(path)
            if node is not None:
                return node.value if node.value is not None else default
            elif create:
                default = default if default is not None else str()
                self.root().add(key, self.Elem.Kind.type2Kind(default), default=default)
                return default
            else:
                raise Exception("Key {} not found".format(key))

    def get_field(self, key):
        nodes = self.get_nodes(key)
        if len(nodes) > 0:
            return nodes[0]
        else:
            return None

    def set(self, key, value, create=False):
        if key is None:
            return None
        elif not key.startswith("/"):
            nodes = self.get_nodes(key)
            if len(nodes) > 0:
                nodes[0].set_value(value)
                return True
            else:
                raise Exception("Key {} not found{}".format(key, ". Can create only from "
                                                                 "root node (add '/' at the "
                                                                 "beginning of the key)" if create else ""))
        else:
            path = key[1:].split("/")
            node = self.get_node(path)
            if node is not None:
                node.set_value(value)
            elif create:
                elem = self.root().add(key, self.Elem.Kind.type2Kind(value))
                elem.set_value(value)
                return True
            else:
                raise Exception("Key {} not found".format(key))

    def store_easyconfig_info(self, tree):
        if self.expanded:
            tree["easyconfig"] = {"expanded": "".join(str(e) for e in self.expanded)}

    def recover_easyconfig_info(self, tree):
        expanded = tree.get("easyconfig", {}).get("expanded")
        if expanded:
            self.expanded = [int(a) for a in expanded]

    def save(self, filename):
        tree = dict()
        if self.widget is not None:
            self.expanded = self.widget.get_expanded()
        self.root_node.getDictionary(tree)
        self.store_easyconfig_info(tree)
        with open(filename, "w") as f:
            yaml.dump(tree, f, sort_keys=False)

    def get_node(self, keys):
        node = self.root_node
        for p in keys:
            found = False
            for c in node.child:
                if c.key.lower() == p.lower():  # or c.pretty.lower() == p.lower():
                    found = True
                    node = c
                    break
            if not found:
                return None
        return node

    def get_nodes(self, key):
        def recu(node, found):
            if (
                    node
                    and key
                    and node.kind != EasyConfig.Elem.Kind.SUBSECTION
                    and (node.key.lower() == key.lower())
            ):  # or node.pretty.lower() == key.lower()):
                found.append(node)
            for c in node.child:
                recu(c, found)

        nodes = []
        recu(self.root_node, nodes)
        return nodes

    def add_dynamic_fields(self, config):
        paths = self.traverse_and_store_paths(config)
        for path in paths:
            if self.get_node(path) is not None:
                continue
            if len(path) > 0:
                node = self.get_node([path[0]])
                if node is None or node.kind != EasyConfig.Elem.Kind.SUBSECTION:
                    # Not an easyconfig dynamic path
                    continue

                for i in range(1,len(path)-1):
                    child = self.get_node(path[0:i+1])
                    if child is None:
                        node = node.add(path[i], EasyConfig.Elem.Kind.SUBSECTION)
                    else:
                        node = child
                node.add(path[-1])

    def traverse_and_store_paths(self, data, path=None, paths=None):
        if path is None:
            path = []
        if paths is None:
            paths = []

        for key, value in data.items():
            current_path = path + [key]

            if isinstance(value, dict):
                self.traverse_and_store_paths(value, current_path, paths)
            else:
                paths.append(current_path)

        return paths

    def load(self, filename):
        try:
            with open(filename, "r") as f:
                config = yaml.safe_load(f)
                self.recover_easyconfig_info(config)
                self.add_dynamic_fields(config)
                self.root_node.load(config)


        except:
            traceback.print_exc()


class MainWindow(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText("Try!")
        self.setGeometry(QRect(100, 100, 100, 100))

        self.c = EasyConfig({"editable": False})
        first_level = self.c.root().addSubSection("first_level", pretty="First level")
        first_level.addLabel("Label", pretty="One label", default="hola", save=False)
        first_level.addString("string", pretty="One string", save=False, callback=lambda x, y: print("cbcbc ", x, y),
                              editable=True)
        first_level.addInt("int", pretty="One int", default=27)
        self.lis = first_level.addList("list", pretty="One list", items=["a", "b", "c"])
        first_level.addFloat("float", pretty="One float", default=28)
        second_level = first_level.addSubSection("second_level", pretty="Second Level", editable=True)
        second_level.addCombobox("Combo", pretty="One combobox", items=["a", "b", "c"],
                                 callback=lambda x, y: print("hhh", x, y))
        second_level.addFile("load_file", pretty="One file", extension="jpg")
        second_level.addFileSave("save_file", extension="jpg", editable=True)
        second_level.addString("string27")

        first_level.addFolderChoice("chose_folder", pretty="Choose folder", extension="jpg")
        first_level.addCheckbox("checkbox", pretty="The checkbox")
        first_level.addEditBox("editbox", pretty="The editbox", font="Helvetica", size=20, bold=True, italic=True)
        first_level.addPassword("password", pretty="The password")
        first_level.addSlider("slider", pretty="Slider", max=10, min=1, den=4, fmt="{:.1f}", default=1.2)

        hidden = self.c.root().addHidden("hidden1")
        hidden.addInt("hidden_int")
        self.c.root().addInt("/danilo/tardioli")
        first_level.addInt("kakka/kakka2/kakka3", default=6)
        self.c.get("/private44/more_private/private_int", 4, create=True)
        self.c.set("/private44/more_private/private_int2", 41, create=True)
        print("kjhdflkjhslkjf", self.c.root().default_params)
        self.clicked.connect(self.test)
        first_level.set_visible(False)
        self.first_level = first_level

    def test(self):
        # self.c.load("co.yaml")
        # self.c.set("float", 88)
        # self.c.set("private_int", 145)
        # print()
        # self.c.set("/minollo/minolli/hdhdh", 6, create=True)

        def do():
            # print(self.c.get("string"), self.c.get("int"))
            # self.c.set("int", self.c.get("int") + 1)
            self.lis.set_value(["a", "d"])
            self.first_level.set_visible(False)

        self.qt = QTimer()
        self.qt.timeout.connect(do)
        self.qt.start(1)

        self.c.edit()
        self.c.save("co.yaml")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
