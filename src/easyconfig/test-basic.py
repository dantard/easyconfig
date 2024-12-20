#!/usr/bin/env python
import sys

import yaml
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox

from EasyConfig import EasyConfig


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.v_layout = QVBoxLayout()
        helper = QWidget()
        helper.setLayout(self.v_layout)
        self.setCentralWidget(helper)

        show_btn = QPushButton("Show")
        self.v_layout.addWidget(show_btn)

        name_btn = QPushButton("Get Data")
        self.v_layout.addWidget(name_btn)

        save_btn = QPushButton("Save")
        self.v_layout.addWidget(save_btn)

        update_btn = QPushButton("Update")
        self.v_layout.addWidget(update_btn)

        show_btn.clicked.connect(self.show_info)
        save_btn.clicked.connect(self.save)
        name_btn.clicked.connect(self.get_name)
        update_btn.clicked.connect(self.update)
        QTimer.singleShot(5000, self.update)

        self.config = EasyConfig(editable=True)

        root = self.config.root()
        self.list = root.addList("list", pretty="List", type="file")
        self.info = root.addSubSection("info", pretty="Information")
        self.name = self.info.getString("name", pretty="Name", default="John")
        surname = self.info.addString("surname", pretty="Surname", default="Doe", editable=False, save=False)
        self.age = self.info.addInt("age", pretty="Age", default=30, callback=lambda x, y: print(x, y))
        self.cb = self.info.addCheckbox("married", pretty="Married", default=False)
        secret = self.info.addString("account", default="bvghfhfgh", hidden=True)

        self.work = root.getSubSection("job", pretty="Job")
        self.slider = self.work.addSlider("salary", pretty="Salary (K)", default=500, min=0, max=1000, den=10, fmt="{:.0f}", callback=lambda x, y: print(x, y))
        self.combo_box = self.work.addCombobox("position", pretty="Position", default=1, items=["Manager", "Employee", "Owner"])

        hidden = root.addHidden("hidden")
        hidden.addString("hidden_string", default="This is an Hidden String")

        self.config.load("config.yaml")

    def show_info(self):
        self.config.exec(self.config.root())
        # self.config.exec(self.info)

    def save(self):
        self.config.save("config.yaml")

    def get_name(self):
        QMessageBox.information(self, "Name",
                                "The name can be obtained this way: " + self.name.get_value() + " or this way: " + self.info.get("name") +
                                " or this way: " + self.config.root().get("info/name"))


    def update(self):
        print("updating")
        self.age.set_value(40)
        # with open("other_file.yaml", "r") as f:
        #     config = yaml.safe_load(f)
        #     self.config.root().load(config)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
