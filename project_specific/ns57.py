#Project Specific Functions
from .. import core
import pymel.core as pm
import logging

# Logging initialize

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# reload
core._reload()
ul = core.ul
ru = core.rul
rcl = core.rcl

#--- Utilities Function ---

def set_Vray_material(mat,mat_type='dielectric',**kwargs):
    '''set Material Attribute'''
    if type(mat) == pm.nt.VRayMtl:
        dielectric_setting = {
            'brdfType':1,
            'reflectionGlossiness':0.805,
            'reflectionColorAmount':1,
            'useFresnel':1,
            'lockFresnelIORToRefractionIOR':1,
            'bumpMapType':1,
            'bumpMult':2.2
        }
        metal_setting = {
            'brdfType':1,
            'reflectionGlossiness':0.743,
            'reflectionColorAmount':1,
            'useFresnel':0,
            'lockFresnelIORToRefractionIOR':1,
            'bumpMapType':1,
            'bumpMult':1.8
        }
        shader_type = {
            'metal':metal_setting,
            'dielectric':dielectric_setting
        }
        if shader_type.has_key(mat_type):
            for attr,value in shader_type[mat_type].items():
                mat.attr(attr).set(value)
    for key,value in kwargs.items():
        try:
            mat.attr(key).set(value)
        except (IOError, OSError, AttributeError) as why:
            print why

def get_character_infos():
    scene_name = pm.sceneName()
    while True:
        if scene_name == scene_name.parent:
            break
        scene_name = scene_name.parent
        if scene_name.parent.endswith('CH'):
            break
    ch_infos = scene_name.basename().split('_')
    return ch_infos

def add_suffix(ob, suff="_skinDeform"):
    pm.rename(ob, ob.name()+str(suff))

def create_skinDeform(ob):
    dupOb = pm.duplicate(ob, name="_".join([ob.name(), "skinDeform"]))
    for child in dupOb[0].listRelatives(ad=True):
        add_suffix(child)

def basic_intergration():
    pm.PyNode('CH_ReferenceShape').visibility.set(False)
    root = pm.PyNode('ROOT')
    for atr in ['tx', 'ty', 'tz',
                'rx', 'ry', 'rz',
                'sx', 'sy', 'sz']:
        root.attr(atr).lock()
        root.attr(atr).set(cb=False, k=False)
    chref = pm.PyNode('CH_Ctrl_Reference')
    for atr in ['FacialVis','FacialBS','SecondaryVis','SecondaryBS']:
        if not chref.hasAttr(atr):
            chref.addAttr(atr,at='bool',k=1)
    if not chref.hasAttr('Radius'):
        chref.addAttr('Radius',at='float',k=1)
        chref.Radius.set(100)
    if not chref.Radius.outputs():
        temp = pm.circle(radius=100)
        temp[0].setRotation([-90,0,0])
        pm.makeIdentity(temp[0], apply=True)
        chref = pm.PyNode('CH_Ctrl_Reference')
        pm.parent(temp[0].getShape(), chref, r=True, s=True)
        pm.delete(chref.getShape(), shape=True)
        chref.Radius >> temp[1].radius
        pm.delete(temp[0])
    if pm.objExists('facialGp'):
        chref.FacialVis >> pm.PyNode('facialGp').visibility
    for bs in ['FacialBS','EyeDeformBS']:
        if pm.objExists(bs):
            chref.FacialBS >> pm.PyNode(bs).envelope
    if pm.objExists('secondaryGp'):
        chref.SecondaryVis >> pm.PyNode('secondaryGp').visibility
    if pm.objExists('SecondaryBS'):
        chref.SecondaryBS >> pm.PyNode('SecondaryBS').envelope

#--- Rigging Body Controls Methods ---

def create_prop_control(bone, parent='ctlGp',useLoc=False, **kws):
    if 'gp' not in bone.name().lower():
        bonGp = rul.create_parent(bone)
    ctlname = ul.get_name(bone).replace('bon', 'ctl')
    ctl = rul.createPinCircle(
            ctlname,
            step=4,
            sphere=True,
            radius=2,
            length=0)
    ctlGp = rul.create_parent(ctl)
    xformTo(ctlGp, bone)
    if useLoc:
        rul.connect_with_loc(ctl, bone, all=True)
    else:
        rul.connect_transform(ctl, bone, all=True)
    rul.control_tagging(ctl, metaname='PropControlsSet_MetaNode')
    if parent:
        if pm.objExists(parent):
            ctlGp.setParent(parent)
        else:
            pm.group(ctlGp,name=parent)
    return ctl

def create_free_control(bone, parent='ctlGp',useLoc=False, **kws):
    if 'gp' not in bone.name().lower():
        bonGp = rul.create_parent(bone)
    ctlname = bone.name().replace('bon', 'ctl')
    ctl = rul.createPinCircle(ctlname,length=0,sphere=True)
    ctlGp = rul.create_parent(ctl)
    xformTo(ctlGp, bone)
    if useLoc:
        rul.connect_with_loc(ctl, bone, all=True)
    else:
        rul.connect_transform(ctl, bone, all=True)
    control_tagging(ctl, metaname='FreeControlsSet_MetaNode')
    if parent:
        if pm.objExists(parent):
          ctlGp.setParent(parent)
        else:
            pm.group(ctlGp,name=parent)
    return ctl

def create_parent_control(boneRoot, parent='ctlGp',useLoc=False, **kws):
    ctls = []
    boneChain = ul.iter_hierachy(boneRoot)
    for bone in iter(boneChain):
        if 'offset' not in ul.get_name(bone):
            if bone.getParent():
                if 'offset' not in ul.get_name(bone.getParent()):
                    rul.create_offset_bone(bone)
            else:
                rul.create_offset_bone(bone)
            name = ul.get_name(bone).split('_')[0]
            ctl = createPinCircle(name)
            ctl.rename(name + '_ctl')
            ctlGp = create_parent(ctl)
            ctlGp.rename(name + '_ctlGp')
            match_transform(ctlGp,bone)
            rul.control_tagging(ctl, metaname='ParentControlsSet_MetaNode')
            if ctls:
                ctlGp.setParent(ctls[-1])
            ctls.append(ctl)
            rul.connect_transform(ctl, bone, all=True )
    ctlRoot = ctls[0].getParent()
    if useLoc:
        rul.connect_with_loc(
            ctls[0],
            ctls[0].outputs(type='joint')[0], all=True)
    if parent:
        if pm.objExists(parent):
            ctlRoot.setParent(parent)
        else:
            pm.group(ctlRoot,name=parent)
    return ctls

#--- Rigging Hair Control Methods ---

def create_long_hair(boneRoot, hairSystem='', circle=True):
    dynamicBones = rul.dup_bone_chain(boneRoot, suffix='dynamic')
    boneGp = rul.create_parent(boneRoot)
    dupBoneGp = rul.create_parent(dynamicBones[0])
    bonChain = ul.iter_hierachy(boneRoot)
    dupBoneChain = ul.iter_hierachy(dynamicBones[0])
    for bone, dupbone in zip(iter(bonChain),iter(dupBoneChain)):
        tranformBool = any([0<bone.attr(atr).get() or bone.attr(atr).get()>0 for atr in ['rx','ry','rz', 'sx','sy','sz']])
        if tranformBool:
            log.info('%s contain value in rotate or scale. Commencing freeze transform'%bone)
            rul.freeze_skin_joint(bone)
            pm.makeIdentity(dupbone, apply=True)
        offsetBone = rul.create_offset_bone(bone)
        offsetMeta = rul.as_meta(offsetBone)
        offsetMeta.connectChild(dupbone.name(), 'dynamicBone', 'drivenBone')
        #pm.orientConstraint(dupbone, offsetBone, mo=True)
        rul.connect_transform(dupbone, offsetBone,rotate=True)
    ikhandle, ikeffector, ikcurve = pm.ikHandle(
        sj=dynamicBones[0], ee=dynamicBones[-1], solver='ikSplineSolver', ns=3)
    ikhandle.setParent(dupBoneGp)
    ikcurve.rename(ul.get_name(boneRoot).replace('bon','ikCurve'))
    hairSystem = rul.make_curve_dynamic(ikcurve, hairSystem=hairSystem)
    dynamicCurve, follicle, hairSys = [i for i in hairSystem]
    dynamicCurve.worldSpace[0] >> ikhandle.inCurve
    controls = create_parent_control(boneRoot, parent='',useLoc=True)
    if circle:
        for control in controls:
            tempShape = rul.createPinCircle(
                control.name(),
                axis='YZ',
                radius=2,
                length=0)
            ul.parent_shape(tempShape, control)
            #pm.delete(tempShape)
    controlGp = rul.create_parent(controls[0].getParent())
    controlGp = controlGp.rename(controlGp.name().split('_')[0]+'_root_ctlGp')
    controlRoot = rul.createPinCircle(controlGp.name(),axis='YZ',radius=3,length=0)
    rul.xformTo(controlRoot, controlGp)
    controlRoot.setParent(controlGp)
    #loc.getParent().setParent(controlGp)
    dupBoneGp.setParent(controlRoot)
    focGp = follicle.getParent().getParent()
    follicle.getParent().setParent(controlRoot)
    pm.delete(focGp)
    pm.parentConstraint(dynamicBones[0],create_parent(controls[0]))
    hairSysMeta = rul.as_meta(hairSys)
    hairSysMeta.connectChildren([c.name() for c in controls], 'boneControl', 'hairSystem', srcSimple=True)
    for ctl, dynamicBone in zip(controls[1:], dynamicBones[1:]):
        offset = rul.create_parent(ctl)
        rul.control_tagging(ctl, metaname='DynamicHairControlsSet_MetaNode')
        loc = rul.connect_with_loc(dynamicBone, offset,all=True)[0]
        loc.getParent().setParent(dynamicBone.getParent())
    #lock ctlRoot translate and scale
    for atr in [
        'tx','ty','tz',
        'sx','sy','sz',]:
        controlRoot.setAttr(atr, lock=True, keyable=False, channelBox=False)
    if not pm.objExists('hairSystem_miscGp'):
        hairMiscGp = pm.nt.Transform(name='hairSystem_miscGp')
    hairMiscGp = pm.PyNode("hairSystem_miscGp")
    hairSys.getParent().setParent(hairMiscGp)
    dynamicCurve.getParent().getParent().setParent(hairMiscGp)
    if pm.objExists('ctlGp'):
        controlGp.setParent('ctlGp')
    else:
        pm.group(controlGp,name='ctlGp')
    if pm.objExists('miscGp'):
        hairMiscGp.setParent('miscGp')
    else:
        pm.group(hairMiscGp,name='miscGp')
    # add ctl tag
    rul.control_tagging(controlRoot, metaname='DynamicHairControlsSet_MetaNode')

def create_short_hair(bone, parent='miscGp'):
    bones = rul.get_current_chain(bone)
    bonename = bone.name().split('|')[-1]
    startBone = bones[0]
    endBone = bones[-1]
    midBone = bones[int(round((len(bones)-1)/2.0))]
    ikhandle, ikeffector, ikcurve = pm.ikHandle(
        sj=startBone, ee=endBone,solver='ikSplineSolver', ns=3)
    ikhandle.rename(bonename+'_ikhandle')
    ikeffector.rename(bonename+'_ikeffector')
    ikcurve.rename(bonename+'_ikCurve')
    sbonetop, mbonetop, ebonetop = [
        dup_bone(b,name = b.name()+'_'+suffix) for b,suffix in zip([startBone,midBone,endBone],['root','mid','top'])]
    #sbonetop.setParent(bone.getParent())
    if (len(bones)-1)%2.0 == 1:
        boneUp = bones[int(math.ceil((len(bones)-1)/2.0))]
        boneDown = bones[int(math.floor((len(bones)-1)/2.0))]
        mbonetop.setTranslation(
            (boneUp.getTranslation('world')+boneDown.getTranslation('world'))/2,'world')
    for b in [sbonetop, mbonetop, ebonetop]:
        b.setParent(None)
        b.radius.set(b.radius.get()*1.2)
    curveSkin = pm.skinCluster(sbonetop,mbonetop,ebonetop,ikcurve)
    ectl = create_free_control(ebonetop,useLoc=True)
    mctl = create_free_control(mbonetop,useLoc=True)
    if parent:
        try:
            ectl.getParent().setParent(parent)
            mctl.getParent().setParent(parent)
        except pm.MayaNodeError as why:
            log.warning(why)
        except AttributeError as why:
            log.error(why)
    rul.control_tagging(ectl, metaname='ShortHairControlsSet_MetaNode')
    rul.control_tagging(mctl, metaname='ShortHairControlsSet_MetaNode')
    rul.group([mbonetop.getParent(), ebonetop.getParent()], grpname=bonename+'_bontopGp')
    rul.group([ikcurve, ikhandle], grpname=bonename+'_ikMisc')
    rul.group([ectl.getParent(), mctl.getParent()], grpname=bonename+'_ctlGp')
    if parent:
        if pm.objExists(parent):
            ikmiscGp.setParent(parent)
        else:
            rul.group(ikmiscGp, grpname=parent)
    return (sbonetop, mbonetop, ebonetop)

def create_short_hair_simple(bone, parent='', miscParent='miscGp'):
    bones = rul.get_current_chain(bone)
    bonename = bone.name().split('|')[-1]
    startBone = bones[0]
    endBone = bones[-1]
    ikhandle, ikeffector, ikcurve = pm.ikHandle(
        sj=startBone, ee=endBone, solver='ikSplineSolver', ns=3)
    ikhandle.rename(bonename+'_ikhandle')
    ikeffector.rename(bonename+'_ikeffector')
    ikcurve.rename(bonename+'_ikCurve')
    sbonetop, ebonetop = [
        dup_bone(b,name = b.name()+'_'+suffix) for b,suffix in zip([startBone,endBone],['root','top'])]
    ectl = create_free_control(ebonetop, useLoc=True)
    # loc = ectl.outputs()[-1]
    curveSkin = pm.skinCluster(sbonetop ,ebonetop,ikcurve)
    if parent:
        try:
            ectl.getParent().setParent(parent)
            # loc.getParent().setParent(parent)
        except pm.MayaNodeError as why:
            log.warning(why)
        except AttributeError as why:
            log.error(why)
    rul.control_tagging(ectl, metaname='ShortHairControlsSet_MetaNode')
    ikmiscGp = pm.group([ikcurve, ikhandle], name=bonename+'_ikMisc')
    bonRootGp =  pm.group([sbonetop,ebonetop.getParent()], name=bonename+'_topBonGp')
    bonRootGp.setParent(bone.getParent())
    ectl.addAttr('twist', type='float', k=1)
    ectl.twist >> ikhandle.twist
    if miscParent:
        if pm.objExists(miscParent):
            ikmiscGp.setParent(miscParent)
        else:
            pm.group(ikmiscGp, name=miscParent)
    return (sbonetop, ebonetop, ectl)

# def create_sway_short_hair(bone,rootTop):
#     bones = get_current_chain(bone)
#     bonename = bone.name().split('|')[-1]
#     startBone = bones[0]
#     endBone = bones[-1]
#     midBone = bones[int(round((len(bones)-1)/2.0))]
#     ikhandle, ikeffector, ikcurve = pm.ikHandle(
#         sj=startBone, ee=endBone,solver='ikSplineSolver')
#     ikhandle.rename(bonename+'_ikhandle')
#     ikeffector.rename(bonename+'_ikeffector')
#     ikcurve.rename(bonename+'_ikCurve')
#     sbonetop, mbonetop, ebonetop = [
#         dup_bone(b,name = b.name()+'_top') for b in [startBone,midBone,endBone]]
#     print (len(bones)-1)%2.0
#     if (len(bones)-1)%2.0 == 1:
#         boneUp = bones[int(math.ceil((len(bones)-1)/2.0))]
#         boneDown = bones[int(math.floor((len(bones)-1)/2.0))]
#         mbonetop.setTranslation(
#             (boneUp.getTranslation('world')+boneDown.getTranslation('world'))/2,'world')
#     for b in [sbonetop, mbonetop, ebonetop]:
#         b.setParent(None)
#         b.radius.set(b.radius.get()*2)
#     curveSkin = pm.skinCluster(sbonetop,mbonetop,ebonetop,ikcurve)
#     if not rootTop.hasAttr('swayspeedX'):
#         pm.addAttr(
#             rootTop,
#             ln='swayspeedX', nn='Sway X Speed', sn='swayspX',
#             at='float', k=1, dv=0.75)
#     if not rootTop.hasAttr('swaystrengthX'):
#         pm.addAttr(
#             rootTop,
#             ln='swaystrengthX', nn='Sway X Strength', sn='swaystrX',
#             at='float', k=1, dv=0.25)
#     if not rootTop.hasAttr('swayfrequencyX'):
#         pm.addAttr(rootTop,
#         ln='swayfrequencyX', nn='Sway X Frequency', sn='swayfreX',
#         at='float', k=1, dv=2)
#     if not rootTop.hasAttr('swayspeedY'):
#         pm.addAttr(rootTop,
#         ln='swayspeedY', nn='Sway Y Speed', sn='swayspY',
#         at='float', k=1, dv=1)
#     if not rootTop.hasAttr('swaystrengthY'):
#         pm.addAttr(rootTop,
#         ln='swaystrengthY', nn='Sway Y Strength', sn='swaystrY',
#         at='float', k=1, dv=0.5)
#     if not rootTop.hasAttr('swayfrequencyY'):
#         pm.addAttr(rootTop,
#         ln='swayfrequencyY', nn='Sway Y Frequency', sn='swayfreY',
#         at='float', k=1, dv=1)
#     pm.select(ikcurve,r=True)
#     X = pm.nonLinear( type='sine' )
#     X[1].rename(bonename+'_sineX')
#     pm.select(ikcurve,r=True)
#     Y = pm.nonLinear( type='sine' )
#     Y[1].rename(bonename+'_sineY')
#     #Z = pm.nonLinear(type='sine')
#     for sineHandle in [X,Y]:
#         sineHandle[0].lowBound.set(0)
#         sineHandle[0].amplitude.set(0.25)
#         sineHandle[0].dropoff.set(-1)
#         sineHandle[0].wavelength.set(1.5)
#         sineHandle[1].setTranslation(sbonetop.getTranslation('world'), 'world')
#         tempAim = pm.aimConstraint(
#             ebonetop,
#             sineHandle[1],
#             aimVector=[0,1,0],
#             )
#         sineHandle[1].setParent(sbonetop)
#         sineHandle[1].scaleY.set(
#             sbonetop.getTranslation().distanceTo(ebonetop.getTranslation()))
#         tempAim.worldUpType.set(1)
#         tempAim.setWorldUpObject(mbonetop.name())
#         if sineHandle == Y:
#             tempAim.setUpVector([1,0,0])
#         else:
#             tempAim.setUpVector([0,0,1])
#     sineExpress = pm.expression(
#         s='%s.offset=time*%s*noise(time);\n%s.offset=time*%s*noise(time);'%(
#             X[0].name(),rootTop.swayspX.name(),Y[0].name(),rootTop.swayspY.name()),
#         td=True, ae=1, uc='all')
#     rootTop.swaystrX >> X[0].amplitude
#     rootTop.swayfreX >> X[0].wavelength
#     rootTop.swaystrY >> Y[0].amplitude
#     rootTop.swayfreY >> Y[0].wavelength
#     return (sbonetop, mbonetop, ebonetop)
