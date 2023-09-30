EasyConfig
==========
This library provides a quick and easy way to create configuration screen in pyQt.
To get started it is necessary to create a ``EasyConfig`` object and add the needed configuration options. All must be done after having created a QApplication.

.. code-block:: python

   from easyconfig.EasyConfig import EasyConfig

   class MainWindow(QPushButton):
      def __init__(self):
          super().__init__()
          self.setText("Try!")
          self.setGeometry(QRect(100, 100, 100, 100))
  
          self.c = EasyConfig()
          first_level = self.c.root().addSubSection("first_level", pretty="First level")
          first_level.addLabel("Label", pretty="One label", default="hola",save=False)
          first_level.addString("string", pretty="One string", save=False, callback=lambda x,y: print("callback ",x,y))
          self.clicked.connect(self.c.edit)

   if __name__ == "__main__":
          app = QApplication(sys.argv)
      
          window = MainWindow()
          window.show()
      
          app.exec()

This example creates a simple button that, when clicked, will show a basic configuration screen (a QDialog subclass). The options contain a label and a LineEdit that can call a callback when it is changed.
Besides ``addLabel()`` and ``addLString()`` there is ``addInt()``, ``addFloat()``, ``addComboBox()``, ``addSlider()``, ``addFIleOpen()``, ``addFileSave()``, ``addEditBox()`` and ``addCheckbox()`` that create the correspondent elements of the appropiate type.
All of them have a mandatory parameter ``key`` which is the key that identifies the option added and that will appear in the configuration file once created from the configuration.

Additionally, all of them support the parameter ``pretty`` which is the name that will appear on the configuration screen. If not specified, the ``key`` will be used.
Other than this, more global parameters are:

* ``save (boolean)`` : Specifies wether or not that specific option should end up in the config file
* ``hidden (boolean)``: Specifies wether or not that specific option should be showed in the config screen 
* ``default (any basic type)``: Default value for that specific option
* ``callback (function)``: Function or method to be called when the value changes

In addition, any ``Element`` has specific options:

Integer
+++++++
* ``fmt``: format to be used (for example ``"{:02d}"``)
* ``max``: Maximum Value
* ``min``: Minimum Value

Float
+++++
* ``fmt``: format to be used (for example ``"{:.2f}"``)
* ``max``: Maximum Value
* ``min``: Minimum Value

Slider
++++++
* ``fmt``: format to be used (for example ``"{:.2f}"``)
* ``max``: Maximum Value
* ``min``: Minimum Value
* ``den``: Denominator. The value returned will be the ``QSlider.value()/den``



ComboBox
++++++++
* ``items``: The items to be added to the QCombobox (e.g. ``["one", "two", "three"]
