# -*- coding: utf-8 -*-
# --------------------------------------
# ポリゴン⇒スナップしたいオブジェクトの順で選択
# 頂点とエッジ中点で一番近いものにスナップ
# 上記プラスPointToPolyを適用
# --------------------------------------

import maya.cmds as cmds
import math

vtxv = []
name = cmds.ls(sl=True) #name[0]がメッシュ　name[1]以降が吸着させるやつら
vname = cmds.ls((name[0] + '.vtx[*]'), v=True, fl=True) #全頂点取得
ename = cmds.ls((name[0] + '.e[*]'), v=True, fl=True) #全エッジ取得

for i in range(1,len(name)):
    mindistance = 9999999999999.0 #距離閾値初期化
    snappos = [0,0,0] #スナップさせるワールド座標
    snapuv = [0,0] #スナップさせる頂点座標
    # --- name[i]現在位置取得 ---
    temploc = cmds.spaceLocator(p=(0,0,0))
    pc = cmds.pointConstraint(name[i], temploc[0], o=(0,0,0), w=1)
    cmds.delete(pc[0])
    jpos = cmds.xform(temploc[0], q=True, ws=True, t=True)
    # --- 頂点 ---
    for vn in vname:
        vpos = cmds.pointPosition(vn, w=True) #頂点座標取得
        distancetemp = math.sqrt( pow((jpos[0]-vpos[0]),2) + pow((jpos[1]-vpos[1]),2) + pow((jpos[2]-vpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vpos
            # --- 頂点からUV座標取得 ---
            un = cmds.filterExpand(cmds.polyListComponentConversion(vn, tuv=True), sm=35)
            snapuv = cmds.polyEditUV(un[0], q=True)
    # --- エッジ ---
    for en in ename:
        # --- エッジから頂点取得 ---
        ev = cmds.filterExpand(cmds.polyListComponentConversion(en, tv=True), sm=31)
        v1pos = cmds.pointPosition(ev[0], w=True) #頂点座標取得
        v2pos = cmds.pointPosition(ev[1], w=True) #頂点座標取得
        vmpos = [(v1pos[0]+v2pos[0])/2.0, (v1pos[1]+v2pos[1])/2.0, (v1pos[2]+v2pos[2])/2.0] #中点座標計算
        distancetemp = math.sqrt( pow((jpos[0]-vmpos[0]),2) + pow((jpos[1]-vmpos[1]),2) + pow((jpos[2]-vmpos[2]),2) )
        if distancetemp <= mindistance :
            mindistance = distancetemp
            snappos = vmpos
            # --- 頂点からUV座標取得 ---
            un = cmds.filterExpand(cmds.polyListComponentConversion(en, tuv=True), sm=35)
            a = cmds.polyEditUV(un[0], q=True)
            if len(un) == 2: #構成UVが3つ以上の場合は1番目と3番目から取得
                b = cmds.polyEditUV(un[1], q=True)
            elif len(un) > 2:
                b = cmds.polyEditUV(un[2], q=True)
            snapuv = [((a[0]+b[0])/2), ((a[1]+b[1])/2)]

    # --- 移動の前に子のペアレントを解除 ---
    chld = cmds.listRelatives(name[i], c=True, typ='transform')
    if chld != None:
        for c in chld:
            cmds.parent(c, w=True)
            
    # --- 位置あわせのみ ---
    cmds.setAttr(temploc[0]+'.translateX', snappos[0])
    cmds.setAttr(temploc[0]+'.translateY', snappos[1])
    cmds.setAttr(temploc[0]+'.translateZ', snappos[2])
    pc = cmds.pointConstraint(temploc[0], name[i], o=(0,0,0), w=1)
    cmds.delete(temploc[0])
    # --- Point to Poly ---
    ptpcnst = cmds.pointOnPolyConstraint(name[0], name[i], mo=False, w=1.0)
    cmds.setAttr(ptpcnst[0] + '.' + name[0] + 'U0', snapuv[0])
    cmds.setAttr(ptpcnst[0] + '.' + name[0] + 'V0', snapuv[1])
    
    # --- 子のペアレントを戻す ---    
    if chld != None:
        for c in chld:
            cmds.parent(c, name[i])
    
    
    