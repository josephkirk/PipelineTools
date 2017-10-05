import pymel.core as pm
from time import sleep,time
import PipelineTools.main.utilities as ul
import PipelineTools.customclass.rigging as rigclass
import riggingMisc as rm
import maya.mel as mm
import string
for mod in [ul,rigclass,rm]:
    reload(mod)

def create_miscGP():
    pass

def import_Facial_Target():
    pass

def create_fac_ctl_shader():
    fac_shadeGP = {
        'green': (
            [0,0.18,0,0.8],
            ['eyeLeftA_ctl',
             'eyeLeftB_ctl',
             'eyeLeftC_ctl',
             'eyeLeftD_ctl',
             'cheekLeftA_ctl',
             'cheekLeftC_ctl',
             'lipCenterA_ctl',
             'lipCenterB_ctl',
             'eyeRightA_ctl',
             'eyeRightB_ctl',
             'eyeRightC_ctl',
             'eyeRightD_ctl',
             'cheekRightA_ctl',
             'cheekRightC_ctl']),
        'blue': (
            [0,0,0.4,0.6],
            ['eyebrowLeftA_ctl',
             'eyebrowLeftC_ctl',
             'lipLeftB_ctl',
             'noseTop_ctl',
             'eyebrowRightA_ctl',
             'eyebrowRightC_ctl',
             'lipRightB_ctl']),
        'red': (
            [0.24,0.028,0,0.75],
            ['eyebrowLeftB_ctl',
             'eyeSubLeftC_ctl',
             'eyeSubLeftD_ctl',
             'lipLeftC_ctl',
             'eyebrowRightB_ctl',
             'eyeSubRightC_ctl',
             'eyeSubRightD_ctl',
             'lipRightC_ctl']),
        'cyan':(
            [0,0.193,0.193,0.8],
            ['eyeSubLeftA_ctl',
            'eyeSubLeftB_ctl',
            'noseLeftA_ctl',
            'cheekLeftB_ctl',
            'lipLeftA_ctl',
            'eyeSubRightA_ctl',
            'eyeSubRightB_ctl',
            'noseRightA_ctl',
            'cheekRightB_ctl',
            'lipRightA_ctl'])}
    for shader, (color,members) in fac_shadeGP.items():
        shdr_name = 'fac_mtl_{}'.format(shader)
        sg_name = '{}{}'.format(shdr_name,'SG')
        if pm.objExists(shdr_name) or pm.objExists(sg_name):
            try:
                pm.delete(shdr_name)
                pm.delete(sg_name)
            except:
                pass
        shdr,sg = pm.createSurfaceShader('surfaceShader')
        pm.rename(shdr,'fac_mtl_{}'.format(shader))
        pm.rename(sg,'{}{}'.format(shdr.name(),'SG'))
        shdr.outColor.set(color[:3])
        shdr.outTransparency.set([color[-1],color[-1],color[-1]])
        for member in members:
            member = ul.get_node(member)
            pm.sets(sg, fe=member)

def create_facialguide_ctl():
    facialpart_name = {
        'eye':30,
        'nose':3,
        'cheek':6,
        'lip':8,}
    facial_bones = {}
    for part,count in facialpart_name.items():
        facial_bones[part] = rigclass.FacialBone.bones(part)['All']
        if len(facial_bones[part]) != count:
            pm.error('{} missing bones, bone count is {}, right amount is {}. Recheck Scene!'.format(part, len(facial_bones[part]), count),n=True)
    #pm.select(cl=True)
    for key, values in facial_bones.items():
        print key, 'bones:\n'
        print 'bone count:' , len(values)
        for value in values:
            if value.offset:
                print value.bone, value.offset
                pm.select(value.bone, add=True)
        print '#'*20


def create_facial_panel():
    rm.create_facial_panel()

def create_ctl():
    '''
    create Facial Control and snap to bone Position
    '''
    if pm.objExists('ctlGp'):
        pm.delete('ctlGp')
    rm.create_ctl()
    ul.get_node('ctlGp').setParent(ul.get_node('ROOT'))
    root = {}
    root['jaw'] = (ul.get_node('jaw_ctlGp'),ul.get_node('jawRoot_bon'))
    root['teeth'] = (ul.get_node('teethUpper_ctlGp'),ul.get_node('teethUpper_bon'))
    root['eye'] = (ul.get_node('eye_ctlGp'),ul.get_node('eyeLeftEnd_bon'))
    for v in string.ascii_uppercase[:3]:
        root['tongue%s'%v] = (ul.get_node('tongueCenter%s_bon'%v),ul.get_node('tongueCenter%sRoot_ctlGp'%v))

    for key,(ob,target) in root.items():
        ob_pos = ob.getTranslation('world')
        target_pos = target.getTranslation('world')
        dest_pos = target_pos
        if ob == root['eye'][0]:
            dest_pos = [ob_pos[0], target_pos[1], ob_pos[2]]
        ob.setTranslation(dest_pos,space='world')
    parent_ctl_to_head()

def snap_eye_ctl():
    '''
        snap eye Control to end Bone Position
    '''
    for dir in ['Left','Right']:
        eye_endbone = ul.get_node('eye%sEnd_bon'%dir)
        eye_ctl = ul.get_node('eye%s_frmGp'%dir)
        pm.select(eye_ctl,r=True)
        pm.setToolTo('moveSuperContext')
        mm.eval('BakeCustomPivot;')
        eye_endbone_pos = eye_endbone.getTranslation(space='world')
        eye_ctl_pos = eye_ctl.getTranslation(space='world')
        eye_ctl.setTranslation((eye_endbone_pos[0],eye_endbone_pos[1],eye_ctl_pos[2]), space='world')     

def create_eye_constraint():
    '''
        aim constraint eye bone to control
    '''
    for dir in ['Left','Right']:
        eye_bone = ul.get_node('eye%s_bon'%dir)
        eye_ctl = ul.get_node('eye%s_ctl'%dir)
        aim_constraint = pm.aimConstraint(eye_ctl,eye_bone,mo=True,wut='objectrotation',wuo=ul.get_node('eyeRoot_ctl'))

def snap_eye_root_ctl():
    '''
        resize eyeRoot_ctl to match eye_frmGp
    '''
    bbs=[]
    ob = ul.get_node('eyeRoot_ctl')
    for dir in ['Left','Right']:
        eye_ctl = ul.get_node('eye%s_frmGp'%dir)
        bb= pm.xform(eye_ctl,q=True,bb=True,ws=True)
        bb = [pm.dt.Point(p) for p in [bb[3:], bb[:3], [bb[3], bb[1], bb[5]], [bb[0], bb[4], bb[5]]]]
        bbs.extend(bb)
    bb = [bbs[0],bbs[2],bbs[5],bbs[7]]
    
    for id,cvid in enumerate([3,4,1,2]):
        #print bb[id],ob.cv[cvid]
        if cvid == 4:
            ob.setCV(0,bb[id],space='world')
            ob.setCV(cvid,bb[id],space='world')
            continue
        ob.setCV(cvid,bb[id],space='world')
    obdup = pm.duplicate(ob)
    for child in obdup[0].listRelatives(type='transform'):
        pm.delete(child)
    pm.select(obdup,r=True)
    ul.lock_transform(lock=False, pivotToOrigin=False)
    obdup[0].setScale([1.05,1.05,1.05])
    pm.makeIdentity(obdup[0], apply=True)
    pm.delete('eyeRoot_ctlShape', s=True)
    pm.select(ob,add=True)
    ul.parent_shape()
    ob.updateCurve()

def connect_eye_attr():
    '''
        connect eye bone rotate to eye lid bone
    '''
    for dir in ['Left','Right']:
        eye_bone = ul.get_node('eye%s_bon'%dir)
        eye_endbone = ul.get_node('eye%sEnd_bon'%dir)
        eye_ctl = ul.get_node('eye%s_ctl'%dir)
        eyelid_bone = ul.get_node('eyeLid%s_bon'%dir)
        mul1 = pm.nt.MultiplyDivide()
        mul2 = pm.nt.MultiplyDivide()
        mul1.attr('operation').set(1)
        mul1.attr('operation').set(2)
        eyeRoot = ul.get_node('eyeRoot_ctl')
        for dir in ["X","Y","Z"]:
            eyeRoot.EyeLidAim >> mul1.attr('input1%s'%dir)
            mul1.attr('input2%s'%dir).set(100)
        mul1.output >> mul2.input2
        eye_bone.rotate >> mul2.input1
        mul2.output >> eyelid_bone.rotate
        eye_ctl.scale >> eye_endbone.scale

def parent_ctl_to_head():
    '''
        parent control to head
    '''
    face_root_ctl = ul.get_node('facialRig_Gp')
    eye_root_ctl = ul.get_node('eye_ctlGp')
    headBone = ul.get_node('CH_Head')
    pm.xform(face_root_ctl,pivots=[0,0,0],p=True,ws=True)
    pm.parentConstraint(headBone, face_root_ctl,mo=True)
    pm.parentConstraint(headBone, eye_root_ctl,mo=True)


### main code
def create_eye_rig():
    '''
        step to create eye rig
    '''
    snap_eye_ctl()
    snap_eye_root_ctl()
    create_eye_constraint()
    connect_eye_attr()

def create_facial_ctl():
    create_ctl()
    create_eye_rig()
    parent_ctl_to_head()

def create_facial_bs_ctl():
    pass

### old code
@ul.do_function_on('single')
def constraint_ctrl_to_loc(ob):
    offgpname = ob.replace('_ctl','_offset_Gp')
    gpname = ob.replace('_ctl','_Gp')
    pm.group(ob, n=offgpname)
    pm.group(offgpname, n=gpname)
    locname = ob.replace('_ctl','_loc')
    pm.pointConstraint(locname, gpname, o=(0,0,0), w=1)

@ul.do_function_on('singlelast',type_filter='transform')
def snap_to_near_vertex_midedge(ob, target, constraint=False):
    print ob, target
    if constraint:
        closest_uv = ul.get_closest_component(ob, target)
        PPconstraint = pm.pointOnPolyConstraint(
            target, ob, mo=False,
            name=(ob.name()+'pointOnPolyConstraint1'))
        PPconstraint.attr(target.name().split('|')[-1]+'U0').set(closest_uv[0])
        PPconstraint.attr(target.name().split('|')[-1]+'V0').set(closest_uv[1])
        print ob, 'constraint to', target 
        return PPconstraint
    closest_component = ul.get_closest_component(ob, target, uv=False)
    ob.setTranslation(closest_component, space='world')
    return closest_component
    
    #get_closest_vert()
    #return distance_list

@ul.do_function_on('single')
def group_loc(ob):
    gpname = ob + '_Gp'
    pm.group(ob, n=gpname)

@ul.do_function_on('single')
def make_loc_and_ctl_from_bon(ob):
    locname = ob.replace('_bon','_loc')
    loc = pm.spaceLocator(p=(0,0,0), n=locname)
    pc = pm.pointConstraint(ob, loc, o=(0,0,0), w=1)
    pm.delete(pc)
    ctlname = ob.replace('_bon','_ctl')
    sph = pm.sphere(p=(0,0,0), ax=(0,1,0), ssw=0, esw=360, r=0.35, d=3, ut=False, tol=0.01, s=8, nsp=4, ch=False, n=ctlname)
    pc = pm.pointConstraint(ob, sph, o=(0,0,0), w=1)
    pm.delete(pc)

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
    pm.connectAttr(mouthCnt+'.mouth_smileClose', faceBS+'.mouth_smileclose', f=True)
    pm.connectAttr(mouthCnt+'.mouth_angerClose', faceBS+'.mouth_angerclose', f=True)

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