# -*- coding: utf-8 -*-

# NS57_Connect_BScontrollerAttr

import pymel.core as pm

faceBS = 'FaceBaseBS'
browCnt = 'brow_ctl'
eyeCnt = 'eye_ctl'
mouthCnt = 'mouth_ctl'

pm.connectAttr(browCnt+'.eyebrow_smile_L', faceBS+'.eyebrow_smile_L', f=True)
pm.connectAttr(browCnt+'.eyebrow_smile_R', faceBS+'.eyebrow_smile_R', f=True)
pm.connectAttr(browCnt+'.eyebrow_sad_L', faceBS+'.eyebrow_sad_L', f=True)
pm.connectAttr(browCnt+'.eyebrow_sad_R', faceBS+'.eyebrow_sad_R', f=True)
pm.connectAttr(browCnt+'.eyebrow_anger_L', faceBS+'.eyebrow_anger_L', f=True)
pm.connectAttr(browCnt+'.eyebrow_anger_R', faceBS+'.eyebrow_anger_R', f=True)

pm.connectAttr(eyeCnt+'.eye_close_L', faceBS+'.eye_close_L', f=True)
pm.connectAttr(eyeCnt+'.eye_close_R', faceBS+'.eye_close_R', f=True)
pm.connectAttr(eyeCnt+'.eye_smile_L', faceBS+'.eye_smile_L', f=True)
pm.connectAttr(eyeCnt+'.eye_smile_R', faceBS+'.eye_smile_R', f=True)
pm.connectAttr(eyeCnt+'.eye_anger_L', faceBS+'.eye_anger_L', f=True)
pm.connectAttr(eyeCnt+'.eye_anger_R', faceBS+'.eye_anger_R', f=True)
pm.connectAttr(eyeCnt+'.eye_open_L', faceBS+'.eye_open_L', f=True)
pm.connectAttr(eyeCnt+'.eye_open_R', faceBS+'.eye_open_R', f=True)

pm.connectAttr(mouthCnt+'.mouth_A', faceBS+'.mouth_A', f=True)
pm.connectAttr(mouthCnt+'.mouth_I', faceBS+'.mouth_I', f=True)
pm.connectAttr(mouthCnt+'.mouth_U', faceBS+'.mouth_U', f=True)
pm.connectAttr(mouthCnt+'.mouth_E', faceBS+'.mouth_E', f=True)
pm.connectAttr(mouthCnt+'.mouth_O', faceBS+'.mouth_O', f=True)
pm.connectAttr(mouthCnt+'.mouth_shout', faceBS+'.mouth_shout', f=True)
pm.connectAttr(mouthCnt+'.mouth_open', faceBS+'.mouth_open', f=True)
pm.connectAttr(mouthCnt+'.mouth_smileClose', faceBS+'.mouth_smileClose', f=True)
pm.connectAttr(mouthCnt+'.mouth_angerClose', faceBS+'.mouth_angerClose', f=True)