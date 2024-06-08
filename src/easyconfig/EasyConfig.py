import sys
import traceback
from pathlib import Path

import yaml
from PyQt5.QtWidgets import (
    QDialog
)

from easyconfig.config_widget import ConfigWidget
from easyconfig.dialog import Dialog
from easyconfig.elem import Elem
from easyconfig.kind import Kind


class EasyConfig:

    def __init__(self, **kwargs):
        self.min_height = None
        self.min_width = None
        self.root_node = Elem("root", Kind.ROOT, None)
        self.root_node.set_default_params(kwargs)
        self.reserved = "main"
        self.expanded = None
        self.widget = None

    def root(self):
        return self.root_node

    def get_widget(self):
        self.widget = ConfigWidget(self.root_node)
        if self.expanded:
            self.widget.set_expanded(self.expanded)
        return self.widget

    def set_dialog_minimum_size(self, width=None, height=None):
        self.min_width = width
        self.min_height = height

    def exec(self, node=None):
        return self.edit(node)

    def edit(self, node=None):
        if node is None:
            node = self.root_node

        config_widget = ConfigWidget(node)
        dialog = Dialog(config_widget)

        if self.min_width is not None:
            config_widget.setMinimumWidth(self.min_width)
        if self.min_height is not None:
            config_widget.setMinimumHeight(self.min_height)

        config_widget.list.collapseAll()
        if self.expanded:
            config_widget.set_expanded(self.expanded)

        res = dialog.exec()
        self.expanded = config_widget.get_expanded()

        if res == QDialog.Accepted:
            config_widget.collect()

        return res

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

    def add_dynamic_fields(self, config):
        paths = self.traverse_and_store_paths(config)
        # print("paths", paths)
        for path in paths:

            # Check if this path exists
            if self.root().get_child(path) is not None:
                # print("Path already exists", path)
                continue

            # Check if this path exists as a dictionary
            is_it_a_dictionary = self.root().get_child(path[:-1])
            if is_it_a_dictionary is not None and is_it_a_dictionary.kind == Kind.DICTIONARY:
                continue

            if len(path) > 0:
                node = self.root().get_child([path[0]])
                if node is None or node.kind != Kind.SUBSECTION:
                    # Not an easyconfig dynamic path
                    continue

                for i in range(1, len(path) - 1):
                    child = self.root().get_child(path)(path[0:i + 1])
                    if child is None:
                        node = node.add(path[i], Kind.SUBSECTION)
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

    def load(self, filename, node=None):
        print(node)
        try:
            with open(filename, "r") as f:
                config = yaml.safe_load(f)
                self.recover_easyconfig_info(config)
                # self.add_dynamic_fields(config)
                if node is None:
                    node = self.root_node
                node.load(config)


        except:
            traceback.print_exc()
