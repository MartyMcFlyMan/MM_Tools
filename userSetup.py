#add this to your userSetup.py in Drive:/Users/User/Documents/maya/version/prefs/scripts/

import maya.cmds as cmds
import sys

scripts_path = cmds.internalVar(usd=True)
sys.path.append(scripts_path.rpartition('scripts')[0] + 'prefs/scripts/MM_maya_tools/')

