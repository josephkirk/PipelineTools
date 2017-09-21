#pointConstraint ctl to loc
# -*- coding: utf-8 -*-

import maya.cmds as cmds

name = cmds.ls(sl=True)
for n in name:
    gpname = n + '_Gp'
    cmds.group(n, n=gpname)