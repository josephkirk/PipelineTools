#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""

import general_utils as ul
import pymel.core as pm
import rig_class as rcl
import math
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
#### Rigging Control


#Project Specific Function
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
    
###Rigging Function
def get_current_chain(ob):
    boneChains = []
    while ob.getChildren():
        childsCount = len(ob.getChildren())
        assert (childsCount==1), 'Joint split to {} at {}'.format(childsCount,ob)
        boneChains.append(ob)
        ob=ob.getChildren()[0]
    else:
        boneChains.append(ob)
    return boneChains

def dup_bone(bone,**kws):
    dupbone = bone.duplicate(po=True,**kws)[0]
    dupbone.setParent(None)
    dupbone.radius.set(bone.radius.get()*2)
    return dupbone

def group(ob):
    '''group control under newTransform'''
    Gp = pm.nt.Transform(name=ob + 'Gp')
    ob.setParent(Gp)
    log.info('group {} under {}'.format(ob, Gp))
    return Gp

def createPinCircle(
        name,
        createCurve=True,
        axis='XY',
        sphere=False,
        cylinder=False,
        offset=[0, 0, 0],
        radius=1.0,
        length=3.0,
        height=2,
        step=20.0,
        maxAngle=360.0):
    '''Master function to create all curve control'''
    log.debug('''create Control with value:\n
        name: {}\n
        create Curve: {}\n
        axis: {}\n
        sphere: {}\n
        offset: {}\n
        radius: {}\n
        length: {}\n
        step: {}\n
        max Angle: {}'''.format(name, createCurve, axis, sphere, offset, radius, length, step, maxAngle))
    maxAngle = maxAngle / 180.0 * math.pi
    inc = maxAngle / step
    pointMatrix = []
    theta = 0
    if length > 0:
        pointMatrix.append([0, 0])
        pointMatrix.append([0, length])
        offset = [offset[0], -radius - length - offset[1], offset[2]]
    # print offset
    while theta <= maxAngle:
        if length > 0:
            x = (-offset[0] + radius * math.sin(theta))
            y = (offset[1] + radius * math.cos(theta)) * -1.0
        else:
            x = (offset[0] + radius * math.cos(theta))
            y = (offset[1] + radius * math.sin(theta))
        pointMatrix.append([x, y])
        # print "theta angle {} produce [{},{}]".format(round(theta,2),round(x,4),round(y,4))
        theta += inc
    if not createCurve:
        return pointMatrix
    axisData = {}
    axisData['XY'] = [[x, y, offset[2]] for x, y in pointMatrix]
    axisData['YX'] = [[y, x, offset[2]] for x, y in pointMatrix]
    axisData['-XY'] = [[-x, -y, offset[2]] for x, y in pointMatrix]
    axisData['-YX'] = [[-y, -x, offset[2]] for x, y in pointMatrix]
    axisData['XZ'] = [[x, offset[2], y] for x, y in pointMatrix]
    axisData['ZX'] = [[y, offset[2], x] for x, y in pointMatrix]
    axisData['-XZ'] = [[-x, offset[2], -y] for x, y in pointMatrix]
    axisData['-ZX'] = [[-y, offset[2], -x] for x, y in pointMatrix]
    axisData['YZ'] = [[offset[2], x, y] for x, y in pointMatrix]
    axisData['ZY'] = [[offset[2], y, x] for x, y in pointMatrix]
    axisData['-YZ'] = [[offset[2], -x, -y] for x, y in pointMatrix]
    axisData['-ZY'] = [[offset[2], -y, -x] for x, y in pointMatrix]
    axisData['mXY'] = axisData['XY'] + axisData['-XY']
    axisData['mYX'] = axisData['YX'] + axisData['-YX']
    axisData['mXZ'] = axisData['XZ'] + axisData['-XZ']
    axisData['mZX'] = axisData['ZX'] + axisData['-ZX']
    axisData['mYZ'] = axisData['YZ'] + axisData['-YZ']
    axisData['mZY'] = axisData['ZY'] + axisData['-ZY']
    axisData['all'] = axisData['XY'] + axisData['XZ'] + axisData['ZX'] + axisData['-XY'] + axisData['-XZ'] + \
                        axisData['-ZX']
    newname = name
    try:
        assert (axisData.has_key(axis)), "Wrong Axis '%s'.\nAvailable axis: %s" % (axis, ','.join(axisData))
        finalPointMatrix = axisData[axis]
    except AssertionError as why:
        finalPointMatrix = axisData['XY']
        log.error(str(why) + '\nDefault to XY')
    if sphere and not cylinder and not length > 0:
        quarCircle = len(pointMatrix) / 4 + 1
        finalPointMatrix = axisData['XY'] + axisData['XZ'] + axisData['XY'][:quarCircle] + axisData['YZ']
    elif sphere and not cylinder and length > 0:
        if axis[-1] == 'X':
            finalPointMatrix = axisData['YX'] + axisData['ZX']
        elif axis[-1] == 'Y':
            finalPointMatrix = axisData['XY'] + axisData['ZY']
        elif axis[-1] == 'Z':
            finalPointMatrix = axisData['XZ'] + axisData['YZ']
    elif cylinder and not sphere and not length > 0:
        newpMatrix = []
        pMatrix = pointMatrix
        newpMatrix.extend([[x, 0, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1]])
        newpMatrix.extend([[x, height, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1][::-1]])
        newpMatrix.extend([[x, 0, y] for x, y in pMatrix[::-1][:len(pMatrix) / 2 + 1]])
        newpMatrix.extend([[x, height, y] for x, y in pMatrix[::-1][len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
        newpMatrix.extend([[x, 0, y] for x, y in pMatrix[len(pMatrix) / 4:len(pMatrix) / 2 + 1]])
        newpMatrix.extend([[x, height, y] for x, y in pMatrix[len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
        newpMatrix.append([newpMatrix[-1][0], 0, newpMatrix[-1][2]])
        newpMatrix.extend([[x, height, y] for x, y in pMatrix[-len(pMatrix) / 4:]])
        finalPointMatrix = newpMatrix
    key = range(len(finalPointMatrix))
    crv = pm.curve(name=newname, d=1, p=finalPointMatrix, k=key)
    log.debug(crv)
    return crv

@ul.do_function_on('singlelast')
def contraint_multi(ob,target, constraintType='Point'):
    constraintDict = {
        'Point': ul.partial(pm.pointConstraint , mo=True),
        'Parent': ul.partial(pm.parentConstraint , mo=True),
        'Orient': ul.partial(pm.orientConstraint , mo=True),
        'Aim': ul.partial(pm.orientConstraint , mo=True)
    }
    assert (constraintDict.has_key(constraintType)), 'wrong Constraint Type'
    constraintDict[constraintType](target,ob)

@ul.do_function_on('double')
def connect_visibility(ob, target, attrname='Vis'):
    pm.addAttr(ob, ln=attrname,at='bool',k=1)
    ob.attr(attrname) >> target.visibility

@ul.do_function_on()
def create_short_hair_simple(bone):
    bones = get_current_chain(bone)
    bonename = bone.name().split('|')[-1]
    startBone = bones[0]
    endBone = bones[-1]
    midBone = bones[int(round((len(bones)-1)/2.0))]
    ikhandle, ikeffector, ikcurve = pm.ikHandle(sj=startBone, ee=endBone,solver='ikSplineSolver')
    ikhandle.rename(bonename+'_ikhandle')
    ikeffector.rename(bonename+'_ikeffector')
    ikcurve.rename(bonename+'_ikCurve')
    sbonetop, mbonetop, ebonetop = [dup_bone(b,name = b.name()+'_top') for b in [startBone,midBone,endBone]]
    print (len(bones)-1)%2.0
    if (len(bones)-1)%2.0 == 1:
        boneUp = bones[int(math.ceil((len(bones)-1)/2.0))]
        boneDown = bones[int(math.floor((len(bones)-1)/2.0))]
        mbonetop.setTranslation((boneUp.getTranslation('world')+boneDown.getTranslation('world'))/2,'world')
    for b in [sbonetop, mbonetop, ebonetop]:
        b.setParent(None)
        b.radius.set(b.radius.get()*2)
    curveSkin = pm.skinCluster(sbonetop,mbonetop,ebonetop,ikcurve)
    return (sbonetop, mbonetop, ebonetop)

@ul.do_function_on()
def create_short_hair_single(bone):
    bones = get_current_chain(bone)
    bonename = bone.name().split('|')[-1]
    startBone = bones[0]
    endBone = bones[-1]
    ikhandle, ikeffector, ikcurve = pm.ikHandle(sj=startBone, ee=endBone,solver='ikSplineSolver')
    ikhandle.rename(bonename+'_ikhandle')
    ikeffector.rename(bonename+'_ikeffector')
    ikcurve.rename(bonename+'_ikCurve')
    sbonetop, ebonetop = [dup_bone(b,name = b.name()+'_top') for b in [startBone,endBone]]
    for b in [sbonetop, ebonetop]:
        b.radius.set(b.radius.get()*2)
    curveSkin = pm.skinCluster(sbonetop ,ebonetop,ikcurve)
    return (sbonetop, ebonetop)

@ul.do_function_on(mode='singlelast')
def create_short_hair(bone,rootTop):
    bones = get_current_chain(bone)
    bonename = bone.name().split('|')[-1]
    startBone = bones[0]
    endBone = bones[-1]
    midBone = bones[int(round((len(bones)-1)/2.0))]
    ikhandle, ikeffector, ikcurve = pm.ikHandle(sj=startBone, ee=endBone,solver='ikSplineSolver')
    ikhandle.rename(bonename+'_ikhandle')
    ikeffector.rename(bonename+'_ikeffector')
    ikcurve.rename(bonename+'_ikCurve')
    sbonetop, mbonetop, ebonetop = [dup_bone(b,name = b.name()+'_top') for b in [startBone,midBone,endBone]]
    print (len(bones)-1)%2.0
    if (len(bones)-1)%2.0 == 1:
        boneUp = bones[int(math.ceil((len(bones)-1)/2.0))]
        boneDown = bones[int(math.floor((len(bones)-1)/2.0))]
        mbonetop.setTranslation((boneUp.getTranslation('world')+boneDown.getTranslation('world'))/2,'world')
    for b in [sbonetop, mbonetop, ebonetop]:
        b.setParent(None)
        b.radius.set(b.radius.get()*2)
    curveSkin = pm.skinCluster(sbonetop,mbonetop,ebonetop,ikcurve)
    if not rootTop.hasAttr('swayspeedX'):
        pm.addAttr(rootTop, ln='swayspeedX', nn='Sway X Speed', sn='swayspX', at='float', k=1, dv=0.75)
    if not rootTop.hasAttr('swaystrengthX'):
        pm.addAttr(rootTop, ln='swaystrengthX', nn='Sway X Strength', sn='swaystrX', at='float', k=1, dv=0.25)
    if not rootTop.hasAttr('swayfrequencyX'):
        pm.addAttr(rootTop, ln='swayfrequencyX', nn='Sway X Frequency', sn='swayfreX', at='float', k=1, dv=2)
    if not rootTop.hasAttr('swayspeedY'):
        pm.addAttr(rootTop, ln='swayspeedY', nn='Sway Y Speed', sn='swayspY', at='float', k=1, dv=1)
    if not rootTop.hasAttr('swaystrengthY'):
        pm.addAttr(rootTop, ln='swaystrengthY', nn='Sway Y Strength', sn='swaystrY', at='float', k=1, dv=0.5)
    if not rootTop.hasAttr('swayfrequencyY'):
        pm.addAttr(rootTop, ln='swayfrequencyY', nn='Sway Y Frequency', sn='swayfreY', at='float', k=1, dv=1)
    pm.select(ikcurve,r=True)
    X = pm.nonLinear( type='sine' )
    X[1].rename(bonename+'_sineX')
    pm.select(ikcurve,r=True)
    Y = pm.nonLinear( type='sine' )
    Y[1].rename(bonename+'_sineY')
    #Z = pm.nonLinear(type='sine')
    for sineHandle in [X,Y]:
        sineHandle[0].lowBound.set(0)
        sineHandle[0].amplitude.set(0.25)
        sineHandle[0].dropoff.set(-1)
        sineHandle[0].wavelength.set(1.5)
        sineHandle[1].setTranslation(sbonetop.getTranslation('world'), 'world')
        tempAim = pm.aimConstraint(
            ebonetop,
            sineHandle[1],
            aimVector=[0,1,0],
            )
        sineHandle[1].setParent(sbonetop)
        sineHandle[1].scaleY.set(sbonetop.getTranslation().distanceTo(ebonetop.getTranslation()))
        tempAim.worldUpType.set(1)
        tempAim.setWorldUpObject(mbonetop.name())
        if sineHandle == Y:
            tempAim.setUpVector([1,0,0])
        else:
            tempAim.setUpVector([0,0,1])
    sineExpress = pm.expression(
        s='%s.offset=time*%s*noise(time);\n%s.offset=time*%s*noise(time);'%(
            X[0].name(),rootTop.swayspX.name(),Y[0].name(),rootTop.swayspY.name()),
        td=True, ae=1, uc='all')
    rootTop.swaystrX >> X[0].amplitude
    rootTop.swayfreX >> X[0].wavelength
    rootTop.swaystrY >> Y[0].amplitude
    rootTop.swayfreY >> Y[0].wavelength
    return (sbonetop, mbonetop, ebonetop)

@ul.do_function_on()
def createOffsetJoint(jointRoot, child=False, suffix='offset_bon'):
    jointlist = [jointRoot]
    if child:
        jointlist.extend(jointRoot.getChildren(allDescendents=True))
    for joint in jointlist:
        newname = joint.name().split('|')[-1].split('_')[0] + '_' + suffix
        offsetJoint = pm.duplicate(joint, name=newname, po=True)[0]
        offsetJoint.drawStyle.set(2)
        oldParent = joint.getParent()
        # pm.parent(offsetJoint, oldParent)
        joint.setParent(offsetJoint)
        # pm.makeIdentity(joint,apply=True)
        # yield offsetJoint

@ul.do_function_on()
def create_loc_control(ob, connect=True):
    obname = ob.name().split('|')[-1].split('_')[0]
    loc = pm.spaceLocator(name=obname + 'loc')
    loc.setTranslation(ob.getTranslation('world'), 'world')
    loc.setRotation(ob.getRotation('world'), 'world')
    loc_Gp = create_parent(loc,cl=True)
    if connect:
        attrdict = {
            'translate': ['tx', 'ty', 'tz'],
            'rotate': ['rx', 'ry', 'rz'],
            'scale': ['sx', 'sy', 'sz']
        }
        for atr, value in attrdict.items():
            loc.attr(atr) >> ob.attr(atr)
            for attr in value:
                loc.attr(attr) >> ob.attr(attr)
    return loc

@ul.do_function_on(mode='double')
def connect_with_loc(ctl,bon):
    loc = create_loc_control(bon,cl=True)
    pct = pm.pointConstraint(ctl, loc)
    oct = pm.orientConstraint(ctl, loc)
    return (loc,pct,oct)

@ul.do_function_on()
def create_loc_on_vert(vert):
    if isinstance(vert,pm.general.MeshVertex):
        tarPos = vert.getPosition('world')
        tarMesh = vert.node()
        temp = pm.spaceLocator()
        fg = rcl.FacialGuide(temp.name())
        pm.delete(temp)
        fg.set_guide_mesh(tarMesh)
        fg.create(pos=tarPos)
        fg.set_constraint()

@ul.do_function_on()
def create_parent(ob):
    obname = ob.name().split('|')[-1].split('_')[0] + '_' + ob.name().split('_')[-1]
    parent = pm.nt.Transform(name=obname + 'Gp')
    oldParent = ob.getParent()
    parent.setTranslation(ob.getTranslation('world'), 'world')
    parent.setRotation(ob.getRotation('world'), 'world')
    parent.setParent(oldParent)
    ob.setParent(parent)
    return parent


@ul.do_function_on()
def remove_parent(ob):
    parent = ob.getParent()
    grandParent = parent.getParent()
    ob.setParent(grandParent)
    pm.delete(parent)


@ul.do_function_on('double')
def xformTo(ob, joint):
    const = pm.parentConstraint(joint, ob)
    pm.delete(const)


@ul.do_function_on('double')
def matchTransform(ob, target):
    ob.setMatrix(target.getMatrix(ws=True), ws=True)


@ul.do_function_on('double')
def connectTransform(ob, target, **kws):
    for atr in ['translate','rotate','scale']:
        if atr not in kws:
            kws[atr] = True
    attrdict = {
        'translate': ['tx', 'ty', 'tz'],
        'rotate': ['rx', 'ry', 'rz'],
        'scale': ['sx', 'sy', 'sz']
    }
    for atr, value in attrdict.items():
        if atr in kws:
            if kws[atr] is False:
                continue
            if 'disconnect' in kws:
                if kws['disconnect']:
                    ob.attr(atr) // target.attr(atr)
                    for attr in value:
                        ob.attr(attr) // target.attr(attr)
                    continue
            ob.attr(atr) >> target.attr(atr)
            for attr in value:
                ob.attr(attr) >> target.attr(attr)

#@ul.do_function_on(mode='set')
def toggleChannelHistory():
    if not pm.selected():
        oblist = pm.ls()
    else:
        oblist = pm.selected()
    for ob in oblist:
        state = ob.isHistoricallyInteresting.get()
        ob.isHistoricallyInteresting.set(not state  )


def deform_normal_off():
    skin_clusters = pm.ls(type='skinCluster')
    if not skin_clusters:
        return
    for skin_cluster in skin_clusters:
        skin_cluster.attr('deformUserNormals').set(False)
        print skin_cluster
        print skin_cluster.attr('deformUserNormals').get()


@ul.do_function_on('single')
def mirror_joint_multi(ob):
    pm.mirrorJoint(ob, myz=True, sr=('Left', 'Right'))


def get_blendshape_target(
        bsname,
        reset_value=False,
        rebuild=False,
        delete_old=True,
        parent=None,
        offset=0,
        exclude=[], exclude_last=False):
    """get blendShape in scene match bsname 
        misc function:
            bsname : blendShape name or id to search for 
            reset_value : reset all blendShape weight Value 
            rebuild: rebuild all Target
            parent: group all rebuild target under parent
            offset: offset rebuild target in X axis
            exclude: list of exclude blendShape target to rebuild and reset
            exclude_last: exclude the last blendShape target from rebuild and reset"""
    bs_list = pm.ls(type='blendShape')
    if not bs_list:
        return
    if isinstance(bsname, int):
        blendshape = bs_list[bsname]
    else:
        blendshape = pm.PyNode(bsname)
    if blendshape is None:
        return
    target_list = []
    pm.select(cl=True)
    for id, target in enumerate(blendshape.weight):
        target_name = pm.aliasAttr(target, q=True)
        if reset_value is True or rebuild is True:
            if target_name not in exclude:
                target.set(0)
        target_weight = target.get()
        target_list.append((target, target_name, target_weight))
    # print target_list
    if rebuild is True:
        base_ob_node = blendshape.getBaseObjects()[0].getParent().getParent()
        print base_ob_node
        base_ob_name = base_ob_node.name()
        blendshape_name = blendshape.name()
        iter = 1
        target_rebuild_list = []
        if parent != None and type(parent) is str:
            if pm.objExists(parent):
                pm.delete(pm.PyNode(parent))
            parent = pm.group(name=parent)
        if exclude_last is True:
            target_list[-1][0].set(1)
            target_list = target_list[:-1]
        base_dup = pm.duplicate(base_ob_node, name=base_ob_name + "_rebuild")
        for target in target_list:
            if target[1] not in exclude:
                target[0].set(1)
                new_target = pm.duplicate(base_ob_node)
                target_rebuild_list.append(new_target)
                pm.parent(new_target, parent)
                pm.rename(new_target, target[1])
                target[0].set(0)
                pm.move(offset * iter, new_target, moveX=True)
                iter += 1
        pm.select(target_rebuild_list, r=True)
        pm.select(base_dup, add=True)
        pm.blendShape()
        blend_reget = get_blendshape_target(blendshape_name)
        blendshape = blend_reget[0]
        target_list = blend_reget[1]
    return (blendshape, target_list)


@ul.do_function_on(mode='singlelast')
def skin_weight_filter(ob, joint, min=0.0, max=0.1, select=False):
    '''return vertex with weight less than theshold'''
    skin_cluster = ul.get_skin_cluster(ob)
    ob_shape = ul.get_shape(ob)
    filter_weight = []
    for vtx in ob_shape.vtx:
        weight = pm.skinPercent(skin_cluster, vtx, query=True, transform=joint, transformValue=True)
        # print weight
        if min < weight <= max:
            filter_weight.append(vtx)
    if select:
        pm.select(filter_weight)
    return filter_weight


@ul.do_function_on(mode='single')
def switch_skin_type(ob, type='classis'):
    type_dict = {
        'Classis': 0,
        'Dual': 1,
        'Blend': 2}
    if not ul.get_skin_cluster(ob) and type not in type_dict.keys():
        return
    skin_cluster = ul.get_skin_cluster(ob)
    skin_cluster.setSkinMethod(type_dict[type])
    deform_normal_state = 0 if type_dict[type] is 2 else 1
    skin_cluster.attr('deformUserNormals').set(deform_normal_state)


@ul.do_function_on(mode='doubleType', type_filter=['float3', 'transform', 'joint'])
def skin_weight_setter(component_list, joints_list, skin_value=1.0, normalized=True, hierachy=False):
    '''set skin weight to skin_value for vert in verts_list to first joint,
       other joint will receive average from normalized weight,
       can be use to set Dual Quarternion Weight'''

    def get_skin_weight():
        skin_weight = []
        if normalized:
            skin_weight.append((joints_list[0], skin_value))
            if len(joints_list) > 1:
                skin_normalized = (1.0 - skin_value) / (len(joints_list) - 1)
                for joint in joints_list[1:]:
                    skin_weight.append((joint, skin_normalized))
            return skin_weight
        for joint in joints_list:
            skin_weight.append((joint, skin_value))
        return skin_weight

    if hierachy:
        child_joint = joints_list[0].listRelatives(allDescendents=True)
        joints_list.extend(child_joint)
        print joints_list

    if any([type(component) is pm.nt.Transform for component in component_list]):
        for component in component_list:
            skin_cluster = ul.get_skin_cluster(component)
            pm.select(component, r=True)
            pm.skinPercent(skin_cluster, transformValue=get_skin_weight())
            print component_list
        pm.select(component_list, joints_list)
    else:
        verts_list = ul.convert_component(component_list)
        skin_cluster = ul.get_skin_cluster(verts_list[0])
        if all([skin_cluster, verts_list, joints_list]):
            pm.select(verts_list)
            pm.skinPercent(skin_cluster, transformValue=get_skin_weight())
            pm.select(joints_list, add=True)
            # print verts_list
            # print skin_weight
            # skin_cluster.setWeights(joints_list,[skin])


@ul.do_function_on(mode='sets', type_filter=['float3'])
def dual_weight_setter(component_list, weight_value=0.0, query=False):
    verts_list = ul.convert_component(component_list)
    shape = verts_list[0].node()
    skin_cluster = ul.get_skin_cluster(verts_list[0])
    if query:
        weight_list = []
        for vert in verts_list:
            for vert in vert.indices():
                weight = skin_cluster.getBlendWeights(shape, shape.vtx[vert])
                weight_list.append((shape.vtx[vert], weight))
        return weight_list
    else:
        for vert in verts_list:
            for vert in vert.indices():
                skin_cluster.setBlendWeights(shape, shape.vtx[vert], [weight_value, weight_value])
                #     print skin_cluster.getBlendWeights(shape, vert)
                # pm.select(verts_list)
                # skin_cluster.setBlendWeights(shape, verts_list, [weight_value,])


@ul.do_function_on(mode='single', type_filter=['float3', 'transform'])
def create_joint(ob_list):
    new_joints = []
    for ob in ob_list:
        if type(ob) == pm.nt.Transform:
            get_pos = ob.translate.get()
        elif type(ob) == pm.general.MeshVertex:
            get_pos = ob.getPosition(space='world')
        elif type(ob) == pm.general.MeshEdge:
            get_pos = ul.get_pos_center_from_edges(ob)
        new_joint = pm.joint(p=get_pos)
        new_joints.append(new_joint)
    for new_joint in new_joints:
        pm.joint(new_joint, edit=True, oj='xyz', sao='yup', ch=True, zso=True)
        if new_joint == new_joints[-1]:
            pm.joint(new_joint, edit=True, oj='none', ch=True, zso=True)


@ul.error_alert
@ul.do_function_on(mode='single')
def insert_joint(joint, num_joint=2):
    og_joint = joint
    joint_child = joint.getChildren()[0] if joint.getChildren() else None
    joint_child.orientJoint('none')
    joint_name = ul.remove_number(joint.name())
    if joint_child:
        distance = joint_child.tx.get() / (num_joint + 1)
        while num_joint:
            insert_joint = pm.insertJoint(joint)
            pm.joint(insert_joint, edit=True, co=True, ch=False, p=[distance, 0, 0], r=True)
            joint = insert_joint
            num_joint -= 1
        joint_list = og_joint.listRelatives(type='joint', ad=1)
        joint_list.reverse()
        joint_list.insert(0, og_joint)
        for index, bone in enumerate(joint_list):
            try:
                pm.rename(bone, "%s%02d" % (joint_name[0], index + 1))
            except:
                pm.rename(bone, "%s#" % joint_name[0])


@ul.do_function_on(mode='double')
def snap_simple(ob1, ob2, worldspace=False, hierachy=False, preserve_child=False):
    '''snap Transform for 2 object'''
    ob1_childs = ob1.listRelatives(type=['joint', 'transform'], ad=1)
    if hierachy:
        ob1_childs.append(ob1)
        ob2_childs = ob2.listRelatives(type=['joint', 'transform'], ad=1)
        ob2_childs.append(ob2)
        for ob1_child, ob2_child in zip(ob1_childs, ob2_childs):
            ob1_child.setMatrix(ob2_child.getMatrix(ws=worldspace), ws=worldspace)
    else:
        ob1_child_old_matrixes = [ob_child.getMatrix(ws=True)
                                  for ob_child in ob1_childs]
        ob1.setMatrix(ob2.getMatrix(ws=worldspace), ws=worldspace)
        if preserve_child:
            for ob1_child, ob1_child_old_matrix in zip(ob1_childs, ob1_child_old_matrixes):
                ob1_child.setMatrix(ob1_child_old_matrix, ws=True)


# pm.copySkinWeights(ss=skin.name(), ds=dest_skin.name(),
#                    noMirror=True, normalize=True,
#                    surfaceAssociation='closestPoint',
#                    influenceAssociation='closestJoint')
# dest_skin.setSkinMethod(skin.getSkinMethod())
@ul.do_function_on(mode='double')
def copy_skin_multi(source_skin_grp, dest_skin_grp, **kwargs):
    '''copy skin for 2 identical group hierachy'''
    source_skins = source_skin_grp.listRelatives(type='transform', ad=1)
    dest_skins = dest_skin_grp.listRelatives(type='transform', ad=1)
    if len(dest_skins) == len(source_skins):
        print '---{}---'.format('Copying skin from %s to %s' % (source_skin_grp, dest_skin_grp))
        for skinTR, dest_skinTR in zip(source_skins, dest_skins):
            copy_skin_single(skinTR, dest_skinTR, **kwargs)
        print '---Copy Skin Finish---'
    else:
        print 'source and target are not the same'


@ul.error_alert
def copy_skin_single(source_skin, dest_skin, **kwargs):
    '''copy skin for 2 object, target object do not need to have skin Cluster'''
    ### keyword add
    kwargs['nm'] = True
    kwargs['nr'] = True
    kwargs['sm'] = True
    kwargs['sa'] = 'closestPoint'
    kwargs['ia'] = ['closestJoint', 'label']
    addskin = kwargs['addskin'] if kwargs.has_key('addskin') else True
    try:
        skin = ul.get_skin_cluster(source_skin)
        kwargs['ss'] = skin.name()
        if not skin:
            raise AttributeError()
        skin_joints = skin.getInfluence()
        print source_skin, 'connected to', skin
        print source_skin, 'influenced by', skin_joints
        skin_dest = ul.get_skin_cluster(dest_skin)
        if not skin_dest:
            dest_skin_joints = []
            for bone in skin_joints:
                label_joint(bone)
                found_bones = pm.ls(bone.otherType.get(), type='joint')
                if len(found_bones) > 1:
                    for found_bone in found_bones:
                        if found_bone != bone:
                            dest_skin_joints.append(found_bone)
                            break
            dest_skin_joints.append(dest_skin)
            skin_dest = pm.skinCluster(*dest_skin_joints, tsb=True)
            dest_skin_joints = dest_skin_joints[:-1]
        else:
            dest_skin_joints = skin_dest.getInfluence()
        print dest_skin, 'connected to', skin_dest
        print dest_skin, 'influenced by', dest_skin_joints
        kwargs['ds'] = skin_dest.name()
        # pm.copySkinWeights(**kwargs)
        # skin_dest.setSkinMethod(skin.getSkinMethod())
        print '{} successfully copy to {}'.format(source_skin, skin_dest), '\n', "_" * 30
    except AttributeError:
        print '%s cannot copy skin to %s' % (source_skin.name(), dest_skin.name())
        print "-" * 30
        for ob in [source_skin, dest_skin]:
            print '{:_>20} connect to skinCluster: {}'.format(ob, ul.get_skin_cluster(ob))
        print "_" * 30


@ul.do_function_on(mode='last')
def connect_joint(bones, boneRoot, **kwargs):
    for bone in bones:
        pm.connectJoint(bone, boneRoot, **kwargs)


@ul.error_alert
@ul.do_function_on(mode='hierachy')
def label_joint(
        ob,
        remove_prefixes=['CH_'],
        direction_label={
            'Left': (1, ['left', 'Left', 'L_', '_L']),
            'Right': (2, ['right', 'Right', 'R_', '_R'])}):
    try:
        ob.attr('type').set(18)
        wildcard = ''
        sideid = 0
        for dir, (side_id, name_wc) in direction_label.items():
            for wc in name_wc:
                print wc, ob.name()
                if wc in ob.name():
                    wildcard = wc
                    sideid = side_id
                    break
            if wildcard:
                break
        print wildcard
        label_name = ob.name().replace(wildcard, '')
        if '|' in label_name:
            label_name = label_name.split('|')[-1]
        if remove_prefixes:
            for prefix in remove_prefixes:
                label_name = label_name.replace(prefix, '')
        ob.otherType.set(label_name)
        ob.side.set(sideid)
        print 'set {} joint label to {}'.format(ob, label_name)
    except AttributeError as why:
        print ob, why


@ul.do_function_on(mode='single')
def create_roll_joint(oldJoint):
    newJoint = pm.duplicate(oldJoint, rr=1, po=1)[0]
    pm.rename(newJoint, ('%sRoll1' % oldJoint.name()).replace('Left', 'LeafLeft'))
    newJoint.attr('radius').set(2)
    pm.parent(newJoint, oldJoint)
    return newJoint


@ul.do_function_on(mode='single')
def create_sub_joint(ob):
    subJoint = pm.duplicate(ob, name='%sSub' % ob.name(), rr=1, po=1, )[0]
    new_pairBlend = pm.createNode('pairBlend')
    subJoint.radius.set(2.0)
    pm.rename(new_pairBlend, '%sPairBlend' % ob.name())
    new_pairBlend.attr('weight').set(0.5)
    ob.rotate >> new_pairBlend.inRotate2
    new_pairBlend.outRotate >> subJoint.rotate
    return (ob, new_pairBlend, subJoint)


@ul.do_function_on(mode='single')
def reset_attr_value(ob):
    attr_exclude_list = [
        "translateX", "translateY", "translateZ",
        "rotateX", "rotateY", "rotateZ",
        "scaleX", "scaleY", "scaleZ",
        "visibility"
    ]
    attr_list = ob.listattr()
    for at in attrList[:-1]:
        bone.attr(at).set(0)


@ul.do_function_on(mode='single')
def create_skinDeform(ob):
    dupOb = pm.duplicate(ob, name="_".join([ob.name(), "skinDeform"]))
    for child in dupOb[0].listRelatives(ad=True):
        ul.add_suffix(child)


@ul.do_function_on(mode='single')
def mirror_joint_tranform(bone, translate=False, rotate=True, **kwargs):
    # print bone
    opbone = get_opposite_joint(bone, customPrefix=(kwargs['customPrefix'] if kwargs.has_key('customPrefix') else None))
    offset = 1
    if not opbone:
        opbone = bone
        offset = -1
        translate = False
    if all([type(b) == pm.nt.Joint for b in [bone, opbone]]):
        if rotate:
            pm.joint(opbone, edit=True, ax=pm.joint(bone, q=True, ax=True),
                     ay=pm.joint(bone, q=True, ay=True) * offset,
                     az=pm.joint(bone, q=True, az=True) * offset)
        if translate:
            bPos = pm.joint(bone, q=True, p=True)
            pm.joint(opbone, edit=True, p=(bPos[0] * -1, bPos[1], bPos[2]),
                     ch=kwargs['ch'] if kwargs.has_key('ch') else False,
                     co=not kwargs['ch'] if kwargs.has_key('ch') else True)


# @ul.do_function_on
def get_opposite_joint(bone, select=False, opBoneOnly=True, customPrefix=None):
    "get opposite Bone"
    mirrorPrefixes_list = [
        ('Left', 'Right'),
        ('_L_', '_R_')
    ]
    try:
        if all(customPrefix, type(customPrefix) == tuple, len(customPrefix) == 2):
            mirrorPrefixes_list.append(customPrefix)
    except:
        pass
    for mirrorprefix in mirrorPrefixes_list:
        for index, mp in enumerate(mirrorprefix):
            if mp in bone.name():
                opBoneName = bone.name().replace(mirrorprefix[index], mirrorprefix[index - 1])
                opBone = pm.ls(opBoneName)[0] if pm.ls(opBoneName) else None
                if select:
                    if opBoneOnly:
                        pm.select(opBone)
                    else:
                        pm.select(bone, opBone)
                print opBoneName
                return opBone


@ul.do_function_on('single')
def reset_bindPose(joint_root):
    joint_childs = joint_root.listRelatives(type=pm.nt.Joint, ad=True)
    for joint in joint_childs:
        if joint.rotate.get() != pm.dt.Vector(0, 0, 0):
            # print type(joint.rotate.get())
            joint.jointOrient.set(joint.rotate.get())
            joint.rotate.set(pm.dt.Vector(0, 0, 0))
    newbp = pm.dagPose(bp=True, save=True)
    bindPoses = pm.ls(type=pm.nt.DagPose)
    for bp in bindPoses:
        if bp != newbp:
            pm.delete(bp)
    print "All bindPose has been reseted to %s" % newbp
    return newbp
