import pymel.core as pm
from PipelineTools.utilities import *
#reload(*)
@do_function_on('single')
def constraint_ctrl_to_loc(n):
    offgpname = ob.replace('_ctl','_offset_Gp')
    gpname = ob.replace('_ctl','_Gp')
    pm.group(n, n=offgpname)
    pm.group(offgpname, n=gpname)
    locname = ob.replace('_ctl','_loc')
    pm.pointConstraint(locname, gpname, o=(0,0,0), w=1)
@timeit
@do_function_on('last')
def snap_to_near_vertex_midedge(ob_list,target):
    target_pos_list = [v.getPosition(space='world') for v in target.vtx]
    midedge_pos_list = [(e.getPoint(0, space='world')+e.getPoint(1, space='world'))/2 for e in target.e]
    print midedge_pos_list
    target_pos_list.extend(midedge_pos_list)
    #def get_closest_vert():
    for ob in ob_list:
        ob_pos = ob.getTranslation(space='world')
        distance = [(ob_pos.distanceTo(target_pos), target_pos) for target_pos in target_pos_list]
        distance.sort(key=lambda x:x[0])
        #print ob,distance[0]
        ob.setTranslation(distance[0][1], space='world')
    #get_closest_vert()
    #return distance_list

@do_function_on('single')
def group_loc(ob):
    gpname = n + '_Gp'
    pm.group(n, n=gpname)

@do_function_on('single')
def make_loc_and_ctl_from_bon(ob):
    locname = ob.replace('_bon','_loc')
    loc = pm.spaceLocator(p=(0,0,0), n=locname)
    pc = pm.pointConstraint(n, loc, o=(0,0,0), w=1)
    pm.delete(pc[0])
    ctlname = ob.replace('_bon','_ctl')
    sph = pm.sphere(p=(0,0,0), ax=(0,1,0), ssw=0, esw=360, r=0.35, d=3, ut=False, tol=0.01, s=8, nsp=4, ch=False, n=ctlname)
    pc = pm.pointConstraint(n, sph, o=(0,0,0), w=1)
    pm.delete(pc[0])

def connect_Bs_control():
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
    pm.connectAttr(mouthCnt+'.mouth_smileclose', faceBS+'.mouth_smileclose', f=True)
    pm.connectAttr(mouthCnt+'.mouth_angerclose', faceBS+'.mouth_angerclose', f=True)

def connect_face_ctl():
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
    for attr in ['translate', 'rotate', 'scale']:
        #Center
        pm.connectAttr(lC+'A_ctl.%s'%attr, lC+'A_bon.%s'%attr, f=True)
        pm.connectAttr(lC+'B_ctl.%s'%attr, lC+'B_bon.%s'%attr, f=True)
        pm.connectAttr(nT+'_ctl.%s'%attr, nT+'_bon.%s'%attr, f=True)
        #Left
        pm.connectAttr(ebL+'A_ctl.%s'%attr, ebL+'A_bon.%s'%attr, f=True)
        pm.connectAttr(ebL+'B_ctl.%s'%attr, ebL+'B_bon.%s'%attr, f=True)
        pm.connectAttr(ebL+'C_ctl.%s'%attr, ebL+'C_bon.%s'%attr, f=True)
        pm.connectAttr(eL+'A_ctl.%s'%attr, eL+'A_bon.%s'%attr, f=True)
        pm.connectAttr(eL+'B_ctl.%s'%attr, eL+'B_bon.%s'%attr, f=True)
        pm.connectAttr(eL+'C_ctl.%s'%attr, eL+'C_bon.%s'%attr, f=True)
        pm.connectAttr(eL+'D_ctl.%s'%attr, eL+'D_bon.%s'%attr, f=True)
        pm.connectAttr(eSL+'A_ctl.%s'%attr, eSL+'A_bon.%s'%attr, f=True)
        pm.connectAttr(eSL+'B_ctl.%s'%attr, eSL+'B_bon.%s'%attr, f=True)
        pm.connectAttr(eSL+'C_ctl.%s'%attr, eSL+'C_bon.%s'%attr, f=True)
        pm.connectAttr(eSL+'D_ctl.%s'%attr, eSL+'D_bon.%s'%attr, f=True)
        pm.connectAttr(nL+'A_ctl.%s'%attr, nL+'A_bon.%s'%attr, f=True)
        pm.connectAttr(cL+'A_ctl.%s'%attr, cL+'A_bon.%s'%attr, f=True)
        pm.connectAttr(cL+'B_ctl.%s'%attr, cL+'B_bon.%s'%attr, f=True)
        pm.connectAttr(cL+'C_ctl.%s'%attr, cL+'C_bon.%s'%attr, f=True)
        pm.connectAttr(lL+'A_ctl.%s'%attr, lL+'A_bon.%s'%attr, f=True)
        pm.connectAttr(lL+'B_ctl.%s'%attr, lL+'B_bon.%s'%attr, f=True)
        pm.connectAttr(lL+'C_ctl.%s'%attr, lL+'C_bon.%s'%attr, f=True)
        #Right
        pm.connectAttr(ebR+'A_ctl.%s'%attr, ebR+'A_bon.%s'%attr, f=True)
        pm.connectAttr(ebR+'B_ctl.%s'%attr, ebR+'B_bon.%s'%attr, f=True)
        pm.connectAttr(ebR+'C_ctl.%s'%attr, ebR+'C_bon.%s'%attr, f=True)
        pm.connectAttr(eR+'A_ctl.%s'%attr, eR+'A_bon.%s'%attr, f=True)
        pm.connectAttr(eR+'B_ctl.%s'%attr, eR+'B_bon.%s'%attr, f=True)
        pm.connectAttr(eR+'C_ctl.%s'%attr, eR+'C_bon.%s'%attr, f=True)
        pm.connectAttr(eR+'D_ctl.%s'%attr, eR+'D_bon.%s'%attr, f=True)
        pm.connectAttr(eSR+'A_ctl.%s'%attr, eSR+'A_bon.%s'%attr, f=True)
        pm.connectAttr(eSR+'B_ctl.%s'%attr, eSR+'B_bon.%s'%attr, f=True)
        pm.connectAttr(eSR+'C_ctl.%s'%attr, eSR+'C_bon.%s'%attr, f=True)
        pm.connectAttr(eSR+'D_ctl.%s'%attr, eSR+'D_bon.%s'%attr, f=True)
        pm.connectAttr(nR+'A_ctl.%s'%attr, nR+'A_bon.%s'%attr, f=True)
        pm.connectAttr(cR+'A_ctl.%s'%attr, cR+'A_bon.%s'%attr, f=True)
        pm.connectAttr(cR+'B_ctl.%s'%attr, cR+'B_bon.%s'%attr, f=True)
        pm.connectAttr(cR+'C_ctl.%s'%attr, cR+'C_bon.%s'%attr, f=True)
        pm.connectAttr(lR+'A_ctl.%s'%attr, lR+'A_bon.%s'%attr, f=True)
        pm.connectAttr(lR+'B_ctl.%s'%attr, lR+'B_bon.%s'%attr, f=True)
        pm.connectAttr(lR+'C_ctl.%s'%attr, lR+'C_bon.%s'%attr, f=True)

def connect_mouth_ctl():
    jaw = 'jaw'
    teeU = 'teethUpper'
    teeL = 'teethLower'
    tonR = 'tongueRight'
    tonC = 'tongueCenter'
    tonL = 'tongueLeft'
    tonM = 'tongueCenter'
    for attr in ['translate', 'rotate', 'scale']:
        pm.connectAttr(jaw+'_ctl.%s'%attr, jaw+'Root_bon.%s'%attr, f=True)
        pm.connectAttr(teeU+'_ctl.%s'%attr, teeU+'_bon.%s'%attr, f=True)
        pm.connectAttr(teeL+'_ctl.%s'%attr, teeL+'_bon.%s'%attr, f=True)
        pm.connectAttr(tonR+'A_ctl.%s'%attr, tonR+'A_bon.%s'%attr, f=True)
        pm.connectAttr(tonC+'A_ctl.%s'%attr, tonC+'A_bon.%s'%attr, f=True)
        pm.connectAttr(tonL+'A_ctl.%s'%attr, tonL+'A_bon.%s'%attr, f=True)
        pm.connectAttr(tonM+'ARoot_ctl.%s'%attr, tonM+'ARoot_bon.%s'%attr, f=True)
        pm.connectAttr(tonR+'B_ctl.%s'%attr, tonR+'B_bon.%s'%attr, f=True)
        pm.connectAttr(tonC+'B_ctl.%s'%attr, tonC+'B_bon.%s'%attr, f=True)
        pm.connectAttr(tonL+'B_ctl.%s'%attr, tonL+'B_bon.%s'%attr, f=True)
        pm.connectAttr(tonM+'BRoot_ctl.%s'%attr, tonM+'BRoot_bon.%s'%attr, f=True)
        pm.connectAttr(tonR+'C_ctl.%s'%attr, tonR+'C_bon.%s'%attr, f=True)
        pm.connectAttr(tonC+'C_ctl.%s'%attr, tonC+'C_bon.%s'%attr, f=True)
        pm.connectAttr(tonL+'C_ctl.%s'%attr, tonL+'C_bon.%s'%attr, f=True)
        pm.connectAttr(tonM+'CRoot_ctl.%s'%attr, tonM+'CRoot_bon.%s'%attr, f=True)
        pm.connectAttr(tonR+'D_ctl.%s'%attr, tonR+'D_bon.%s'%attr, f=True)
        pm.connectAttr(tonC+'D_ctl.%s'%attr, tonC+'D_bon.%s'%attr, f=True)
        pm.connectAttr(tonL+'D_ctl.%s'%attr, tonL+'D_bon.%s'%attr, f=True)
        pm.connectAttr(tonM+'DRoot_ctl.%s'%attr, tonM+'DRoot_bon.%s'%attr, f=True)