from collections import OrderedDict
import maya.cmds
import maya.mel
import maya.api.OpenMaya

from . import const
from .main import PoseyTemplate


def manage_hik(func):
    def wrapper(*args, **kwargs):

        # 1. disable IK
        # 2. Run funct
        # 3. Restore IK

        ik_states = {}
        ik_effectors = maya.cmds.ls(sl=1, type="hikIKEffector")
        for e in ik_effectors:
            ik_states[e] = [maya.cmds.getAttr(f"{e}.pull"),
                            maya.cmds.getAttr(f"{e}.reachRotation"),
                            maya.cmds.getAttr(f"{e}.reachTranslation")
                            ]

            maya.cmds.setAttr(f"{e}.pull", 0)
            maya.cmds.setAttr(f"{e}.reachRotation", 0)
            maya.cmds.setAttr(f"{e}.reachTranslation", 0)


        # hikRigAlign - enable 1 Dummy_Fight_ControlRig;
        #pinning_state = maya.mel.eval("hikGlobals -query -releaseAllPinning")

        # Prep HIK rig for editing
        #maya.mel.eval("hikGlobals -edit -releaseAllPinning 1")
        #maya.mel.eval("hikRigAlign - enable 0")
        #maya.mel.eval("hikManipStart 1 1")
        #maya.mel.eval("$gHIKneedSyncOnSetKeyframe = 0")
        #maya.mel.eval("hikGlobals - query - releaseAllPinning")

        # Run function
        func(*args, **kwargs)

        for e in ik_states:
            maya.cmds.setAttr(f"{e}.pull", ik_states[e][0])
            maya.cmds.setAttr(f"{e}.reachRotation", ik_states[e][1])
            maya.cmds.setAttr(f"{e}.reachTranslation", ik_states[e][2])

        # Return HIK rig to default state
        #maya.mel.eval("hikManipStop")
        #maya.mel.eval("hikRigAlign - enable 1")
        # maya.mel.eval(f"hikGlobals -edit -releaseAllPinning {pinning_state}")

        # Toggle time to "refresh" the rig
        # current_time = maya.cmds.currentTime(query=True)
        # maya.cmds.currentTime(current_time-1, edit=True)
        # maya.cmds.currentTime(current_time, edit=True)

    return wrapper


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

        return maya.cmds.ls(sl=True)


    def get_pose_data(self, sel):
        """
        Stores object names and their matrices into an OrderedDict()

        Args:
            sel: list, The objects to get pose data from.

        Returns: OrderedDict()

        """

        pose_data = OrderedDict()

        # For each selected obj, save worldSpace matrix to dict
        for obj in sel:
            obj_info = {"matrix": maya.cmds.getAttr(f"{obj}.worldMatrix")}
            pose_data[obj.rpartition(':')[-1]] = obj_info

        return pose_data


    @manage_hik
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

        # Build reflection matrix if mirroring is desired.
        reflection_matrix = None
        if mirror:
            # We can multiply a matrix by this to mirror it across the given axis.
            reflection_matrix = maya.api.OpenMaya.MMatrix()
            # MMatrix.setElement(row, col, val)
            reflection_matrix.setElement(const.MIRROR_MAP[mirror.lower()], const.MIRROR_MAP[mirror.lower()], -1)

        # Gather info about reference object before pasting pose to the rest of the objects.
        if ref_obj:

            if not maya.cmds.objExists(ref_obj):
                maya.cmds.error("Reference object doesn't exist. Is the name correct?")
                return False

            try:
                obj_info = pose_data[ref_obj.rpartition(':')[-1]]
            except KeyError:
                maya.cmds.error(
                    "Could not find reference object in pose file. Please select it and save the pose again")
                return False

            curr_ref_matrix = maya.cmds.xform(ref_obj, matrix=True, worldSpace=True, q=True)
            saved_ref_matrix = obj_info["matrix"]

            # TODO: Uncomment this if rotating the ref obj is desired.
            # # Build new matrix taking rotation from the saved pose and translation from the object's current position.
            # # Maya uses row major 4x4 matrices and index 12-14 represent translation
            # result_ref_matrix = saved_ref_matrix.copy()
            # result_ref_matrix[12] = curr_ref_matrix[12]
            # result_ref_matrix[13] = curr_ref_matrix[13]
            # result_ref_matrix[14] = curr_ref_matrix[14]
            #
            # # Set matrix
            # maya.cmds.xform(ref_obj, matrix=result_ref_matrix, worldSpace=True)

        else:
            curr_ref_matrix = []
            saved_ref_matrix = []

        # Find pose data for selected objects
        for obj in selection:

            # Already handled the ref object above
            if obj == ref_obj:
                continue

            # Search by name or selection order
            obj_info = {}
            if by_name:
                try:
                    obj_info = pose_data[obj.rpartition(':')[-1]]
                except KeyError:
                    maya.cmds.warning(f"Pose info not found for {obj}. Skipping.")
                    continue

            else:
                curr_idx = selection.index(obj)
                obj_info = pose_data[list(pose_data)[curr_idx]]

                if not obj_info:
                    maya.cmds.warning(f"Pose info not found for {obj}. Skipping.")
                    continue

            result_matrix = maya.api.OpenMaya.MMatrix(obj_info["matrix"])
            if ref_obj:
                # Calculate offset matrix b/w the current object's worldSpaceMatrix and the reference object's
                # worldSpaceInverse matrix. Both matrices are from the pose file.
                offset_matrix = result_matrix * maya.api.OpenMaya.MMatrix(saved_ref_matrix).inverse()

                if reflection_matrix:
                    offset_matrix = offset_matrix * reflection_matrix

                # Convert the offset matrix back into world space based on the new position of the reference object.
                # result_matrix = offset_matrix * maya.api.OpenMaya.MMatrix(result_ref_matrix)
                result_matrix = offset_matrix * maya.api.OpenMaya.MMatrix(curr_ref_matrix)

            else:

                if reflection_matrix:
                    result_matrix = result_matrix * reflection_matrix

            # Set matrix
            maya.cmds.xform(obj, matrix=result_matrix, worldSpace=True)

        print("KEY SET")
        maya.cmds.setKeyframe()

        return True


# def get_selection():
#     return maya.cmds.ls(sl=True)
#
#
# def get_pose_dict():
#
#     pose_data = OrderedDict()
#
#     # For each selected obj, save worldSpace matrix to dict
#     selection = get_selection()
#     for obj in selection:
#         obj_info = {"matrix": maya.cmds.getAttr(f"{obj}.worldMatrix")}
#         pose_data[obj.rpartition(':')[-1]] = obj_info
#
#     return pose_data
#
#
# def paste(selection, pose_data, by_name=True, ref_obj='', mirror=''):
#
#     # Build reflection matrix if mirroring is desired.
#     reflection_matrix = None
#     if mirror:
#
#         # We can multiply a matrix by this to mirror it across the given axis.
#         reflection_matrix = maya.api.OpenMaya.MMatrix()
#         # MMatrix.setElement(row, col, val)
#         reflection_matrix.setElement(const.MIRROR_MAP[mirror.lower()], const.MIRROR_MAP[mirror.lower()], -1)
#
#     # Gather info about reference object before pasting pose to the rest of the objects.
#     if ref_obj:
#
#         if not maya.cmds.objExists(ref_obj):
#             maya.cmds.error("Reference object doesn't exist. Is the name correct?")
#             return False
#
#         try:
#             obj_info = pose_data[ref_obj.rpartition(':')[-1]]
#         except KeyError:
#             maya.cmds.error("Could not find reference object in pose file. Please select it and save the pose again")
#             return False
#
#         curr_ref_matrix = maya.cmds.xform(ref_obj, matrix=True, worldSpace=True, q=True)
#         saved_ref_matrix = obj_info["matrix"]
#
#         # TODO: Uncomment this if rotating the ref obj is desired.
#         # # Build new matrix taking rotation from the saved pose and translation from the object's current position.
#         # # Maya uses row major 4x4 matrices and index 12-14 represent translation
#         # result_ref_matrix = saved_ref_matrix.copy()
#         # result_ref_matrix[12] = curr_ref_matrix[12]
#         # result_ref_matrix[13] = curr_ref_matrix[13]
#         # result_ref_matrix[14] = curr_ref_matrix[14]
#         #
#         # # Set matrix
#         # maya.cmds.xform(ref_obj, matrix=result_ref_matrix, worldSpace=True)
#
#     else:
#         curr_ref_matrix = []
#         saved_ref_matrix = []
#
#     # Find pose data for selected objects
#     for obj in selection:
#
#         # Already handled the ref object above
#         if obj == ref_obj:
#             continue
#
#         # Search by name or selection order
#         obj_info = {}
#         if by_name:
#             try:
#                 obj_info = pose_data[obj.rpartition(':')[-1]]
#             except KeyError:
#                 maya.cmds.warning(f"Pose info not found for {obj}. Skipping.")
#                 continue
#
#         else:
#             curr_idx = selection.index(obj)
#             obj_info = pose_data[list(pose_data)[curr_idx]]
#
#             if not obj_info:
#                 maya.cmds.warning(f"Pose info not found for {obj}. Skipping.")
#                 continue
#
#         result_matrix = maya.api.OpenMaya.MMatrix(obj_info["matrix"])
#         if ref_obj:
#             # Calculate offset matrix b/w the current object's worldSpaceMatrix and the reference object's
#             # worldSpaceInverse matrix. Both matrices are from the pose file.
#             offset_matrix = result_matrix * maya.api.OpenMaya.MMatrix(saved_ref_matrix).inverse()
#
#             if reflection_matrix:
#                 offset_matrix = offset_matrix * reflection_matrix
#
#             # Convert the offset matrix back into world space based on the new position of the reference object.
#             # result_matrix = offset_matrix * maya.api.OpenMaya.MMatrix(result_ref_matrix)
#             result_matrix = offset_matrix * maya.api.OpenMaya.MMatrix(curr_ref_matrix)
#
#         else:
#
#             if reflection_matrix:
#                 result_matrix = result_matrix * reflection_matrix
#
#         # Set matrix
#         maya.cmds.xform(obj, matrix=result_matrix, worldSpace=True)
#
#     return True
