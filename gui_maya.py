from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtWidgets
import shiboken2
import maya.OpenMayaUI

from .gui import PoseyWinTemplate


class PoseyWin(PoseyWinTemplate):

    def get_parent_window(self):
        """
            Gets Maya's main window object

            TODO: Needs to be overridden per DCC

            Returns: Swig Object of type 'QWidget *'

        """

        ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
        if ptr is not None:
            return shiboken2.wrapInstance(int(ptr), QtWidgets.QMainWindow)
        else:
            return None


def build():
    """

    Returns: MainWindow object

    """
    #global win

    # if win:
    #     win.setObjectName("")
    #     del win

    win = PoseyWin()
    #win.setObjectName(const.TOOL_NAME)
    win.show()

    return win

