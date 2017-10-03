#pointConstraint ctl to loc
# -*- coding: utf-8 -*-

import pymel.core as pm

name = pm.ls(sl=True)
for n in name:
    gpname = n + '_Gp'
    pm.group(n, n=gpname)