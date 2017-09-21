#pointConstraint ctl to loc
# -*- coding: utf-8 -*-

import maya.cmds as cmds

name = cmds.ls(sl=True)
for n in name:
    offgpname = n.replace('_ctl','_offset_Gp')
    gpname = n.replace('_ctl','_Gp')
    cmds.group(n, n=offgpname)
    cmds.group(offgpname, n=gpname)
    locname = n.replace('_ctl','_loc')
    cmds.pointConstraint(locname, gpname, o=(0,0,0), w=1)