# -*- coding: utf-8 -*-

# NS57_Connect_mouthCntToBon

import pymel.core as pm

jaw = 'jaw'
teeU = 'teethUpper'
teeL = 'teethLower'
tonR = 'tongueRight'
tonC = 'tongueCenter'
tonL = 'tongueLeft'
tonM = 'tongueCenter'

pm.connectAttr(jaw+'_cnt.translate', jaw+'Root_bon.translate', f=True)
pm.connectAttr(teeU+'_cnt.translate', teeU+'_bon.translate', f=True)
pm.connectAttr(teeL+'_cnt.translate', teeL+'_bon.translate', f=True)

pm.connectAttr(tonR+'A_cnt.translate', tonR+'A_bon.translate', f=True)
pm.connectAttr(tonC+'A_cnt.translate', tonC+'A_bon.translate', f=True)
pm.connectAttr(tonL+'A_cnt.translate', tonL+'A_bon.translate', f=True)
pm.connectAttr(tonM+'ARoot_cnt.translate', tonM+'ARoot_bon.translate', f=True)

pm.connectAttr(tonR+'B_cnt.translate', tonR+'B_bon.translate', f=True)
pm.connectAttr(tonC+'B_cnt.translate', tonC+'B_bon.translate', f=True)
pm.connectAttr(tonL+'B_cnt.translate', tonL+'B_bon.translate', f=True)
pm.connectAttr(tonM+'BRoot_cnt.translate', tonM+'BRoot_bon.translate', f=True)

pm.connectAttr(tonR+'C_cnt.translate', tonR+'C_bon.translate', f=True)
pm.connectAttr(tonC+'C_cnt.translate', tonC+'C_bon.translate', f=True)
pm.connectAttr(tonL+'C_cnt.translate', tonL+'C_bon.translate', f=True)
pm.connectAttr(tonM+'CRoot_cnt.translate', tonM+'CRoot_bon.translate', f=True)

pm.connectAttr(tonR+'D_cnt.translate', tonR+'D_bon.translate', f=True)
pm.connectAttr(tonC+'D_cnt.translate', tonC+'D_bon.translate', f=True)
pm.connectAttr(tonL+'D_cnt.translate', tonL+'D_bon.translate', f=True)
pm.connectAttr(tonM+'DRoot_cnt.translate', tonM+'DRoot_bon.translate', f=True)


pm.connectAttr(jaw+'_cnt.rotate', jaw+'Root_bon.rotate', f=True)
pm.connectAttr(teeU+'_cnt.rotate', teeU+'_bon.rotate', f=True)
pm.connectAttr(teeL+'_cnt.rotate', teeL+'_bon.rotate', f=True)

pm.connectAttr(tonR+'A_cnt.rotate', tonR+'A_bon.rotate', f=True)
pm.connectAttr(tonC+'A_cnt.rotate', tonC+'A_bon.rotate', f=True)
pm.connectAttr(tonL+'A_cnt.rotate', tonL+'A_bon.rotate', f=True)
pm.connectAttr(tonM+'ARoot_cnt.rotate', tonM+'ARoot_bon.rotate', f=True)

pm.connectAttr(tonR+'B_cnt.rotate', tonR+'B_bon.rotate', f=True)
pm.connectAttr(tonC+'B_cnt.rotate', tonC+'B_bon.rotate', f=True)
pm.connectAttr(tonL+'B_cnt.rotate', tonL+'B_bon.rotate', f=True)
pm.connectAttr(tonM+'BRoot_cnt.rotate', tonM+'BRoot_bon.rotate', f=True)

pm.connectAttr(tonR+'C_cnt.rotate', tonR+'C_bon.rotate', f=True)
pm.connectAttr(tonC+'C_cnt.rotate', tonC+'C_bon.rotate', f=True)
pm.connectAttr(tonL+'C_cnt.rotate', tonL+'C_bon.rotate', f=True)
pm.connectAttr(tonM+'CRoot_cnt.rotate', tonM+'CRoot_bon.rotate', f=True)

pm.connectAttr(tonR+'D_cnt.rotate', tonR+'D_bon.rotate', f=True)
pm.connectAttr(tonC+'D_cnt.rotate', tonC+'D_bon.rotate', f=True)
pm.connectAttr(tonL+'D_cnt.rotate', tonL+'D_bon.rotate', f=True)
pm.connectAttr(tonM+'DRoot_cnt.rotate', tonM+'DRoot_bon.rotate', f=True)


pm.connectAttr(jaw+'_cnt.scale', jaw+'Root_bon.scale', f=True)
pm.connectAttr(teeU+'_cnt.scale', teeU+'_bon.scale', f=True)
pm.connectAttr(teeL+'_cnt.scale', teeL+'_bon.scale', f=True)

pm.connectAttr(tonR+'A_cnt.scale', tonR+'A_bon.scale', f=True)
pm.connectAttr(tonC+'A_cnt.scale', tonC+'A_bon.scale', f=True)
pm.connectAttr(tonL+'A_cnt.scale', tonL+'A_bon.scale', f=True)
pm.connectAttr(tonM+'ARoot_cnt.scale', tonM+'ARoot_bon.scale', f=True)

pm.connectAttr(tonR+'B_cnt.scale', tonR+'B_bon.scale', f=True)
pm.connectAttr(tonC+'B_cnt.scale', tonC+'B_bon.scale', f=True)
pm.connectAttr(tonL+'B_cnt.scale', tonL+'B_bon.scale', f=True)
pm.connectAttr(tonM+'BRoot_cnt.scale', tonM+'BRoot_bon.scale', f=True)

pm.connectAttr(tonR+'C_cnt.scale', tonR+'C_bon.scale', f=True)
pm.connectAttr(tonC+'C_cnt.scale', tonC+'C_bon.scale', f=True)
pm.connectAttr(tonL+'C_cnt.scale', tonL+'C_bon.scale', f=True)
pm.connectAttr(tonM+'CRoot_cnt.scale', tonM+'CRoot_bon.scale', f=True)

pm.connectAttr(tonR+'D_cnt.scale', tonR+'D_bon.scale', f=True)
pm.connectAttr(tonC+'D_cnt.scale', tonC+'D_bon.scale', f=True)
pm.connectAttr(tonL+'D_cnt.scale', tonL+'D_bon.scale', f=True)
pm.connectAttr(tonM+'DRoot_cnt.scale', tonM+'DRoot_bon.scale', f=True)




