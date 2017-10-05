import pymel.core as pm
from time import sleep,time
import PipelineTools.main.utilities as ul
import PipelineTools.customclass.rigging as rigclass
import riggingMisc as rm
import maya.mel as mm
import string
for mod in [ul,rigclass,rm]:
    reload(mod)

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
            print childs
            for child in childs:
                if item == 'eyeDeform':
                    pm.rename(child, '{}_{}'.format(item,child.name()[-1]))
                else:
                    pm.rename(child, child.name().replace('_mdl_', '_mdl_{}_'.format(item)))
            dupgp.setParent(facialdeform)

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
        'eye':32,
        'nose':3,
        'cheek':6,
        'lip':8,}
    facial_bones = {}
    guide_mesh = pm.ls('*_mdl_facialGuide_head')
    if not guide_mesh:
        pm.error('missing _mdl_facialGuide_head')
    guide_mesh = guide_mesh[0]
    for part,count in facialpart_name.items():
        facial_bones[part] = rigclass.FacialBone.bones(part)['All']
        if len(facial_bones[part]) != count:
            for bone in facial_bones[part]:
                print bone
            pm.select(facial_bones[part], r=True)
            pm.error('{} have duplicate or missing bones, bone count is {}, right amount is {}. Recheck Scene!'.format(part, len(facial_bones[part]), count),n=True)
    #pm.select(cl=True)
    if pm.objExists('facialGuide_locGp'):
        loc_gp = ul.get_node('facialGuide_locGp')
    else:
        loc_gp = pm.nt.Transform(name='facialGuide_locGp')
        loc_gp.setParent(ul.get_node('miscGp'))
    for key, values in facial_bones.items():
        print key, 'bones:\n'
        print 'bone count:' , len(values)
        for value in values:
            if value.offset:
                print value.bone, value.offset
                print value.control
                if not value.control.node:
                    value.control.create(pos=value.bone.getTranslation('world'), parent=ul.get_node('ctlGp'))
                else:
                    value.get_control()
                #print 'create', value.control.node
                #print value.control.guide 
                print value.control.root_name
                if not value.control.root.name() != value.control.root_name:
                    pm.rename(value.control.root, value.control.root_name)
                value.control.guide.create(pos=value.bone.getTranslation('world'), parent=loc_gp)
                #print 'create', value.control.node.guide
                value.control.guide.set_guide_mesh(guide_mesh)
                value.control.guide.set_constraint()
                #print 'constraint {} to {}'.format(value.control.guide, guide_mesh)
                value.control.set_constraint()
                #print 'constraint {} to {}'.format(value.control.root, value.control.guide)
                value.connect()
                #print 'connect {} to {}'.format(value, value.control)
                #pm.select(value.bone, add=True)
        print '#'*20
    create_fac_ctl_shader()

def connect_mouth_ctl():
    mouth_part = ['jaw','teeth','tongue']
    for part in mouth_part:
        bones = rigclass.FacialBone.bones(part)['All']
        for bone in bones:
            if bone.offset:
                if bon.control.node:
                    bon.connect()

def create_facial_panel():
    rm.create_bs_ctl()
    import_facialtarget()

def import_facialtarget():
    scenedir = pm.sceneName().dirname()
    os.chdir(scenedir)
    os.chdir('..')
    dir =  os.getcwd()
    bsdir = dir+'\\facialtarget'
    bsdir = pm.util.common.path(bsdir+'\\facialtarget.mb')
    pm.importFile(bsdir, defaultNamespace=True)
    bstarget_gp = pm.ls('*_facialtarget')
    if bstarget_gp:
        bstarget_gp = bstarget_gp[0]
        bstarget_gp.setParent(ul.get_node('miscGp'))
        bstargets = bstarget_gp.getChildren()
        pm.select(bstargets,r=True)
        pm.select('jawDeform',add=True)
        pm.select('orig',add=True)
        facebs = pm.blendShape(name='FaceBaseBS',w=[(0,1),])
        facebs.jawDeform.set(1)
        for key, value in {'facialGuide':'FaceGuideBS','facial':'FaceDeformBS'}.items():
            pm.select('orig',r=True)
            pm.select(key,add=True)
            pm.blendShape(name=value,w=[(0,1),])
        pm.select('facial',r=True)
        pm.select("*_mdl_face_grp_skinDeform",add=True)
        pm.blendShape(name='RootBS',w=[(0,1),])
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
    connect_mouth_ctl()
    parent_ctl_to_head()

def create_facial_bs_ctl():
    setup_facialgp()
    create_facialguide_ctl()
    create_facial_panel()