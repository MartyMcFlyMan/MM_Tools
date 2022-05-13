import maya.cmds as cmds


def combine_nurbs(selection):
    """Select Nurbs to make into a single Nurb."""
    for obj in selection:
        cmds.makeIdentity(obj, a=True, t=True, r=True, s=True)
        cmds.delete(obj, ch=True)
    parent_name = selection[-1]
    selection.pop()  # remove parent_name from list
    # now we have a list of the nurbs we need to parent under the parent_name
    for obj in selection:
        shape_name = cmds.listRelatives(obj, ad=True, shapes=True)[0]
        cmds.parent(shape_name, parent_name, s=True, r=True)
        cmds.delete(obj)


def colour_override(selection, color):
    colors = {
        "red": [1, 0, 0],
        "green": [0, 1, 0],
        "blue": [0, 0, 1],
        "pink": [1, 0, 1],
        "pale_blue": [0, 1, 1],
        "pale_green": [0.5, 1, 0],
        "purple": [0.5, 0, 1],
        "yellow": [1, 1, 0],
        "orange": [1, 0.5, 0],
        "white": [1, 1, 1],
        "black": [0, 0, 0]
    }
    red, green, blue = colors[color]
    for obj in selection:
        cmds.setAttr('{0}.overrideEnabled'.format(obj), 1)
        cmds.setAttr('{0}.overrideRGBColors'.format(obj), 1)
        cmds.setAttr('{0}.overrideColorRGB'.format(obj), red, green, blue)

