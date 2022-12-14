"""
Copy and Paste poses
"""

import sys
import json
from pathlib import Path
from collections import OrderedDict
from abc import ABC, abstractmethod

from . import const


class PoseyTemplate(ABC):
    """
    Template class containing all the necessary methods for reading and writing poses. This class is meant to
    be inherited from per DCC.
    """

    def __init__(self):
        pass

    def copy(self, filepath=""):
        """
        Copies the pose of the current selection to the specified file. If no filepath is
        provided, the clipboard will be used.

        Returns: bool

        """

        # Get selection
        sel = self.get_selection()
        if not sel:
            return False

        # Get pose data from selection
        pose = self.get_pose_data(sel)
        if not pose:
            return False

        # Write to file
        self.serialize_pose(pose)

        return True

    def deserialize_pose(self, filepath=""):
        """
        Converts the pose in the specified file into an OrderedDict(). If no filepath is specified,
        the clipboard will be used.

        Returns: OrderedDict()

        """

        if not filepath:
            filepath = const.CLIPBOARD

        pose_data = OrderedDict()
        with open(filepath, "r", encoding="ascii") as pose_file:
            pose_data = json.loads(pose_file.read(), object_pairs_hook=OrderedDict)

        return pose_data

    @abstractmethod
    def get_selection(self):
        """
        Gets the current selection

        TODO: Needs to be overridden per DCC

        Returns: list

        """

        return []

    @abstractmethod
    def get_pose_data(self, sel):
        """
        Stores object names and their matrices into an OrderedDict()

        Args:
            sel: list, The objects to get pose data from.

        TODO: Needs to be overridden per DCC

        Returns: OrderedDict()

        """

        return OrderedDict()

    def paste(self, filepath="", by_name=True, ref_obj='', mirror=''):
        """
        Pastes the specified pose to the current selection. If no filepath is specified,
        the clipboard will be used.

        TODO: Switch mirror axis to mirror plane
        TODO: Switch prints() to logs

        Args:
            filepath: str, The file containing the pose
            by_name: bool, Determines whether the pose will be pasted by name or selection order
            ref_obj: str, Name of the object to paste pose relative to. This is typically the hip control.
            mirror: str, the axis on which to mirror the pose over

        Returns: bool

        """

        # Get selection
        selection = self.get_selection()
        if not selection:
            print("Could not paste pose. Nothing has been selected")
            return False

        # Mirror check
        if mirror and mirror.lower() not in list(const.MIRROR_MAP):
            print("Invalid mirror kwarg passed. Accepts 'x', 'y', or 'z'")
            return False

        # Get pose data
        pose_data = self.deserialize_pose(filepath=filepath)
        if not pose_data:
            print("Clipboard is empty. Please select an object and copy the pose again.")
            return False

        # Perform DCC specific paste
        result = self.paste_dcc(selection, pose_data, by_name=by_name, ref_obj=ref_obj, mirror=mirror)
        return result

    @abstractmethod
    def paste_dcc(self, selection, pose_data, by_name=True, ref_obj='', mirror=''):
        """
        Paste method specific to each DCC. Should always be called by paste()

        TODO: Needs to be overridden per DCC

        Args:
            selection: list, Selected objects to paste to
            pose_data: OrderedDict(), The pose to paste
            by_name: bool, Determines whether the pose will be pasted by name or selection order
            ref_obj: str, Name of the object to paste pose relative to. This is typically the hip control.
            mirror: str, the axis on which to mirror the pose over

        Returns: bool

        """

        return False

    def serialize_pose(self, pose_data, filepath=""):
        """
        Writes pose to the specified file. If no filepath is provided, the clipboard will be used.

        Args:
            pose_data: OrderedDict(), The pose data from get_pose_data()
            filepath: str, The file to write to

        Returns: bool

        """

        if not filepath:
            filepath = const.CLIPBOARD

        with open(filepath, "w", encoding="ascii") as pose_file:
            json_obj = json.dumps(pose_data)
            pose_file.write(json_obj)

        return True


### FUNCTIONAL ###


# def copy(filepath=""):
#     """
#     Copies the pose of the current selection to Clipboard.json
#
#     Returns:
#         _type_: _description_
#     """
#
#     pose_data = app.get_pose_dict()
#     if not pose_data:
#         print("Couldn't copy pose. Select some objects and try again.")
#         return False
#
#     if not filepath:
#         filepath = const.CLIPBOARD
#     else:
#         filepath = Path(filepath)
#
#     with open(filepath, "w", encoding="ascii") as clipboard:
#         json_obj = json.dumps(pose_data)
#         clipboard.write(json_obj)
#
#     return True
#
#
# def paste(by_name=True, ref_obj='', mirror=''):
#     """
#     Pastes pose from clipboard onto the current selection.
#
#     Args:
#         by_name (bool, optional): If True, pose will be pasted by object names. If False,
#         pose will be pasted by selection order. Defaults to True.
#         ref_obj (string, optional): Name of the object to paste pose relative to. This is typically the hip control.
#         mirror (str, optional): Axis to reflect the mirror over. Accepts 'x', 'y' or 'z'
#
#     Returns:
#         bool: True if pose pasted successfully.
#     """
#
#     selection = app.get_selection()
#     if not selection:
#         print("Could not paste pose. Nothing has been selected")
#         return False
#
#     # Get pose data from clipboard file
#     if not const.CLIPBOARD.exists():
#         print("Clipboard file doesn't exist. Please save a pose and try again.")
#         return False
#
#     if mirror and (isinstance(mirror, str) is False or mirror.lower() not in list(const.MIRROR_MAP)):
#         print("Invalid mirror kwarg passed. Accepts 'x', 'y', or 'z'")
#         return False
#
#     pose_data = OrderedDict()
#     with open(const.CLIPBOARD, "r", encoding="ascii") as clipboard:
#         pose_data = json.loads(clipboard.read(), object_pairs_hook=OrderedDict)
#
#     if not pose_data:
#         print("Clipboard is empty. Please select an object and copy the pose again.")
#         return False
#
#     result = app.paste(selection, pose_data, by_name=by_name, ref_obj=ref_obj, mirror=mirror)
#     return result
