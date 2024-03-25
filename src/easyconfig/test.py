import sys

from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtWidgets import QPushButton, QApplication

from EasyConfig import EasyConfig


class MainWindow(QPushButton):
    def __init__(self):
        super().__init__()
        self.setText("Try!")
        self.setGeometry(QRect(100, 100, 100, 100))
        self.clicked.connect(self.create_key)

        self.config = EasyConfig(editable=True)

        root = self.config.root()
        info = root.addSubSection("info", pretty="Information")
        name = info.addString("name", pretty="Name", default="John")
        surname = info.addString("surname", pretty="Surname", default="Doe", editable=False, save=False)
        self.age = info.addInt("age", pretty="Age", default=30)
        secret = info.addString("secret", default="kjdhsjh", hidden=True)
        self.slider = info.addSlider("slider", pretty="Slider", default=50, min=0, max=100, den=100, fmt="{:.1f}", callback=lambda x, y: print(x, y))
        self.cb = info.addCheckbox("cb", pretty="Check Box", default=True)

        self.combo_box = info.addCombobox("combo_box", pretty="Combo Box", default=1, items=["Option 1", "Option 2", "Option 3"], callback=self.cba)

        hidden = root.addHidden("hidden")
        hidden.addString("hidden_string", pretty="Hidden String", default="Hidden")

        self.config.load("config.yaml")

        self.qt = QTimer()
        self.qt.timeout.connect(self.print)
        self.qt.start(1000)

        self.config.edit()

        self.config.save("config.yaml")

    def cba(self, a, b):
        print(self.cb.get_value(), a, b, self.combo_box.get_param("items"))

    def print(self):
        print(self.config.root().get("info/age"))
        print(self.slider.get_value())
        self.age.set_value(self.age.get_value() + 1)
        self.combo_box.update_param(items=["Option 1", "Option 2", "Option 3", "Option 4"])

    def create_key(self):
        self.config.root().set("info/dynamic_data", "Janeaa", create=True)
        self.config.root().set("hidden/hidden_dynamic_data", "Janeaa", create=True)

        print(self.config.root().get("info/temp2", default="Ninja2", create=True))
        self.config.save("config.yaml")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
