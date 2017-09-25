# -*- coding: utf-8 -*-
#�|���S���˃X�i�b�v�������I�u�W�F�N�g�̏��őI��
#���_�ƃG�b�W���_�ň�ԋ߂���̂ɃX�i�b�v
import pymel.core as pm
import math

vtxv = []
name = pm.ls(sl=True)
vname = pm.ls((name[0] + '.vtx[*]'), v=True, fl=True)
ename = pm.ls((name[0] + '.e[*]'), v=True, fl=True)

for i in range(1,len(name)):
    mindistance = 9999999999999.0
    snappos = [0,0,0]
    temploc = pm.spaceLocator(p=(0,0,0))
    pc = pm.pointConstraint(name[i], temploc[0], o=(0,0,0), w=1)
    pm.delete(pc[0])
    jpos = pm.xform(temploc[0], q=True, ws=True, t=True)
    for vn in vname:
        vpos = pm.pointPosition(vn, w=True)
        distancetemp = math.sqrt( pow((jpos[0]-vpos[0]),2) + pow((jpos[1]-vpos[1]),2) + pow((jpos[2]-vpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vpos

    for en in ename:
        ev = pm.filterExpand(pm.polyListComponentConversion(en, tv=True), sm=31)
        v1pos = pm.pointPosition(ev[0], w=True)
        v2pos = pm.pointPosition(ev[1], w=True)
        vmpos = [(v1pos[0]+v2pos[0])/2.0, (v1pos[1]+v2pos[1])/2.0, (v1pos[2]+v2pos[2])/2.0]
        distancetemp = math.sqrt( pow((jpos[0]-vmpos[0]),2) + pow((jpos[1]-vmpos[1]),2) + pow((jpos[2]-vmpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vmpos
    chld = pm.listRelatives(name[i], c=True, typ='transform')
    if chld != None:
        for c in chld:
            pm.parent(c, w=True)
    pm.setAttr(temploc[0]+'.translateX', snappos[0])
    pm.setAttr(temploc[0]+'.translateY', snappos[1])
    pm.setAttr(temploc[0]+'.translateZ', snappos[2])
    pc = pm.pointConstraint(temploc[0], name[i], o=(0,0,0), w=1)
    pm.delete(temploc[0])
    if chld != None:
        for c in chld:
            pm.parent(c, name[i])