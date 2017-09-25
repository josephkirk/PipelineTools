#pointConstraint ctl to loc
# -*- coding: utf-8 -*-

import pymel.core as pm

name = pm.ls(sl=True)
for n in name:
    offgpname = n.replace('_ctl','_offset_Gp')
    gpname = n.replace('_ctl','_Gp')
    pm.group(n, n=offgpname)
    pm.group(offgpname, n=gpname)
    locname = n.replace('_ctl','_loc')
    pm.pointConstraint(locname, gpname, o=(0,0,0), w=1)