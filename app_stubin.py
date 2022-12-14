from collections import OrderedDict

from .main import PoseyTemplate


class Posey(PoseyTemplate):
    """
    Sub-class of PoseyTemplate() containing Maya specific code.
    """

    def __init__(self):
        super(Posey, self).__init__()


    def get_selection(self):
        """
        Gets the current selection

        Returns: list

        """

        return []


    def get_pose_data(self, sel):
        """
        Stores object names and their matrices into an OrderedDict()

        Args:
            sel: list, The objects to get pose data from.

        Returns: OrderedDict()

        """

        pose_data = OrderedDict()
        return pose_data


    def paste_dcc(self, selection, pose_data, by_name=True, ref_obj='', mirror=''):
        """
        Paste method specific to each DCC. Should always be called by paste().

        Args:
            selection: list, Selected objects to paste to
            pose_data: OrderedDict(), The pose to paste
            by_name: bool, Determines whether the pose will be pasted by name or selection order
            ref_obj: str, Name of the object to paste pose relative to. This is typically the hip control.
            mirror: str, the axis on which to mirror the pose over

        Returns: bool

        """

        return False
