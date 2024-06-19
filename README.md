# EasyConfig

This library provides a quick and easy way to create configuration dialogs in pyQt.
To get started it is necessary to create a ``EasyConfig`` object and add the needed configuration options. All must be done after having created a QApplication.

```
import sys
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

        show_btn.clicked.connect(self.show_info)
        save_btn.clicked.connect(self.save)
        name_btn.clicked.connect(self.get_name)
        
        # Configure configuration dialog 
        
        self.config = EasyConfig(editable=True)

        root = self.config.root()
        self.info = root.addSubSection("info", pretty="Information")
        self.name = self.info.getString("name", pretty="Name", default="John")
        surname = self.info.addString("surname", pretty="Surname", default="Doe", editable=False, save=False)
        self.age = self.info.addInt("age", pretty="Age", default=30)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


```
This example creates a simple button that, when clicked, will show a basic configuration dialog.