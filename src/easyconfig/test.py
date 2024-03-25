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
        age = info.addInt("age", pretty="Age", default=30)
        secret = info.addString("secret", default="kjdhsjh", hidden=True)

        hidden = root.addHidden("hidden")
        hidden.addString("hidden_string", pretty="Hidden String", default="Hidden")

        self.config.load("config.yaml")


        self.config.edit()

        self.config.save("config.yaml")

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