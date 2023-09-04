import pymel.core as pm
from time import sleep,time
import PipelineTools.main.utilities as ul
import PipelineTools.main.rigging as rig
import PipelineTools.baseclass.rig as rigclass
import riggingMisc as rm
import maya.mel as mm
import string
for mod in [ul, rigclass, rig, rm]:
    reload(mod)
@ul.error_alert
def setup_facialgp():
    miscgp = ul.get_node('miscGp')
    if not miscgp:
        miscgp = pm.nt.Transform(name='miscGp')
        miscgp.setParent(ul.get_node('ROOT'))
    #else:
    facialdeform = ul.get_node('face_deformationSystem')
    if not facialdeform:
        facialdeform = pm.nt.Transform(name='face_deformationSystem')
        facialdeform.setParent(ul.get_node(miscgp))
    facegp = pm.ls('*_face_grp')
    if facegp:
        facegp = facegp[0]
    else:
        pm.error('missing mdl_face_grp')
    eyegp = pm.ls('*_eye_grp')
    if eyegp:
        eyegp = eyegp[0]
    else:
        pm.error('missing mdl_eye_grp')
    facial_gp = {
        'orig':[],
        'jawDeform':[],
        'facialGuide':[],
        'facial':[],
        'eyeDeform':[]}
    for item in facial_gp:
        if not pm.ls(item):
            if item == 'eyeDeform':
                dupgp = pm.duplicate(eyegp, name=item)[0]
            else:
                dupgp = pm.duplicate(facegp, name=item)[0]
            childs = dupgp.getChildren()

            for child in childs:
                if item == 'eyeDeform':
                    pm.rename(child, '{}_{}'.format(item,child.name()[-1]))
                    for subchild in child.getChildren():
                        pm.rename(subchild, subchild.name().replace('_mdl_', '_mdl_{}_'.format(item)))
                else:
                    pm.rename(child, child.name().replace('_mdl_', '_mdl_{}_'.format(item)))
            dupgp.setParent(facialdeform)
            if item == 'facialGuide':
                pm.parentConstraint('CH_Head', 'facialGuide', mo=True)
@ul.error_alert
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
@ul.error_alert
def create_facialguide_ctl():
    facialpart_name = {
        'eye':32,
        'nose':3,
        'cheek':6,
        'lip':8,}
    facial_bones = {}
    ##### skin to facial
    pm.select('facial',r=True)
    pm.select('facialRoot_bon',add=True)
    mm.eval('newSkinCluster "-toSelectedBones -bindMethod 1 -normalizeWeights 1 -weightDistribution 1 -mi 1 -dr 2 -rui false,multipleBindPose,1";')
    skin_cluster = ul.get_skin_cluster(pm.ls('facial|*_mdl_head')[0])
    pm.select(cl=True)
    #######
    guide_mesh = pm.ls('*_mdl_facialGuide_head')
    if not guide_mesh:
        pm.error('missing _mdl_facialGuide_head')
    guide_mesh = guide_mesh[0]
    for part,count in facialpart_name.items():
        facial_bones[part] = rigclass.FacialBone.getBones(part)['All']
        if len(facial_bones[part]) != count:
            for bone in facial_bones[part]:

            #pm.select(facial_bones[part], r=True)
            pm.error('{} have duplicate or missing bones, bone count is {}, right amount is {}. Recheck Scene!'.format(part, len(facial_bones[part]), count),n=True)
    #pm.select(cl=True)
    if pm.objExists('facialGuide_locGp'):
        loc_gp = ul.get_node('facialGuide_locGp')
    else:
        loc_gp = pm.nt.Transform(name='facialGuide_locGp')
        loc_gp.setParent(ul.get_node('miscGp'))
    if pm.objExists('facialRig_Gp'):
            ctl_gp = ul.get_node('facialRig_Gp')
    else:
        ctl_gp = pm.nt.Transform(name='facialRig_Gp')
        ctl_gp.setParent(ul.get_node('ctlGp'))
    for key, values in facial_bones.items():


        for value in values:
            if value.offset:


                if not value.control.node:
                    value.control.create(pos=value.bone.getTranslation('world'), parent=ul.get_node(ctl_gp))
                else:
                    value.get_control()



                if not value.control.root.name() != value.control.root_name:
                    pm.rename(value.control.root, value.control.root_name)
                value.control.guide.create(pos=value.bone.getTranslation('world'), parent=loc_gp)

                value.control.guide.set_guide_mesh(guide_mesh)
                value.control.guide.set_constraint()

                value.control.set_constraint()

                value.connect()
                #pm.select('facial')
                #pm.select(value.bone)
                pm.skinCluster(skin_cluster, edit=True,
                   ug=True, dr=2, ps=0, ns=10, lw=True, wt=0,
                   ai=value.bone)
                pm.skinCluster(skin_cluster, edit=True,
                   lw=False,
                   inf=value.bone)
                #pm.skinCluster(tsb=True)
                #pm.select(cl=True)

                #pm.select(value.bone, add=True)

    create_fac_ctl_shader()
@ul.error_alert
def connect_mouth_ctl():
    mouth_part = ['jaw','teeth','tongue']
    for part in mouth_part:
        bones = rigclass.FacialBone.getBones(part)['All']
        for bone in bones:
            if bone.offset:
                if bone.control.node:
                    bone.connect()

                else:
                    if 'Root' in bone.bone.name():

                        newName = bone._name.replace('Root','')
                        bone.get_control(other_name=newName)
                        bone.connect()

                    else:

                    
@ul.error_alert
def import_facialtarget():
    scenedir = pm.sceneName().dirname()
    dir =  scenedir.parent
    bsdir = pm.util.common.path(dir+'/facialtarget/facialtarget.mb')
    pm.importFile(bsdir, defaultNamespace=True)
    bstarget_gp = pm.ls('*_facialtarget')
    if bstarget_gp:
        bstarget_gp = bstarget_gp[0]
        bstarget_gp.setParent(ul.get_node('miscGp'))
        bstargets = bstarget_gp.getChildren()
        pm.select(bstargets,r=True)
        pm.select('jawDeform',add=True)
        pm.select('orig',add=True)
        facebs = pm.blendShape(name='FaceBaseBS', automatic=True)
        facebs[0].jawDeform.set(1)
        for key, value in {'facialGuide':'FaceGuideBS','facial':'FaceDeformBS'}.items():
            pm.select('orig',r=True)
            pm.select(key,add=True)
            pm.blendShape(name=value,w=[(0,1),], automatic=True)
        pm.select('facial',r=True)
        pm.select("*_face_grp_skinDeform",add=True)
        pm.blendShape(name='RootBS',w=[(0,1),], automatic=True, after=True)
        pm.select('eyeDeform',r=True)
        pm.select("*_eye_grp_skinDeform",add=True)
        pm.blendShape(name='EyeDeformBS',w=[(0,1),], automatic=True, after=True)
    connect_Bs_control()
@ul.error_alert
def add_jawdeform_skin():
    facial_parts = {
        'facialRoot,jawRoot,eyeLid':['head'],
        'facialRoot,eyeLid':['eyelash','Matsuge'],
        'teethUpper':['tooth_U'],
        'teethLower':['tooth_D'],
        'tongue':['tongue']}
    pm.select(cl=True)
    for parts,meshes in facial_parts.items():
        bones=[]
        try:
            for part in parts.split(','):
                if part:

                    if part != 'tongue':
                        get_bones = [bone for bone in rigclass.FacialBone.getBones(part)['All'] if bone.bone and 'End' not in bone.name]
                    else:
                        get_bones = [bone for bone in rigclass.FacialBone.getBones(part)['All'] if bone.bone and 'Root' not in bone.name]
                        get_bones.append(ul.get_node('tongueRoot_bon'))
                    if get_bones:
                        bones.append(get_bones)
            skin_mesh = []
            for mesh in meshes:
                skin_mesh.append(pm.ls('*_jawDeform_{}'.format(mesh)))
            if skin_mesh and bones:

                pm.select(skin_mesh,r=True)
                pm.select(bones,add=True)
                mm.eval('newSkinCluster "-toSelectedBones -bindMethod 1 -normalizeWeights 1 -weightDistribution 1 -mi 1 -dr 2 -rui false,multipleBindPose,1";')
            else:
                "can not add skin for %s"%parts
                raise
        except:


@ul.error_alert
def add_eyeform_skin():
    for dir in ['Left','Right']:
        if all([pm.ls(ob) for ob in ['eye{}_bon'.format(dir), 'eye{}End_bon'.format(dir), 'eyeDeform_{:.1}'.format(dir)]]):
            pm.select('eye{}_bon'.format(dir), 'eye{}End_bon'.format(dir), 'eyeDeform_{:.1}'.format(dir),r=True)
            mm.eval('newSkinCluster "-toSelectedBones -bindMethod 1 -normalizeWeights 1 -weightDistribution 1 -mi 1 -dr 2 -rui false,multipleBindPose,1";')
        else:


@ul.error_alert
def copy_facialskin():
    curscene = pm.sceneName()
    skin_dir = curscene.dirname().dirname().__div__('facialskin')
    for file in skin_dir.files('*.mb*'):
        file_name = file.basename().replace(file.ext,'')
        pm.createReference(file,namespace=file_name)

        deformGp_list = ['facial', 'jaw', 'eye']
        for deformGp_name in deformGp_list:
            if deformGp_name in file_name.lower():
                target_deformGp_name = 'face_deformationSystem|{}*'.format(deformGp_name)
                src_deformGp_name = '{}:{}*'.format(file_name,deformGp_name)
                target_gp = pm.ls(target_deformGp_name)[0] if pm.ls(target_deformGp_name) else None
                src_gp = pm.ls(src_deformGp_name)[0] if pm.ls(src_deformGp_name) else None
                if target_gp and src_gp:

                    rig.copy_skin_multi(src_gp, target_gp)
                else:

        pm.FileReference(file).remove()
        # for object in ['head', 'tongue', 'eyelash', 'Matsuge']:
        #     skin_src_get = pm.ls('{}:*_{}'.format(file_name, object))
        #     eye_skin_src_get = pm.ls('{}:*_{}'.format(file_name, object))
        #     if 'facial' in file_name.lower():
        #         skin_target_get = pm.ls('facial|*_mdl_{}'.format(object))
        #     elif 'jaw' in file_name.lower():
        #         skin_target_get = pm.ls('jawDeform|*_jawDeform_{}'.format(object))
        #     if skin_src_get and skin_target_get:
        #         if ul.get_skin_cluster(skin_src_get[0]) and ul.get_skin_cluster(skin_target_get[0]):
        #             pm.select(skin_src_get,r=True)
        #             pm.select(skin_target_get,add=True)
        #             mm.eval('copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation closestJoint -influenceAssociation label -normalize;')

        # if 'jaw' in file_name.lower():
        #     for object in ['eye', 'eyelens', 'eyeref']:
        #         for direction in ['L','R']:
        #             skin_src_get = pm.ls('{}:*mdl_{}_{}'.format(file_name, object, direction))
        #             skin_target_get = pm.ls('*_mdl_eyeDeform_{}_{}'.format( object, direction))
        #             if skin_src_get and skin_target_get:
        #                 if ul.get_skin_cluster(skin_src_get[0]) and ul.get_skin_cluster(skin_target_get[0]):
        #                     pm.select(skin_src_get,r=True)
        #                     pm.select(skin_target_get,add=True)
        #                     mm.eval('copySkinWeights  -noMirror -surfaceAssociation closestPoint -influenceAssociation label -normalize;')

        #             else:






        # pm.FileReference(file).remove()
@ul.error_alert
def create_guidebs():
    pm.select('orig',r=True)
    pm.select('facialGuide',add=True)
    pm.blendShape(name='FaceGuideBS', automatic=True)
@ul.error_alert
def create_deformbs():
    pm.select('orig',r=True)
    pm.select('facial',add=True)
    pm.blendShape(name='FaceDeformBS', automatic=True)
@ul.error_alert
def create_rootbs():
    pm.select('facial',r=True)
    pm.select("*_mdl_face_grp_skinDeform")
    pm.blendShape(name='RootBS',w=[(0,1),], automatic=True)
@ul.error_alert
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
    root['teethUpper'] = (ul.get_node('teethUpper_ctlGp'),ul.get_node('teethUpper_bon'))
    root['eye'] = (ul.get_node('eye_ctlGp'),ul.get_node('eyeLeftEnd_bon'))
    for v in string.ascii_uppercase[:4]:
        root['tongue%s'%v] = (ul.get_node('tongueCenter%sRoot_ctlGp'%v),ul.get_node('tongueCenter%s_bon'%v))
    root['teethLower'] = (ul.get_node('teethLower_ctlGp'),ul.get_node('teethLower_bon'))
    for key,(ob,target) in root.items():

        ob_pos = ob.getTranslation('world')
        target_pos = target.getTranslation('world')
        dest_pos = target_pos
        if key == 'eye':
            dest_pos = [ob_pos[0], target_pos[1], ob_pos[2]]
        ob.setTranslation(dest_pos,space='world')

        #ob.setPivots(dest_pos, worldSpace=True)
        if key != 'eye':
           pm.matchTransform(ob, target, pivots=True)
           pm.matchTransform(ob.getChildren()[0], target, pivots=True)

    pm.parentConstraint('CH_Head', 'facialRig_Gp', mo=True)

    pm.parentConstraint('CH_Head', 'eye_ctlGp', mo=True)

@ul.error_alert
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
@ul.error_alert
def create_eye_constraint():
    '''
        aim constraint eye bone to control
    '''
    for dir in ['Left','Right']:
        eye_bone = ul.get_node('eye%s_bon'%dir)
        eye_ctl = ul.get_node('eye%s_ctl'%dir)
        aim_constraint = pm.aimConstraint(eye_ctl,eye_bone,mo=True,wut='objectrotation',wuo=ul.get_node('eyeRoot_ctl'))
@ul.error_alert
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

        if cvid == 4:
            ob.setCV(0,bb[id],space='world')
            ob.setCV(cvid,bb[id],space='world')
            continue
        ob.setCV(cvid,bb[id],space='world')
    ob.updateCurve()
    obdup = pm.duplicate(ob)
    for child in obdup[0].listRelatives(type='transform'):
        pm.delete(child)
    pm.select(obdup,r=True)
    ul.lock_transform(lock=False, pivotToOrigin=False)
    obdup[0].setScale([1.05,1.05,1.05])
    #pm.makeIdentity(obdup[0], apply=True)
    #pm.delete('eyeRoot_ctlShape', s=True)
    pm.select(ob,add=True)
    ul.parent_shape()

@ul.error_alert
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
        for satr in ['sx','sy','sz']:
            eye_endbone.attr(satr).set(eye_ctl.scaleX)

@ul.error_alert
def parent_ctl_to_head():
    '''
        parent control to head
    '''
    ctls = []
    ctls.append('facialGuide')
    ctls.append('facial_panelGp')
    ctls.append('facialRig_Gp')
    ctls.append('ctlGp|eye_ctlGp')
    headBone = ul.get_node('CH_Head')
    for ctl in ctls:
        pm.parentConstraint(headBone, ctl, mo=True)
@ul.error_alert
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
### main code
@ul.error_alert
def create_facial_panel(offset=6.5):
    rm.create_bs_ctl()
    pm.headsUpMessage("Create Facial BlendShape Control", time=0.2)
    pm.refresh()
    sleep(0.1)
    facial_panelGp = ul.get_node('facial_panelGp')
    panel_pos = facial_panelGp.getTranslation('world')
    headBone = ul.get_node('CH_Head')
    headBone_pos = headBone.getTranslation('world')
    facial_panelGp.setTranslation([panel_pos[0], headBone_pos[1]+offset , panel_pos[2]], 'world')
    pm.headsUpMessage("Snap Control to Head", time=0.2)
    pm.refresh()
    sleep(0.1)
    import_facialtarget()
    pm.headsUpMessage("Import BlendShape and connect to control", time=0.2)
    pm.refresh()
    sleep(0.1)
    pm.parentConstraint('CH_Head', 'facial_panelGp', mo=True)
    pm.headsUpMessage("Parent Constraint facial_panelGp to head bone", time=0.2)
    pm.refresh()
    sleep(0.1)

def create_eye_rig():
    '''
        step to create eye rig
    '''
    msg = []
    msg.append(snap_eye_ctl())
    msg.append(snap_eye_root_ctl())
    msg.append(create_eye_constraint())
    msg.append(connect_eye_attr())
    return msg

#@ul.error_alert
def create_facial_ctl():
    msg = []
    msg.append(create_ctl())
    pm.headsUpMessage("Face Control Created", time=0.2)
    sleep(0.1)
    msg.append(create_eye_rig())
    pm.headsUpMessage("Eyes Rig Created", time=0.2)
    sleep(0.1)
    msg.append(connect_mouth_ctl())
    pm.headsUpMessage("Mouth Control to Bone Connected", time=0.2)
    return msg
    #parent_ctl_to_head()

#@ul.error_alert
def create_facial_bs_ctl():
    msg=[]
    pm.headsUpMessage("Create Facial Deformation Groups", time=0.2)
    msg.append(setup_facialgp())
    pm.refresh()
    sleep(0.1)
    pm.headsUpMessage("Create Facial Control and Guide rig, skin", time=0.2)
    msg.append(create_facialguide_ctl())
    pm.refresh()
    sleep(0.1)
    pm.headsUpMessage("Add skin to Jaw Deform Group", time=0.2)
    msg.append(add_jawdeform_skin())
    pm.refresh()
    sleep(0.1)
    pm.headsUpMessage("Add skin to Jaw Deform Group", time=0.2)
    msg.append(add_eyeform_skin())
    pm.refresh()
    sleep(0.1)
    pm.headsUpMessage("create Face Blend Shape Control, import and set up BlenShape", time=0.2)
    msg.append(create_facial_panel())
    return msg

@ul.timeit
def create_facial_rig():
    errmsg = []
    msg = ft.create_ctl()
    errmsg.append(msg)
    pm.refresh()
    if not pm.confirmBox(title='Facial Rig Status',message = "Face Control Created\nError:\n%s"%msg, yes='Continue?', no='Stop?'):
        return
    msg = ft.create_eye_rig()
    errmsg.append(msg)
    pm.refresh()
    if not pm.confirmBox(title='Facial Rig Status',message = "Eyeballs Rig Created\nError:\n%s"%msg, yes='Continue?', no='Stop?'):
        return
    msg = ft.connect_mouth_ctl()
    errmsg.append(msg)
    pm.refresh()
    if not pm.confirmBox(title='Facial Rig Status',message = "Mouth Control to Bone Connected\nError:\n%s"%msg, yes='Continue?', no='Stop?'):
        return
    msg = ft.create_facial_bs_ctl()
    errmsg.append(msg)
    pm.refresh()
    if not pm.confirmBox(title='Facial Rig Status',message = "Create BlendShape control and setup BlendShape \nError:\n%s"%msg, yes='Continue?', no='Stop?'):
        return
    # ft.parent_ctl_to_head()
    # pm.refresh()
    # if not pm.confirmBox(title='Facial Rig Status',message = "Parent Root Group to Head OK", yes='Continue?', no='Stop?'):
    #     return
    msg = ft.copy_facialskin()
    pm.refresh()
    if not pm.confirmBox(title='Facial Rig Status',message = "Facial Copy \nError:\n%s"%msg, yes='Continue?', no='Stop?'):
        return
    pm.informBox(title='Riggin Status', message = "Face Rig Complete")

def facialScriptNode():
    def connectBS():
        try:
            if not pm.ls('RootBS') and not pm.ls('EyeDeformBS'):
                pm.select('facial',r=True)
                pm.select("*_face_grp_skinDeform",add=True)
                pm.blendShape(name='RootBS',w=[(0,1),], automatic=True)
                pm.select('eyeDeform',r=True)
                pm.select("*_eye_grp_skinDeform",add=True)
                pm.blendShape(name='EyeDeformBS',w=[(0,1),], ar=True)
        except:

    def unConnectBS():
        try:
            pm.delete('RootBS')
            pm.delete('EyeDeformBS')
        except:
            'cant delete RootBS and EyeDeformBS'
    initNode = pm.scriptNode( st=2, bs='connectBS()', n='script', stp='python')
    pm.scriptNode(initNode, e=True, afterScript='unConnectBS()', stp='python'
    return initNode 