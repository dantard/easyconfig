import sys
import traceback
from pathlib import Path

import yaml
from PyQt5.QtWidgets import (
    QDialog
)

from easyconfig.callbacks import Callback
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

    def set_callback_enabled(self, enabled):
        Callback.callback_enabled = enabled

    def root(self):
        return self.root_node

    def get_widget(self, node=None, skip_heading_subsection=False):
        node = node or self.root_node
        self.widget = ConfigWidget(node, skip_heading_subsection)
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

    def store_easyconfig_info(self, tree, node=None):
        if self.expanded:
            if node is None:
                node = self.root_node
            if tree.get("easyconfig") is None:
                tree["easyconfig"] = {}
            tree["easyconfig"].update({"expanded-" + node.key: "".join(str(e) for e in self.expanded)})

    def recover_easyconfig_info(self, tree, node=None):
        if node is None:
            node = self.root_node
        expanded = tree.get("easyconfig", {}).get("expanded-" + node.key)
        if expanded:
            self.expanded = [int(a) for a in expanded]

    def save(self, filename, node=None):

        tree = dict()
        if self.widget is not None:
            self.expanded = self.widget.get_expanded()

        if node is None:
            self.root_node.getDictionary(tree)
        else:
            with open(filename, "r") as f:
                saved_tree = yaml.safe_load(f)
            node.getDictionary(tree)
            saved_tree[node.key] = tree[node.key]
            tree = saved_tree

        self.store_easyconfig_info(tree, node)
        # print(tree)
        with open(filename, "w") as f:
            yaml.dump(tree, f, sort_keys=False)

    def load(self, filename, node=None, callbacks=False):
        try:
            with open(filename, "r") as f:
                config = yaml.safe_load(f)
                self.recover_easyconfig_info(config, node)
                # self.add_dynamic_fields(config)
                if node is None:
                    node = self.root_node
                node.load(config, callbacks=callbacks)
        except Exception as e:
            print("Config file not found or corrupted")
