# -*- coding: utf-8 -*-
# --------------------------------------
# 選択したジョイントの位置にロケータとコントローラを作成
# --------------------------------------

import maya.cmds as cmds

name = cmds.ls(sl=True)
for n in name:
    locname = n.replace('_bon','_loc')
    loc = cmds.spaceLocator(p=(0,0,0), n=locname)
    pc = cmds.pointConstraint(n, loc, o=(0,0,0), w=1)
    cmds.delete(pc[0])
for n in name:
    ctlname = n.replace('_bon','_ctl')
    sph = cmds.sphere(p=(0,0,0), ax=(0,1,0), ssw=0, esw=360, r=0.35, d=3, ut=False, tol=0.01, s=8, nsp=4, ch=False, n=ctlname)
    pc = cmds.pointConstraint(n, sph, o=(0,0,0), w=1)
    cmds.delete(pc[0])