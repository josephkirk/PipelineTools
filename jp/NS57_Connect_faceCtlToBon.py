# -*- coding: utf-8 -*-

# NS57_Connect_mouthctlToBon

import maya.cmds as cmds


lC = 'lipCenter'
nT = 'noseTop'

ebL = 'eyebrowLeft'
eL = 'eyeLeft'
eSL = 'eyeSubLeft'
nL = 'noseLeft'
cL = 'cheekLeft'
lL = 'lipLeft'

ebR = 'eyebrowRight'
eR = 'eyeRight'
eSR = 'eyeSubRight'
nR = 'noseRight'
cR = 'cheekRight'
lR = 'lipRight'

#Center translate

cmds.connectAttr(lC+'A_ctl.translate', lC+'A_bon.translate', f=True)
cmds.connectAttr(lC+'B_ctl.translate', lC+'B_bon.translate', f=True)
cmds.connectAttr(nT+'_ctl.translate', nT+'_bon.translate', f=True)

#Left translate

cmds.connectAttr(ebL+'A_ctl.translate', ebL+'A_bon.translate', f=True)
cmds.connectAttr(ebL+'B_ctl.translate', ebL+'B_bon.translate', f=True)
cmds.connectAttr(ebL+'C_ctl.translate', ebL+'C_bon.translate', f=True)

cmds.connectAttr(eL+'A_ctl.translate', eL+'A_bon.translate', f=True)
cmds.connectAttr(eL+'B_ctl.translate', eL+'B_bon.translate', f=True)
cmds.connectAttr(eL+'C_ctl.translate', eL+'C_bon.translate', f=True)
cmds.connectAttr(eL+'D_ctl.translate', eL+'D_bon.translate', f=True)

cmds.connectAttr(eSL+'A_ctl.translate', eSL+'A_bon.translate', f=True)
cmds.connectAttr(eSL+'B_ctl.translate', eSL+'B_bon.translate', f=True)
cmds.connectAttr(eSL+'C_ctl.translate', eSL+'C_bon.translate', f=True)
cmds.connectAttr(eSL+'D_ctl.translate', eSL+'D_bon.translate', f=True)

cmds.connectAttr(nL+'A_ctl.translate', nL+'A_bon.translate', f=True)

cmds.connectAttr(cL+'A_ctl.translate', cL+'A_bon.translate', f=True)
cmds.connectAttr(cL+'B_ctl.translate', cL+'B_bon.translate', f=True)
cmds.connectAttr(cL+'C_ctl.translate', cL+'C_bon.translate', f=True)

cmds.connectAttr(lL+'A_ctl.translate', lL+'A_bon.translate', f=True)
cmds.connectAttr(lL+'B_ctl.translate', lL+'B_bon.translate', f=True)
cmds.connectAttr(lL+'C_ctl.translate', lL+'C_bon.translate', f=True)

#Right translate

cmds.connectAttr(ebR+'A_ctl.translate', ebR+'A_bon.translate', f=True)
cmds.connectAttr(ebR+'B_ctl.translate', ebR+'B_bon.translate', f=True)
cmds.connectAttr(ebR+'C_ctl.translate', ebR+'C_bon.translate', f=True)

cmds.connectAttr(eR+'A_ctl.translate', eR+'A_bon.translate', f=True)
cmds.connectAttr(eR+'B_ctl.translate', eR+'B_bon.translate', f=True)
cmds.connectAttr(eR+'C_ctl.translate', eR+'C_bon.translate', f=True)
cmds.connectAttr(eR+'D_ctl.translate', eR+'D_bon.translate', f=True)

cmds.connectAttr(eSR+'A_ctl.translate', eSR+'A_bon.translate', f=True)
cmds.connectAttr(eSR+'B_ctl.translate', eSR+'B_bon.translate', f=True)
cmds.connectAttr(eSR+'C_ctl.translate', eSR+'C_bon.translate', f=True)
cmds.connectAttr(eSR+'D_ctl.translate', eSR+'D_bon.translate', f=True)

cmds.connectAttr(nR+'A_ctl.translate', nR+'A_bon.translate', f=True)

cmds.connectAttr(cR+'A_ctl.translate', cR+'A_bon.translate', f=True)
cmds.connectAttr(cR+'B_ctl.translate', cR+'B_bon.translate', f=True)
cmds.connectAttr(cR+'C_ctl.translate', cR+'C_bon.translate', f=True)

cmds.connectAttr(lR+'A_ctl.translate', lR+'A_bon.translate', f=True)
cmds.connectAttr(lR+'B_ctl.translate', lR+'B_bon.translate', f=True)
cmds.connectAttr(lR+'C_ctl.translate', lR+'C_bon.translate', f=True)

#Center rotate

cmds.connectAttr(lC+'A_ctl.rotate', lC+'A_bon.rotate', f=True)
cmds.connectAttr(lC+'B_ctl.rotate', lC+'B_bon.rotate', f=True)
cmds.connectAttr(nT+'_ctl.rotate', nT+'_bon.rotate', f=True)

#Left rotate

cmds.connectAttr(ebL+'A_ctl.rotate', ebL+'A_bon.rotate', f=True)
cmds.connectAttr(ebL+'B_ctl.rotate', ebL+'B_bon.rotate', f=True)
cmds.connectAttr(ebL+'C_ctl.rotate', ebL+'C_bon.rotate', f=True)

cmds.connectAttr(eL+'A_ctl.rotate', eL+'A_bon.rotate', f=True)
cmds.connectAttr(eL+'B_ctl.rotate', eL+'B_bon.rotate', f=True)
cmds.connectAttr(eL+'C_ctl.rotate', eL+'C_bon.rotate', f=True)
cmds.connectAttr(eL+'D_ctl.rotate', eL+'D_bon.rotate', f=True)

cmds.connectAttr(eSL+'A_ctl.rotate', eSL+'A_bon.rotate', f=True)
cmds.connectAttr(eSL+'B_ctl.rotate', eSL+'B_bon.rotate', f=True)
cmds.connectAttr(eSL+'C_ctl.rotate', eSL+'C_bon.rotate', f=True)
cmds.connectAttr(eSL+'D_ctl.rotate', eSL+'D_bon.rotate', f=True)

cmds.connectAttr(nL+'A_ctl.rotate', nL+'A_bon.rotate', f=True)

cmds.connectAttr(cL+'A_ctl.rotate', cL+'A_bon.rotate', f=True)
cmds.connectAttr(cL+'B_ctl.rotate', cL+'B_bon.rotate', f=True)
cmds.connectAttr(cL+'C_ctl.rotate', cL+'C_bon.rotate', f=True)

cmds.connectAttr(lL+'A_ctl.rotate', lL+'A_bon.rotate', f=True)
cmds.connectAttr(lL+'B_ctl.rotate', lL+'B_bon.rotate', f=True)
cmds.connectAttr(lL+'C_ctl.rotate', lL+'C_bon.rotate', f=True)

#Right rotate

cmds.connectAttr(ebR+'A_ctl.rotate', ebR+'A_bon.rotate', f=True)
cmds.connectAttr(ebR+'B_ctl.rotate', ebR+'B_bon.rotate', f=True)
cmds.connectAttr(ebR+'C_ctl.rotate', ebR+'C_bon.rotate', f=True)

cmds.connectAttr(eR+'A_ctl.rotate', eR+'A_bon.rotate', f=True)
cmds.connectAttr(eR+'B_ctl.rotate', eR+'B_bon.rotate', f=True)
cmds.connectAttr(eR+'C_ctl.rotate', eR+'C_bon.rotate', f=True)
cmds.connectAttr(eR+'D_ctl.rotate', eR+'D_bon.rotate', f=True)

cmds.connectAttr(eSR+'A_ctl.rotate', eSR+'A_bon.rotate', f=True)
cmds.connectAttr(eSR+'B_ctl.rotate', eSR+'B_bon.rotate', f=True)
cmds.connectAttr(eSR+'C_ctl.rotate', eSR+'C_bon.rotate', f=True)
cmds.connectAttr(eSR+'D_ctl.rotate', eSR+'D_bon.rotate', f=True)

cmds.connectAttr(nR+'A_ctl.rotate', nR+'A_bon.rotate', f=True)

cmds.connectAttr(cR+'A_ctl.rotate', cR+'A_bon.rotate', f=True)
cmds.connectAttr(cR+'B_ctl.rotate', cR+'B_bon.rotate', f=True)
cmds.connectAttr(cR+'C_ctl.rotate', cR+'C_bon.rotate', f=True)

cmds.connectAttr(lR+'A_ctl.rotate', lR+'A_bon.rotate', f=True)
cmds.connectAttr(lR+'B_ctl.rotate', lR+'B_bon.rotate', f=True)
cmds.connectAttr(lR+'C_ctl.rotate', lR+'C_bon.rotate', f=True)

#Center scale

cmds.connectAttr(lC+'A_ctl.scale', lC+'A_bon.scale', f=True)
cmds.connectAttr(lC+'B_ctl.scale', lC+'B_bon.scale', f=True)
cmds.connectAttr(nT+'_ctl.scale', nT+'_bon.scale', f=True)

#Left scale

cmds.connectAttr(ebL+'A_ctl.scale', ebL+'A_bon.scale', f=True)
cmds.connectAttr(ebL+'B_ctl.scale', ebL+'B_bon.scale', f=True)
cmds.connectAttr(ebL+'C_ctl.scale', ebL+'C_bon.scale', f=True)

cmds.connectAttr(eL+'A_ctl.scale', eL+'A_bon.scale', f=True)
cmds.connectAttr(eL+'B_ctl.scale', eL+'B_bon.scale', f=True)
cmds.connectAttr(eL+'C_ctl.scale', eL+'C_bon.scale', f=True)
cmds.connectAttr(eL+'D_ctl.scale', eL+'D_bon.scale', f=True)

cmds.connectAttr(eSL+'A_ctl.scale', eSL+'A_bon.scale', f=True)
cmds.connectAttr(eSL+'B_ctl.scale', eSL+'B_bon.scale', f=True)
cmds.connectAttr(eSL+'C_ctl.scale', eSL+'C_bon.scale', f=True)
cmds.connectAttr(eSL+'D_ctl.scale', eSL+'D_bon.scale', f=True)

cmds.connectAttr(nL+'A_ctl.scale', nL+'A_bon.scale', f=True)

cmds.connectAttr(cL+'A_ctl.scale', cL+'A_bon.scale', f=True)
cmds.connectAttr(cL+'B_ctl.scale', cL+'B_bon.scale', f=True)
cmds.connectAttr(cL+'C_ctl.scale', cL+'C_bon.scale', f=True)

cmds.connectAttr(lL+'A_ctl.scale', lL+'A_bon.scale', f=True)
cmds.connectAttr(lL+'B_ctl.scale', lL+'B_bon.scale', f=True)
cmds.connectAttr(lL+'C_ctl.scale', lL+'C_bon.scale', f=True)

#Right scale

cmds.connectAttr(ebR+'A_ctl.scale', ebR+'A_bon.scale', f=True)
cmds.connectAttr(ebR+'B_ctl.scale', ebR+'B_bon.scale', f=True)
cmds.connectAttr(ebR+'C_ctl.scale', ebR+'C_bon.scale', f=True)

cmds.connectAttr(eR+'A_ctl.scale', eR+'A_bon.scale', f=True)
cmds.connectAttr(eR+'B_ctl.scale', eR+'B_bon.scale', f=True)
cmds.connectAttr(eR+'C_ctl.scale', eR+'C_bon.scale', f=True)
cmds.connectAttr(eR+'D_ctl.scale', eR+'D_bon.scale', f=True)

cmds.connectAttr(eSR+'A_ctl.scale', eSR+'A_bon.scale', f=True)
cmds.connectAttr(eSR+'B_ctl.scale', eSR+'B_bon.scale', f=True)
cmds.connectAttr(eSR+'C_ctl.scale', eSR+'C_bon.scale', f=True)
cmds.connectAttr(eSR+'D_ctl.scale', eSR+'D_bon.scale', f=True)

cmds.connectAttr(nR+'A_ctl.scale', nR+'A_bon.scale', f=True)

cmds.connectAttr(cR+'A_ctl.scale', cR+'A_bon.scale', f=True)
cmds.connectAttr(cR+'B_ctl.scale', cR+'B_bon.scale', f=True)
cmds.connectAttr(cR+'C_ctl.scale', cR+'C_bon.scale', f=True)

cmds.connectAttr(lR+'A_ctl.scale', lR+'A_bon.scale', f=True)
cmds.connectAttr(lR+'B_ctl.scale', lR+'B_bon.scale', f=True)
cmds.connectAttr(lR+'C_ctl.scale', lR+'C_bon.scale', f=True)








