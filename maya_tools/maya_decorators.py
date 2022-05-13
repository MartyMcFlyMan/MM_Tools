import maya.cmds as cmds


def run_in_undochunk(func):
    """ Run function in undochunk for single click undoing. """
    def _wrapper_run_in_undochunk():
        try:
            cmds.undoInfo(openChunk=True)
            func()
        finally:
            cmds.undoInfo(closeChunk=True)
    return _wrapper_run_in_undochunk


def keep_selection(func):
    """ Get current selection, run function, return to initial selection. """
    def _wrapper_keep_selection():
        try:
            initial_selection = cmds.ls(sl=True)
            func()
        finally:
            cmds.select(initial_selection)
    return _wrapper_keep_selection
