# -*- coding: utf-8 -*-
#ポリゴン⇒スナップしたいオブジェクトの順で選択
#頂点とエッジ中点で一番近いものにスナップ
import maya.cmds as cmds
import math

vtxv = []
name = cmds.ls(sl=True)
vname = cmds.ls((name[0] + '.vtx[*]'), v=True, fl=True)
ename = cmds.ls((name[0] + '.e[*]'), v=True, fl=True)

for i in range(1,len(name)):
    mindistance = 9999999999999.0
    snappos = [0,0,0]
    temploc = cmds.spaceLocator(p=(0,0,0))
    pc = cmds.pointConstraint(name[i], temploc[0], o=(0,0,0), w=1)
    cmds.delete(pc[0])
    jpos = cmds.xform(temploc[0], q=True, ws=True, t=True)
    for vn in vname:
        vpos = cmds.pointPosition(vn, w=True)
        distancetemp = math.sqrt( pow((jpos[0]-vpos[0]),2) + pow((jpos[1]-vpos[1]),2) + pow((jpos[2]-vpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vpos

    for en in ename:
        ev = cmds.filterExpand(cmds.polyListComponentConversion(en, tv=True), sm=31)
        v1pos = cmds.pointPosition(ev[0], w=True)
        v2pos = cmds.pointPosition(ev[1], w=True)
        vmpos = [(v1pos[0]+v2pos[0])/2.0, (v1pos[1]+v2pos[1])/2.0, (v1pos[2]+v2pos[2])/2.0]
        distancetemp = math.sqrt( pow((jpos[0]-vmpos[0]),2) + pow((jpos[1]-vmpos[1]),2) + pow((jpos[2]-vmpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vmpos
    chld = cmds.listRelatives(name[i], c=True, typ='transform')
    if chld != None:
        for c in chld:
            cmds.parent(c, w=True)
    cmds.setAttr(temploc[0]+'.translateX', snappos[0])
    cmds.setAttr(temploc[0]+'.translateY', snappos[1])
    cmds.setAttr(temploc[0]+'.translateZ', snappos[2])
    pc = cmds.pointConstraint(temploc[0], name[i], o=(0,0,0), w=1)
    cmds.delete(temploc[0])
    if chld != None:
        for c in chld:
            cmds.parent(c, name[i])