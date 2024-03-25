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

        def get_value(self):
            return self.ed.currentItem().text() if self.ed.currentItem() is not None else None

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