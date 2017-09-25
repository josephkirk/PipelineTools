# -*- coding: utf-8 -*-
# --------------------------------------
# �|���S���˃X�i�b�v�������I�u�W�F�N�g�̏��őI��
# ���_�ƃG�b�W���_�ň�ԋ߂���̂ɃX�i�b�v
# ��L�v���XPointToPoly��K�p
# --------------------------------------

import pymel.core as pm
import math

vtxv = []
name = pm.ls(sl=True) #name[0]�����b�V���@name[1]�ȍ~���z����������
vname = pm.ls((name[0] + '.vtx[*]'), v=True, fl=True) #�S���_�擾
ename = pm.ls((name[0] + '.e[*]'), v=True, fl=True) #�S�G�b�W�擾

for i in range(1,len(name)):
    mindistance = 9999999999999.0 #����臒l������
    snappos = [0,0,0] #�X�i�b�v�����郏�[���h���W
    snapuv = [0,0] #�X�i�b�v�����钸�_���W
    # --- name[i]���݈ʒu�擾 ---
    temploc = pm.spaceLocator(p=(0,0,0))
    pc = pm.pointConstraint(name[i], temploc[0], o=(0,0,0), w=1)
    pm.delete(pc[0])
    jpos = pm.xform(temploc[0], q=True, ws=True, t=True)
    # --- ���_ ---
    for vn in vname:
        vpos = pm.pointPosition(vn, w=True) #���_���W�擾
        distancetemp = math.sqrt( pow((jpos[0]-vpos[0]),2) + pow((jpos[1]-vpos[1]),2) + pow((jpos[2]-vpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vpos
            # --- ���_����UV���W�擾 ---
            un = pm.filterExpand(pm.polyListComponentConversion(vn, tuv=True), sm=35)
            snapuv = pm.polyEditUV(un[0], q=True)
    # --- �G�b�W ---
    for en in ename:
        # --- �G�b�W���璸�_�擾 ---
        ev = pm.filterExpand(pm.polyListComponentConversion(en, tv=True), sm=31)
        v1pos = pm.pointPosition(ev[0], w=True) #���_���W�擾
        v2pos = pm.pointPosition(ev[1], w=True) #���_���W�擾
        vmpos = [(v1pos[0]+v2pos[0])/2.0, (v1pos[1]+v2pos[1])/2.0, (v1pos[2]+v2pos[2])/2.0] #���_���W�v�Z
        distancetemp = math.sqrt( pow((jpos[0]-vmpos[0]),2) + pow((jpos[1]-vmpos[1]),2) + pow((jpos[2]-vmpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vmpos
            # --- ���_����UV���W�擾 ---
            un = pm.filterExpand(pm.polyListComponentConversion(en, tuv=True), sm=35)
            a = pm.polyEditUV(un[0], q=True)
            if len(un) == 2: #�\��UV��3�ȏ�̏ꍇ��1�Ԗڂ�3�Ԗڂ���擾
                b = pm.polyEditUV(un[1], q=True)
            elif len(un) > 2:
                b = pm.polyEditUV(un[2], q=True)
            snapuv = [((a[0]+b[0])/2), ((a[1]+b[1])/2)]

    # --- �ړ��̑O�Ɏq�̃y�A�����g��� ---
    chld = pm.listRelatives(name[i], c=True, typ='transform')
    if chld != None:
        for c in chld:
            pm.parent(c, w=True)
            
    # --- �ʒu���킹�̂� ---
    pm.setAttr(temploc[0]+'.translateX', snappos[0])
    pm.setAttr(temploc[0]+'.translateY', snappos[1])
    pm.setAttr(temploc[0]+'.translateZ', snappos[2])
    pc = pm.pointConstraint(temploc[0], name[i], o=(0,0,0), w=1)
    pm.delete(temploc[0])
    # --- Point to Poly ---
    ptpcnst = pm.pointOnPolyConstraint(name[0], name[i], mo=False, w=1.0)
    pm.setAttr(ptpcnst[0] + '.' + name[0] + 'U0', snapuv[0])
    pm.setAttr(ptpcnst[0] + '.' + name[0] + 'V0', snapuv[1])
    
    # --- �q�̃y�A�����g��߂� ---    
    if chld != None:
        for c in chld:
            pm.parent(c, name[i])
    
    
    