from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import os
import json
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance


class Renamer:
    def __init__(self):
        return

    def _run_in_undochunk(func):
        """ Run function in undochunk for single click undoing. """
        def _wrapper_run_in_undochunk(self, *args):
            try:
                cmds.undoInfo(openChunk=True)
                func(self, *args)
            finally:
                cmds.undoInfo(closeChunk=True)
        return _wrapper_run_in_undochunk

    @_run_in_undochunk
    def add_suffix(self, suffix):
        initial_selection = self.selection
        for index in range(len(initial_selection)):
            old_long_name = self.selection[index]
            new_name = old_long_name.split("|")[-1] + suffix
            cmds.rename(old_long_name, new_name)

    @_run_in_undochunk
    def add_prefix(self, prefix):
        initial_selection = self.selection
        for index in range(len(initial_selection)):
            old_long_name = self.selection[index]
            new_short_name = prefix + old_long_name.split("|")[-1]
            cmds.rename(old_long_name, new_short_name)

    @_run_in_undochunk
    def search_replace(self, search_str, replace_str):
        initial_selection = self.selection
        for index in range(len(initial_selection)):
            old_long_name = self.selection[index]
            old_short_name = old_long_name.split("|")[-1]
            new_short_name = old_short_name.replace(search_str, replace_str)
            cmds.rename(old_long_name, new_short_name)

    @_run_in_undochunk
    def rename_and_number(self, rename_str, padding):
        padding = len(padding)
        initial_selection = self.selection
        for index in range(len(initial_selection)):
            old_long_name = self.selection[index]
            new_short_name = rename_str + str(index + 1).zfill(padding)
            cmds.rename(old_long_name, new_short_name)

    @_run_in_undochunk
    def auto_suffix_joints(self):
        joints_list = cmds.ls(type="joint")
        type_suffix = "_JNT"
        for index in range(len(joints_list)):
            old_long_name = cmds.ls(type="joint")[index]
            if not old_long_name.endswith(type_suffix):
                new_name = old_long_name.split("|")[-1] + type_suffix
                cmds.rename(old_long_name, new_name)

    @_run_in_undochunk
    def auto_suffix_locators(self):
        joints_list = cmds.ls(type="locator")
        type_suffix = "_LOC"
        for index in range(len(joints_list)):
            loc_shape_name = cmds.ls(type="locator")[index]
            locator_transform = cmds.listRelatives(loc_shape_name, p=True, f=True)[0]
            if not locator_transform.endswith(type_suffix):
                new_name = locator_transform.split("|")[-1] + type_suffix
                cmds.rename(locator_transform, new_name)

    @_run_in_undochunk
    def auto_suffix_meshes(self):
        joints_list = cmds.ls(type="mesh")
        type_suffix = "_GEO"
        for index in range(len(joints_list)):
            mesh_shape_name = cmds.ls(type="mesh")[index]
            locator_transform = cmds.listRelatives(mesh_shape_name, p=True, f=True)[0]
            if not locator_transform.endswith(type_suffix):
                new_name = locator_transform.split("|")[-1] + type_suffix
                cmds.rename(locator_transform, new_name)

    @property
    def selection(self):
        return cmds.ls(sl=True, l=True)


def maya_main_window():
    """ return maya main window as QWidget object """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class RenamerUI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(RenamerUI, self).__init__(parent)
        self.renamer = rc.Renamer()
        self.user_script_directory = cmds.internalVar(usd=True)
        self.user_preset_file = "MM_rename_user_presets.json"
        self.user_preset_path = self.user_script_directory + self.user_preset_file
        self.init_ui()
        self.create_user_presets()

    def init_ui(self):
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # remove ? button
        self.setFixedWidth(300)
        self.setWindowTitle("MM Rename")
        self.setObjectName("MM_Rename")
        self.create_widgets()
        self.create_connections()
        self.create_layouts()
        self.show()
        self.setFixedSize(self.size())

    def create_widgets(self):
        # Tab 1
        self.prefix_line = QtWidgets.QLineEdit()
        self.suffix_line = QtWidgets.QLineEdit()
        self.search_line = QtWidgets.QLineEdit()
        self.replace_line = QtWidgets.QLineEdit()
        self.rename_line = QtWidgets.QLineEdit()
        self.padding_menu = QtWidgets.QComboBox()
        self.padding_menu.addItems(["01", "1", "001", "0001", "00001", "000001"])
        self.padding_menu.setFixedWidth(70)
        self.add_prefix_btn = QtWidgets.QPushButton("+ Prefix")
        self.add_prefix_btn.setFixedSize(55, 20)
        self.add_suffix_btn = QtWidgets.QPushButton("+ Suffix")
        self.add_suffix_btn.setFixedSize(55, 20)
        self.replace_btn = QtWidgets.QPushButton("Replace")
        self.replace_btn.setFixedSize(55, 20)
        self.rename_btn = QtWidgets.QPushButton("Rename")
        self.rename_btn.setFixedSize(55, 20)
        self.prefix_preset_btn = QtWidgets.QPushButton("+ Prefix")
        self.prefix_preset_menu = QtWidgets.QComboBox()
        self.prefix_preset_menu.setFixedWidth(70)
        self.prefix_preset_btn.setFixedSize(55, 20)
        self.suffix_preset_btn = QtWidgets.QPushButton("+ Suffix")
        self.suffix_preset_btn.setFixedSize(55, 20)
        self.suffix_preset_menu = QtWidgets.QComboBox()
        self.suffix_preset_menu.setFixedWidth(70)

        # Tab 2
        self.auto_suffix_joints_btn = QtWidgets.QPushButton("Auto Suffix Joints")
        self.auto_suffix_meshes_btn = QtWidgets.QPushButton("Auto Suffix Meshes")
        self.auto_suffix_locators_btn = QtWidgets.QPushButton("Auto Suffix Locators")

        # Tab3
        self.add_prefix_preset_btn = QtWidgets.QPushButton("Add Prefix")
        self.add_prefix_preset_btn.setFixedSize(90, 20)
        self.add_suffix_preset_btn = QtWidgets.QPushButton("Add Suffix")
        self.add_suffix_preset_btn.setFixedSize(90, 20)
        self.remove_prefix_preset_btn = QtWidgets.QPushButton("Remove Prefix")
        self.remove_prefix_preset_btn.setFixedSize(90, 20)
        self.remove_suffix_preset_btn = QtWidgets.QPushButton("Remove Suffix")
        self.remove_suffix_preset_btn.setFixedSize(90, 20)
        self.add_prefix_preset_line = QtWidgets.QLineEdit()
        self.add_suffix_preset_line = QtWidgets.QLineEdit()
        self.remove_prefix_preset_menu = QtWidgets.QComboBox()
        self.remove_suffix_preset_menu = QtWidgets.QComboBox()

        regexp = QtCore.QRegExp('^([a-zA-Z]+)$')
        text_validator = QtGui.QRegExpValidator(regexp)
        self.add_prefix_preset_line.setValidator(text_validator)
        self.add_suffix_preset_line.setValidator(text_validator)

    def create_connections(self):
        self.add_suffix_btn.clicked.connect(lambda: self.renamer.add_suffix(self.suffix_line.text()))
        self.add_prefix_btn.clicked.connect(lambda: self.renamer.add_prefix(self.prefix_line.text()))
        self.replace_btn.clicked.connect(
            lambda: self.renamer.search_replace(self.search_line.text(), self.replace_line.text()))
        self.rename_btn.clicked.connect(
            lambda: self.renamer.rename_and_number(self.rename_line.text(), self.padding_menu.currentText()))
        self.prefix_preset_btn.clicked.connect(
            lambda: self.renamer.add_prefix(self.prefix_preset_menu.currentText() + "_"))
        self.suffix_preset_btn.clicked.connect(
            lambda: self.renamer.add_suffix("_" + self.suffix_preset_menu.currentText()))
        self.auto_suffix_joints_btn.clicked.connect(self.renamer.auto_suffix_joints)
        self.auto_suffix_locators_btn.clicked.connect(self.renamer.auto_suffix_locators)
        self.auto_suffix_meshes_btn.clicked.connect(self.renamer.auto_suffix_meshes)
        self.add_prefix_preset_btn.clicked.connect(self.add_prefix_preset)
        self.add_suffix_preset_btn.clicked.connect(self.add_suffix_preset)
        self.remove_prefix_preset_btn.clicked.connect(self.remove_prefix_preset)
        self.remove_suffix_preset_btn.clicked.connect(self.remove_suffix_preset)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.tabs = QtWidgets.QTabWidget()
        self.main_layout.addWidget(self.tabs)
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tabs.addTab(self.tab1, "Main")
        self.tabs.addTab(self.tab2, "Auto Rename")
        self.tabs.addTab(self.tab3, "User Presets")

        # Tab 1
        tab1_layout = QtWidgets.QVBoxLayout()
        tab1_form_layout = QtWidgets.QFormLayout()
        tab1_form_layout.setSpacing(6)
        tab1_form_layout.addRow(self._spacer())
        tab1_form_layout.addRow(self.add_prefix_btn, self.prefix_line)
        tab1_form_layout.addRow(self.add_suffix_btn, self.suffix_line)
        tab1_form_layout.addRow(self._separator())
        tab1_form_layout.addRow("Search", self.search_line)
        tab1_form_layout.addRow(self.replace_btn, self.replace_line)
        tab1_form_layout.addRow(self._separator())
        tab1_form_layout.addRow(self.rename_btn, self.rename_line)
        tab1_form_layout.addRow("# Padding:", self.padding_menu)
        tab1_form_layout.addRow(self._separator())
        tab1_form_layout.addRow(self.prefix_preset_btn, self.prefix_preset_menu)
        tab1_form_layout.addRow(self.suffix_preset_btn, self.suffix_preset_menu)
        tab1_layout.addLayout(tab1_form_layout)
        tab1_layout.addStretch()
        self.tab1.setLayout(tab1_layout)

        # Tab 2
        tab2_layout = QtWidgets.QVBoxLayout()
        tab2_layout.setSpacing(6)
        tab2_layout.addWidget(self.auto_suffix_joints_btn)
        tab2_layout.addWidget(self.auto_suffix_locators_btn)
        tab2_layout.addWidget(self.auto_suffix_meshes_btn)
        tab2_layout.addStretch()
        self.tab2.setLayout(tab2_layout)

        # Tab 3
        tab3_layout = QtWidgets.QVBoxLayout()
        tab3_form_layout = QtWidgets.QFormLayout()
        tab3_form_layout.addRow(self.add_prefix_preset_btn, self.add_prefix_preset_line)
        tab3_form_layout.addRow(self.add_suffix_preset_btn, self.add_suffix_preset_line)
        tab3_form_layout.addRow(self.remove_prefix_preset_btn, self.remove_prefix_preset_menu)
        tab3_form_layout.addRow(self.remove_suffix_preset_btn, self.remove_suffix_preset_menu)
        tab3_layout.setSpacing(6)
        tab3_layout.addLayout(tab3_form_layout)
        tab3_layout.addStretch()
        self.tab3.setLayout(tab3_layout)

        self.setLayout(self.main_layout)

    def create_user_presets(self):
        """Check if presets file exists, if not, create it with default settings"""
        user_presets = {
            "prefix": [
                "L",  # Left
                "R",  # Right
                "C",  # Center
                "B",  # Back
                "F"   # Front
            ],
            "suffix": [
                "JNT",  # Joint
                "GRP",  # Groups
                "GEO",  # Geo
                "LOC",  # Locator
                "CTL",  # Controller
            ]
        }
        if self.user_preset_file not in os.listdir(self.user_script_directory):
            with open(self.user_preset_path, 'w') as file_for_write:
                json.dump(user_presets, file_for_write, indent=4)
        else:
            with open(self.user_preset_path, "r") as file_for_read:
                user_presets = json.load(file_for_read)
        self.prefix_preset_menu.addItems(user_presets["prefix"])
        self.suffix_preset_menu.addItems(user_presets["suffix"])
        self.remove_prefix_preset_menu.addItems(user_presets["prefix"])
        self.remove_suffix_preset_menu.addItems(user_presets["suffix"])

    @staticmethod
    def _separator(space=10):
        """ create separator from QFrame object """
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setLineWidth(1)
        separator.setFixedHeight(space)
        return separator

    @staticmethod
    def _spacer(space=0):
        """ Create empty space object """
        separator = QtWidgets.QFrame()
        separator.setLineWidth(1)
        separator.setFixedHeight(space)
        return separator

    def refresh_preset_menus(self):
        with open(self.user_preset_path, "r") as file_for_read:
            user_presets = json.load(file_for_read)

        self.prefix_preset_menu.clear()
        self.suffix_preset_menu.clear()
        self.remove_prefix_preset_menu.clear()
        self.remove_suffix_preset_menu.clear()

        self.prefix_preset_menu.addItems(user_presets["prefix"])
        self.suffix_preset_menu.addItems(user_presets["suffix"])
        self.remove_prefix_preset_menu.addItems(user_presets["prefix"])
        self.remove_suffix_preset_menu.addItems(user_presets["suffix"])

    def add_prefix_preset(self):
        with open(self.user_preset_path, "r") as file_for_read:
            user_presets = json.load(file_for_read)
        user_presets["prefix"].append(self.add_prefix_preset_line.text())
        with open(self.user_preset_path, 'w') as file_for_write:
            json.dump(user_presets, file_for_write, indent=4)
        self.refresh_preset_menus()


    def add_suffix_preset(self):
        with open(self.user_preset_path, "r") as file_for_read:
            user_presets = json.load(file_for_read)
        user_presets["suffix"].append(self.add_suffix_preset_line.text())
        with open(self.user_preset_path, 'w') as file_for_write:
            json.dump(user_presets, file_for_write, indent=4)
        self.refresh_preset_menus()

    def remove_prefix_preset(self):
        with open(self.user_preset_path, "r") as file_for_read:
            user_presets = json.load(file_for_read)
        user_presets["prefix"].remove(self.remove_prefix_preset_menu.currentText())
        with open(self.user_preset_path, 'w') as file_for_write:
            json.dump(user_presets, file_for_write, indent=4)
        self.refresh_preset_menus()

    def remove_suffix_preset(self):
        with open(self.user_preset_path, "r") as file_for_read:
            user_presets = json.load(file_for_read)
        user_presets["suffix"].remove(self.remove_suffix_preset_menu.currentText())
        with open(self.user_preset_path, 'w') as file_for_write:
            json.dump(user_presets, file_for_write, indent=4)
        self.refresh_preset_menus()


if __name__ == "__main__":
    if cmds.window("MM_Rename", q=True, ex=True):
        cmds.deleteUI("MM_Rename")
    renamer_ui = RenamerUI()