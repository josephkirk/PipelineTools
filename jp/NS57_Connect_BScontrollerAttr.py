# -*- coding: utf-8 -*-

# NS57_Connect_BScontrollerAttr

import maya.cmds as cmds

faceBS = 'FaceBaseBS'
browCnt = 'brow_cnt'
eyeCnt = 'eye_cnt'
mouthCnt = 'mouth_cnt'

cmds.connectAttr(browCnt+'.eyebrow_smile_L', faceBS+'.eyebrow_smile_L', f=True)
cmds.connectAttr(browCnt+'.eyebrow_smile_R', faceBS+'.eyebrow_smile_R', f=True)
cmds.connectAttr(browCnt+'.eyebrow_sad_L', faceBS+'.eyebrow_sad_L', f=True)
cmds.connectAttr(browCnt+'.eyebrow_sad_R', faceBS+'.eyebrow_sad_R', f=True)
cmds.connectAttr(browCnt+'.eyebrow_anger_L', faceBS+'.eyebrow_anger_L', f=True)
cmds.connectAttr(browCnt+'.eyebrow_anger_R', faceBS+'.eyebrow_anger_R', f=True)

cmds.connectAttr(eyeCnt+'.eye_close_L', faceBS+'.eye_close_L', f=True)
cmds.connectAttr(eyeCnt+'.eye_close_R', faceBS+'.eye_close_R', f=True)
cmds.connectAttr(eyeCnt+'.eye_smile_L', faceBS+'.eye_smile_L', f=True)
cmds.connectAttr(eyeCnt+'.eye_smile_R', faceBS+'.eye_smile_R', f=True)
cmds.connectAttr(eyeCnt+'.eye_anger_L', faceBS+'.eye_anger_L', f=True)
cmds.connectAttr(eyeCnt+'.eye_anger_R', faceBS+'.eye_anger_R', f=True)
cmds.connectAttr(eyeCnt+'.eye_open_L', faceBS+'.eye_open_L', f=True)
cmds.connectAttr(eyeCnt+'.eye_open_R', faceBS+'.eye_open_R', f=True)

cmds.connectAttr(mouthCnt+'.mouth_A', faceBS+'.mouth_A', f=True)
cmds.connectAttr(mouthCnt+'.mouth_I', faceBS+'.mouth_I', f=True)
cmds.connectAttr(mouthCnt+'.mouth_U', faceBS+'.mouth_U', f=True)
cmds.connectAttr(mouthCnt+'.mouth_E', faceBS+'.mouth_E', f=True)
cmds.connectAttr(mouthCnt+'.mouth_O', faceBS+'.mouth_O', f=True)
cmds.connectAttr(mouthCnt+'.mouth_shout', faceBS+'.mouth_shout', f=True)
cmds.connectAttr(mouthCnt+'.mouth_open', faceBS+'.mouth_open', f=True)
cmds.connectAttr(mouthCnt+'.mouth_smileClose', faceBS+'.mouth_smileClose', f=True)
cmds.connectAttr(mouthCnt+'.mouth_angerClose', faceBS+'.mouth_angerClose', f=True)