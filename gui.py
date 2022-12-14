"""
Module containing Posey's GUI
"""

import sys
from pathlib import Path
from PySide2 import QtGui, QtWidgets, QtCore
from . import const

# TODO: This is a little redundant since we do the same thing in __init__.py
app_name = Path(sys.argv[0]).stem.lower()
if app_name == "maya":
    from .app_maya import Posey
else:
    from .app_stubin import Posey


class PoseyWinTemplate(QtWidgets.QWidget):
    """
    Class containing UI elements and connections.
    """

    def __init__(self):
        super(PoseyWinTemplate, self).__init__(parent=self.get_parent_window())

        self.posey = Posey()

        # Window Settings
        self.setWindowFlags(QtCore.Qt.Window)  # Ensures GUI appears as a window
        self.setWindowTitle(const.TOOL_NAME)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Main layout
        self.layout_main = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout_main)

        # Tab Widget Init
        self.tab_widget = QtWidgets.QTabWidget()

        self.tab_temp = QtWidgets.QWidget()
        self.layout_tab_temp = QtWidgets.QVBoxLayout()
        self.tab_temp.setLayout(self.layout_tab_temp)
        self.tab_widget.addTab(self.tab_temp, "Temp")

        self.tab_lib = QtWidgets.QWidget()
        self.layout_tab_lib = QtWidgets.QGridLayout()

        self.tab_lib.setLayout(self.layout_tab_lib)
        self.tab_widget.addTab(self.tab_lib, "Library")

        self.layout_main.addWidget(self.tab_widget)

        ### Tab Temp ###

        # Reference Object
        self.line_ref_obj = QtWidgets.QLineEdit()
        self.line_ref_obj.setPlaceholderText("Reference Object (Optional)")

        # Copy & Paste
        self.btn_copy = QtWidgets.QPushButton()
        self.btn_copy.setText("Copy")
        self.btn_copy.clicked.connect(self.on_copy_temp)

        self.btn_paste = QtWidgets.QPushButton()
        self.btn_paste.setText("Paste")
        self.btn_paste.clicked.connect(self.on_paste)

        self.copy_paste_layout = QtWidgets.QHBoxLayout()
        self.copy_paste_layout.addWidget(self.btn_copy)
        self.copy_paste_layout.addWidget(self.btn_paste)

        self.layout_tab_temp.addWidget(self.line_ref_obj)
        self.layout_tab_temp.addLayout(self.copy_paste_layout)

        ### Tab Library ###

        # Actions
        self.action_copy  = QtWidgets.QAction("Copy")
        self.action_copy.triggered.connect(self.on_copy)

        self.tab_lib.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.tab_lib.addAction(self.action_copy)

        ### Logger ###

        # self.text_edit_logger = QtWidgets.QPlainTextEdit()
        # self.text_edit_logger.setReadOnly(True)
        # self.text_edit_logger.setFixedHeight(100)
        # self.layout_main.addWidget(self.text_edit_logger)


    def get_parent_window(self):
        """
            Gets DCC's main window object

            TODO: Needs to be overridden per DCC

            Returns: None

        """
        return None


    def on_copy(self):
        # Create icon in grid view
        i = 0
        while i <= 15:
            label = QtWidgets.QLabel()
            label.setMinimumSize(32, 32)
            label.setMaximumSize(128, 128)
            pixmap = QtGui.QPixmap(str(Path(const.IMG_DIR, "placeholder.jpg").resolve()))
            #label.resize(150, 150)
            label.setPixmap(pixmap.scaled(label.size(), QtCore.Qt.KeepAspectRatio))

            # Check how many rows there are
            # Check how many items are in current row
            # If number of items < max items, add to row
            # Else, create new row
            children = self.layout_tab_lib.children()
            if children:
                last_item_pos = self.layout_tab_lib.getItemPosition(len(children) - 1)
                print(last_item_pos)

            self.layout_tab_lib.addWidget(label)
            i += 1


    def on_copy_temp(self):
        """
        Copy pose from selected objects

        Returns: bool

        """

        result = self.posey.copy(filepath="")
        return result


    def on_paste(self):
        """
        Paste pose to selected objects

        Returns: bool

        """

        result = self.posey.paste(filepath="", by_name=True, ref_obj=self.line_ref_obj.text(), mirror="")
        return result


def build():
    """

    Returns: MainWindow object

    """

    win = PoseyWinTemplate()
    win.show()

    return win
