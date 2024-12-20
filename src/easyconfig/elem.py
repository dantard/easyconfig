from PyQt5.QtCore import QObject, pyqtSignal

from easyconfig.callbacks import Callback
from easyconfig.kind import Kind


class Elem(QObject):

    callbacks_enabled = True

    class Wrapper:
        def __init__(self, **kwargs):
            self.elem = kwargs

    elem_value_changed = pyqtSignal()
    elem_param_changed = pyqtSignal(dict)

    def __init__(self, key, kind, parent=None, **kwargs):
        super().__init__()
        self.tree_view_item = None
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
        self.widget = None
        self.dict_way = False

    def set_widget(self, widget):
        self.widget = widget

    def get_widget(self):
        return self.widget

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
        # print("update_param", kwargs)
        self.param_changed.emit(kwargs)

    def set_value(self, value, emit=True):
        if self.value != value:
            self.value = value
            self.elem_value_changed.emit()
            if self.kwargs.get("callback", None) and Callback.callbacks_enabled:
                self.kwargs["callback"](self.key, value)

    def block_widget_signals(self, block):
        if self.widget is not None:
            self.widget.block_signals(block)


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

    def getDoubleText(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.DOUBLE_TEXT, **kwargs)
        return None

    def getCombobox(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.COMBOBOX, **kwargs)
        return None

    def getCheckbox(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.CHECKBOX, **kwargs)
        return None

    def getFolderChoice(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.CHOSE_DIR, **kwargs)
        return None

    def getFileSave(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.FILE_SAVE, **kwargs)
        return None

    def getFile(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.FILE, **kwargs)
        return None

    def getFloat(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.FLOAT, **kwargs)
        return None

    def getSlider(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.SLIDER, **kwargs)
        return None

    def getLabel(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.LABEL, **kwargs)
        return None

    def getInt(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.INT, **kwargs)
        return None

    def getEditBox(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.EDITBOX, **kwargs)
        return None

    def getPassword(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.PASSWORD, **kwargs)
        return None

    def getString(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.STR, **kwargs)
        return None

    def getList(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.LIST, **kwargs)
        return None

    def getDictionary(self, name, create=True, **kwargs):
        if self.has_key(name):
            return self.get_node_by_key(name)
        elif create:
            return self.add(name, Kind.DICTIONARY, **kwargs)
        return None

    def addChild(self, elem):
        if elem.key in [c.key for c in self.child]:
            raise Exception(f"Key '{elem.key}' already exists")
        self.child.append(elem)

    def has_key(self, key):
        return self.get_child(key) is not None

    def get_node_by_key(self, key):
        return self.get_child(key)

    def addSubSection(self, key, **kwargs):

        for k, v in self.default_params.items():
            if not k in kwargs:
                kwargs[k] = v

        elem = Elem(key, Kind.SUBSECTION, self, **kwargs)
        elem.set_default_params(self.default_params, kwargs)



        self.addChild(elem)
        elem.addInt("+hidden", default=0, hidden=True, save=False)
        return elem

    def getSubSection(self, key, create=True, **kwargs):
        if self.has_key(key):
            return self.get_node_by_key(key)
        elif create:
            return self.addSubSection(key, **kwargs)
        return None

    def get_pretty(self):
        return self.kwargs.get("pretty", self.key)

    def addHidden(self, key, **kwargs):
        kwargs.update({'hidden': True})
        return self.addSubSection(key, **kwargs)

    def getHidden(self, key, create=True, **kwargs):
        if self.has_key(key):
            return self.get_node_by_key(key)
        elif create:
            return self.addHidden(key, **kwargs)
        return None

    def update_value(self, value):
        self.value = value
        callback = self.kwargs.get("callback")
        if Callback.callbacks_enabled and callback is not None:
            callback(self.key, self.value)

    def update(self, **kwargs):
        if self.widget is not None:
            self.widget.update(**kwargs)

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
                if not self.dict_way:
                    dic[self.key] = self.value
                else:
                    dic[self.key] = {"+value": self.value, "+hidden": self.hidden, "+save": self.save}


    # def load(self, dic, keys=None, callbacks=False):
    #     def traverse_dict(d):
    #         if isinstance(d, dict):
    #             keys = list(d.keys())
    #             for k in keys:
    #                 if k.endswith("@"):
    #                     value = d.pop(k)
    #                     k = k.replace("@", "")
    #                     d[k] = value
    #                     d[k]["@hidden"] = True
    #             for key, value in d.items():
    #                 traverse_dict(value)
    #         elif isinstance(d, list):
    #             for item in d:
    #                 traverse_dict(item)
    #
    #     traverse_dict(dic)
    #     print("aaa", dic)
    #     self.load_easy(dic, keys, callbacks)

    def __repr__(self):
        return "{},{}".format(self.key, self.value)

    def load(self, dic, keys=None, callbacks=False):
        if self.kind == Kind.ROOT:
            keys = []
            for c in self.child:
                c.load(dic, keys.copy(), callbacks)
        elif self.kind == Kind.SUBSECTION:
            if keys is None:
                keys = []
            keys.append(self.key)

            for c in self.child:
               c.load(dic, keys.copy(), callbacks)

               # If there is a field +hidden
               # and is true hide the field
               if c.key == "+hidden":
                   self.hidden = self.hidden or c.value
                   self.set_visible(not self.hidden)
        else:
            for k in keys:
                dic = dic.get(k)
                if dic is None:
                    break

            if dic is not None:
                Callback.callbacks_enabled = callbacks
                dict_value = dic.get(self.key, self.value)

                # NEW: MANAGE parameters for field
                # They must start with a '+' and are
                # value, hidden, save and addtionally
                # all those valid for the widget itself

                if type(dict_value) is dict and any([a.startswith('+') for a in dict_value.keys()]):
                    value = dict_value.pop("+value")
                    self.hidden = dict_value.pop("+hidden", False)
                    self.set_visible(not self.hidden)
                    self.save = dict_value.pop("+save", True)
                    clean_dict = {key.lstrip('+'): value for key, value in dict_value.items()}
                    self.kwargs.update(clean_dict)
                    self.dict_way = True
                else:
                    # OLD basic case
                    value = dict_value

                self.set_value(value)
                Callback.callbacks_enabled = True


    '''
    def get_children(self, key):
        def recu(node, found):
            if node and key and node.kind != Kind.SUBSECTION and node.key == key:
                found.append(node)
            for c in node.child:
                recu(c, found)

        nodes = []
        recu(self, nodes)
        return nodes
    '''

    def get_children(self):
        return self.child

    def get_key(self):
        return self.key

    def get_child(self, keys):
        if type(keys) == str:
            keys = keys.lstrip("/").split("/")
        elif not type(keys) in [list, tuple]:
            raise Exception("Keys must be a string or list/tuple")

        node = self
        for key in keys:
            # found refers to to this part of the key
            found = False
            for child in node.child:  # type: Elem
                if child.key == key:  # or c.pretty.lower() == p.lower():
                    found = True
                    node = child
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

    def set_visible(self, visible):
        if self.tree_view_item is not None:
            self.tree_view_item.setHidden(not visible)

    def callback(self):
        if self.kwargs.get("callback", None) and Callback.callbacks_enabled:
            self.kwargs["callback"](self.key, self.value)