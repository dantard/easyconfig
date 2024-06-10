#!/usr/bin/env python
import sys

from PyQt5.QtCore import QRect, QTimer
from PyQt5.QtWidgets import QPushButton, QApplication, QMainWindow, QWidget, QVBoxLayout

from EasyConfig import EasyConfig


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.v_layout = QVBoxLayout()
        helper = QWidget()
        helper.setLayout(self.v_layout)
        self.setCentralWidget(helper)

        load_btn = QPushButton("Load")
        self.v_layout.addWidget(load_btn)

        try_btn = QPushButton("Show All")
        self.v_layout.addWidget(try_btn)

        show_info_btn = QPushButton("Show Info")
        self.v_layout.addWidget(show_info_btn)

        show_job_btn = QPushButton("Show Job")
        self.v_layout.addWidget(show_job_btn)

        add_section_btn = QPushButton("Add Section")
        self.v_layout.addWidget(add_section_btn)

        save_btn = QPushButton("Save")
        self.v_layout.addWidget(save_btn)

        load_btn.clicked.connect(self.load)
        try_btn.clicked.connect(self.create_key)
        show_info_btn.clicked.connect(self.show_info)
        show_job_btn.clicked.connect(self.show_job)
        add_section_btn.clicked.connect(self.add_section)
        save_btn.clicked.connect(self.save)

        self.config = EasyConfig(editable=True)

        root = self.config.root()
        self.info = root.addSubSection("info", pretty="Information")
        name = self.info.addString("name", pretty="Name", default="John")
        name = self.info.getString("name", pretty="Name", default="John")
        surname = self.info.addString("surname", pretty="Surname", default="Doe", editable=False, save=False)
        self.age = self.info.addInt("age", pretty="Age", default=30)
        self.cb = self.info.addCheckbox("married", pretty="Married", default=False)
        secret = self.info.addString("account", default="ES7473489383454", hidden=True)

        # self.work = root.addSubSection("job", pretty="Job")
        self.work = root.getSubSection("job", pretty="Job")

        self.slider = self.work.addSlider("salary", pretty="Salary (K)", default=500, min=0, max=1000, den=10, fmt="{:.1f}", callback=lambda x, y: print(x, y))
        self.slider = self.work.addSlider("Salary", pretty="Salary (K)", default=500, min=0, max=1000, den=10, fmt="{:.1f}", callback=lambda x, y: print(x, y))
        self.combo_box = self.work.addCombobox("position", pretty="Position", default=1, items=["Manager", "Employee", "Owner"], callback=self.cba)

        hidden = root.addHidden("hidden")
        hidden.addString("hidden_string", default="This is an Hidden String")

    def load(self):
        self.config.load("config.yaml")

    def show_info(self):
        self.config.exec(self.info)

    def show_job(self):
        self.config.exec(self.work)

    def add_section(self):
        new_section = self.config.root().addSubSection("new_section", pretty="New Section")
        new_section.addString("new_string", pretty="New String", default="New Value")
        self.config.load("config.yaml", new_section)
        self.config.exec(new_section)

    def save(self):
        self.config.save("config.yaml")

    def cba(self, a, b):
        print(self.cb.get_value(), a, b, self.combo_box.get_param("items"))

    def print(self):
        print(self.config.root().get("info/age"))
        print(self.slider.get_value())
        self.age.set_value(self.age.get_value() + 1)
        self.combo_box.update_param(items=["Option 1", "Option 2", "Option 3", "Option 4"])

    def create_key(self):
        self.config.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
