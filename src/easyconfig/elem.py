from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QTreeWidgetItem, QLabel

from config_widget import ConfigWidget
from kind import Kind
from widgets import DoubleLabel, String, List, EditBox, Password, Float, ComboBox, Checkbox, FolderChoice, SaveFile, File, Slider, Label, Integer


class Elem(QObject):

    class Wrapper:
        def __init__(self, **kwargs):
            self.elem = kwargs

    value_changed = pyqtSignal()
    param_changed = pyqtSignal(dict)


    def __init__(self, key, kind, parent=None, **kwargs):
        super().__init__()
        self.kind = kind
        self.kwargs = kwargs
        self.save = kwargs.get("save", True)
        self.hidden = kwargs.get("hidden", False)
        self.value = kwargs.get("default", None)
        self.default_params = {}
        self.key = key
        self.child = []
        self.parent = parent
        self.node = None

    def set_default_params(self, params_dict, append=None, remove=None):
        self.default_params = params_dict.copy()

        if append is not None:
            self.default_params.update(append)

        # Do not propagate the pretty and default parameters
        remove = ["pretty", "default"] + (remove if remove else [])
        for p in remove:
            self.default_params.pop(p, None)

    def get_value(self):
        return self.value

    def update_param(self, **kwargs):
        print("update_param", kwargs)
        self.param_changed.emit(kwargs)

    def set_value(self, value, emit=True):
        self.value = value
        self.value_changed.emit()

    def add(self, key, kind=Kind.STR, **kwargs):

        for k, v in self.default_params.items():
            if not k in kwargs:
                kwargs[k] = v

        if '/' in key:
            if key.startswith("/") and self.kind != Kind.ROOT:
                raise Exception("A key can begin with '/' only if adding from the root node")

            key = key if not key.startswith("/") else key[1:]
            fields = key.split("/")
            node, field_index = self, -1
            for i, field in enumerate(fields):
                for child in node.child:  # type: Elem
                    if child.key == field:
                        node = child
                        field_index = i
                        break

            for i in range(field_index + 1, len(fields) - 1):
                node = node.addSubSection(fields[i])

            elem = Elem(fields[-1], kind, self, **kwargs)
            elem.set_default_params(self.default_params)
            node.addChild(elem)

        else:
            elem = Elem(key, kind, self, **kwargs)
            elem.set_default_params(self.default_params)
            self.addChild(elem)

        return elem

    def addString(self, name, **kwargs):
        return self.add(name, Kind.STR, **kwargs)

    def addDict(self, name, **kwargs):
        return self.add(name, Kind.DICTIONARY, **kwargs)

    def addList(self, name, **kwargs):
        return self.add(name, Kind.LIST, **kwargs)

    def addEditBox(self, name, **kwargs):
        return self.add(name, Kind.EDITBOX, **kwargs)

    def addPassword(self, name, **kwargs):
        return self.add(name, Kind.PASSWORD, **kwargs)

    def addInt(self, name, **kwargs):
        return self.add(name, Kind.INT, **kwargs)

    def addLabel(self, name, **kwargs):
        return self.add(name, Kind.LABEL, **kwargs)

    def addSlider(self, name, **kwargs):
        return self.add(name, Kind.SLIDER, **kwargs)

    def addFloat(self, name, **kwargs):
        return self.add(name, Kind.FLOAT, **kwargs)

    def addFile(self, name, **kwargs):
        return self.add(name, Kind.FILE, **kwargs)

    def addFileSave(self, name, **kwargs):
        return self.add(name, Kind.FILE_SAVE, **kwargs)

    def addFolderChoice(self, name, **kwargs):
        return self.add(name, Kind.CHOSE_DIR, **kwargs)

    def addCheckbox(self, name, **kwargs):
        return self.add(name, Kind.CHECKBOX, **kwargs)

    def addCombobox(self, name, **kwargs):
        return self.add(name, Kind.COMBOBOX, **kwargs)

    def addDoubleText(self, name, **kwargs):
        return self.add(name, Kind.DOUBLE_TEXT, **kwargs)

    def addChild(self, elem):
        self.child.append(elem)

    def addSubSection(self, key, **kwargs):

        for k, v in self.default_params.items():
            if not k in kwargs:
                kwargs[k] = v

        elem = Elem(key, Kind.SUBSECTION, self, **kwargs)
        elem.set_default_params(self.default_params, kwargs)

        self.addChild(elem)
        return elem

    def get_pretty(self):
        return self.kwargs.get("pretty", self.key)

    def addHidden(self, key, **kwargs):
        kwargs.update({'hidden': True})
        return self.addSubSection(key, **kwargs)

    def update_value(self, value):
        self.value = value
        print("Update value", self.key, value)
        callback = self.kwargs.get("callback")
        if callback is not None:
            callback(self.key, self.value)

    def getDictionary(self, dic):
        if self.kind == Kind.ROOT:
            dic.clear()
            for c in self.child:
                c.getDictionary(dic)
        elif self.kind == Kind.SUBSECTION:
            if self.save:
                dic[self.key] = {}
                dic = dic[self.key]
                for c in self.child:
                    c.getDictionary(dic)
        else:
            if self.save:
                dic[self.key] = self.value

    def load(self, dic, keys=None):
        if self.kind == Kind.ROOT:
            keys = []
            for c in self.child:
                c.load(dic, keys.copy())
        elif self.kind == Kind.SUBSECTION:
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
                print("setting", self.key, self.value)

    def get_children(self, key):
        def recu(node, found):
            if node and key and node.kind != Kind.SUBSECTION and node.key.lower() == key.lower():
                found.append(node)
            for c in node.child:
                recu(c, found)

        nodes = []
        recu(self, nodes)
        return nodes

    def get_child(self, keys):
        node = self
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

    def get(self, key, **kwargs):

        if key.startswith("/"):
            raise Exception("Paths must be relative to current node (remove heading '/')")

        default = kwargs.get("default", None)
        create = kwargs.get("create", False)

        if key is None:
            return None  # , val=value)

        path = key.split("/")
        node = self.get_child(path)
        if node is not None:
            return node.value if node.value is not None else default
        elif create:
            if self.get_child(path[0]) is None:
                raise Exception("Dynamic field *must* be child of non-dynamic field ({} not found)".format(path[0]))

            default = default if default is not None else str()
            elem = self.add(key, Kind.type2Kind(default), default=default)
            elem.set_default_params(kwargs)
            return default
        else:
            raise Exception("Key {} not found".format(key))

    def set(self, key, value, **kwargs):

        if key.startswith("/"):
            raise Exception("Paths must be relative to current node (remove heading '/')")

        if key is None:
            return None

        create = kwargs.get("create", False)
        kind = kwargs.get("kind", Kind.type2Kind(value))

        path = key.split("/")
        node = self.get_child(path)
        if node is not None:
            node.set_value(value)
        elif create:
            if self.get_child(path[0]) is None:
                raise Exception("Dynamic field *must* be child of non-dynamic field ({} not found)".format(path[0]))

            elem = self.add(key, kind)
            elem.set_value(value)
            return True
        else:
            raise Exception("Key {} not found".format(key))

    def get_param(self, key, default=None):
        return self.kwargs.get(key, default)
