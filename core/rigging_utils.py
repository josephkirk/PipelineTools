#!/usr/bin/env python
# -*- coding: utf-8 -*-

import general_utils as ul
import pymel.core as pm
import math
from string import ascii_uppercase as alphabet
from itertools import product
import logging
import copy
import maya.mel as mm
from ..packages.Red9.core import Red9_Meta as meta

# Logging initialize #

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Rigging MetaData Functions #

def as_meta(ob):
    if hasattr(ob, 'name'):
        return meta.MetaClass(ob.name())

def get_controller_metanode(metaname='ControllersMeta'):
    if pm.ls(metaname):
        controlmeta = meta.MetaClass(metaname)
    else:
        controlmeta = meta.MetaClass(name=metaname)
    return controlmeta

def select_controller_metanode(metaname='ControllersMeta'):
    if pm.ls(metaname):
        pm.select(metaname)
    else:
        log.error('No controller metaNode exists')

@ul.do_function_on()
def control_tagging(ob, metaname='ControllersMeta', remove=False):
    controlmeta = get_controller_metanode(metaname)
    if ob.name() not in controlmeta.getChildren() and not remove:
        if ob.inputs(type='network'):
            control_tagging(
                ob,
                metaname=ob.inputs(type='network')[0].name(),
                remove=True)
        controlmeta.connectChildren(ob.name(), attr='controls',srcSimple=True)
    else:
        if remove:
            controlmeta.disconnectChild(ob.name(), deleteDestPlug=True)
    return controlmeta

def remove_all_control_tags(metaname='ControllersMeta', select=False):
    if pm.ls(metaname):
        controlmeta = meta.MetaClass(metaname)
        controls = controlmeta.getChildren()
        if select:
            pm.select(controls)
            return controls
        for control in controls:
            controlmeta.disconnectChild(control, deleteDestPlug=True)
        return controls

def reset_controller_transform():
    controlmeta = get_controller_metanode()
    controllers = controlmeta.getChildren()
    for controller in controllers:
        ul.reset_transform(pm.PyNode(controller))

# Rigging Utilities Function #
# --- Utilities ---

def toggleChannelHistory(state=True):
    oblist = pm.ls()
    for ob in oblist:
        ob.isHistoricallyInteresting.set(state)
        log.info('{} Channel History Display Set To {}'.format(ob,state))

# @ul.do_function_on()
def group(ob, grpname='', *args):
    '''group control under newTransform'''
    obs = ul.recurse_collect([ob, args])
    # obs = [pm.PyNode(o) for o in obs if pm.objExists(o)]
    if not grpname:
        grpname = obs[0].name() + 'Gp'
    Gp = pm.nt.Transform(name=grpname)
    for ob in obs:
        ob.setParent(Gp)
        log.info('group {} under {}'.format(ob, Gp))
    return Gp

@ul.do_function_on()
def create_parent(ob):
    obname = ob.name().split('|')[-1]
    parent = pm.nt.Transform(name=obname + 'Gp')
    oldParent = ob.getParent()
    # parent.setTranslation(ob.getTranslation('world'), 'world')
    # parent.setRotation(ob.getRotation('world'), 'world')
    xformTo(parent, ob)
    parent.setParent(oldParent)
    ob.setParent(parent)
    log.info('create Parent Transform %s'%parent)
    return parent

@ul.do_function_on()
def remove_parent(ob):
    parent = ob.getParent()
    grandParent = parent.getParent()
    ob.setParent(grandParent)
    log.info('delete %s'%parent)
    pm.delete(parent)
    return grandParent

def create_square(
        name,
        width=1,
        length=1,
        offset=[0, 0, 0]):
    xMax = width/2
    yMax = length/2
    pointMatrix = [
        [ xMax,0, yMax ],
        [ xMax,0, -yMax ],
        [ -xMax,0, -yMax ],
        [ -xMax,0, yMax ],
        [  xMax,0, yMax ]
    ]
    key = range(len(pointMatrix))
    crv = pm.curve(name=name, d=1, p=pointMatrix, k=key)
    log.debug(crv)
    return crv

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

    while theta <= maxAngle:
        if length > 0:
            x = (-offset[0] + radius * math.sin(theta))
            y = (offset[1] + radius * math.cos(theta)) * -1.0
        else:
            x = (offset[0] + radius * math.cos(theta))
            y = (offset[1] + radius * math.sin(theta))
        pointMatrix.append([x, y])

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
    axisData['all'] = axisData['XY'] + axisData['XZ'] + \
                      axisData['ZX'] + axisData['-XY'] + \
                      axisData['-XZ'] + axisData['-ZX']
    newname = name
    try:
        assert (axisData.has_key(axis)), \
            "Wrong Axis '%s'.\nAvailable axis: %s" % (axis, ','.join(axisData))
        finalPointMatrix = axisData[axis]
    except AssertionError as why:
        finalPointMatrix = axisData['XY']
        log.error(str(why) + '\nDefault to XY')
    if sphere and not cylinder and not length > 0:
        quarCircle = len(pointMatrix) / 4 + 1
        finalPointMatrix = axisData['XY'] + axisData['XZ'] + \
                           axisData['XY'][:quarCircle] + axisData['YZ']
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
        newpMatrix.extend(
            [[x, 0, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[:len(pMatrix) / 4 + 1][::-1]])
        newpMatrix.extend(
            [[x, 0, y] for x, y in pMatrix[::-1][:len(pMatrix) / 2 + 1]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[::-1][len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
        newpMatrix.extend(
            [[x, 0, y] for x, y in pMatrix[len(pMatrix) / 4:len(pMatrix) / 2 + 1]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[len(pMatrix) / 2:-len(pMatrix) / 4 + 1]])
        newpMatrix.append(
            [newpMatrix[-1][0], 0, newpMatrix[-1][2]])
        newpMatrix.extend(
            [[x, height, y] for x, y in pMatrix[-len(pMatrix) / 4:]])
        finalPointMatrix = newpMatrix
    key = range(len(finalPointMatrix))
    crv = pm.curve(name=newname, d=1, p=finalPointMatrix, k=key)
    log.debug(crv)
    return crv

@ul.do_function_on('singleLast')
def polyConstraint(target, mesh, direct=True):
    closest_uv = ul.get_closest_component(target, mesh)
    if not direct:
        target = create_parent(target)
    constraint = pm.pointOnPolyConstraint(
        mesh, target, mo=True)
    stripname = mesh.split('|')[-1]
    constraint.attr(stripname + 'U0').set(closest_uv[0])
    constraint.attr(stripname + 'V0').set(closest_uv[1])

@ul.error_alert
@ul.do_function_on('singleLast')
def constraint_multi(ob, target, constraintType='Point', addChildAttr=False):
    constraintDict = {
        'Point': ul.partial(pm.pointConstraint , mo=True),
        'Parent': ul.partial(pm.parentConstraint , mo=True),
        'Orient': ul.partial(pm.orientConstraint , mo=True),
        'PointOrient': None,
        'LocP': None,
        'LocO': None,
        'LocOP': None,
        'Aim': ul.partial(pm.aimConstraint , mo=True, aimVector=[1,0,0], upVector=[1, 0, 0], worldUpType="none")
    }
    assert (constraintDict.has_key(constraintType)), 'wrong Constraint Type'
    if constraintType == 'PointOrient':
        ct1 = constraintDict['Point'](target,ob)
        ct2 = constraintDict['Orient'](target,ob)
        return (ct1, ct2)
    if constraintType.startswith('Loc'):
        assert (isinstance(ob,pm.general.MeshVertex)), 'target %s is not a vertex'%ob
        loc = create_loc_on_vert(ob)
        if constraintType == 'LocP':
            ct = constraintDict['Point'](loc, target)
            return (loc, ct)
        if constraintType == 'LocO':
            ct = constraintDict['Orient'](loc, target)
            return (loc, ct)
        if constraintType == 'LocOP':
            ct1 = constraintDict['Point'](loc, target)
            ct2 = constraintDict['Orient'](loc, target)
            return (loc, ct1, ct2)
    ct = constraintDict[constraintType](target, ob)
    if addChildAttr:
        if not hasattr(ob, 'constraintFollow'):
            ob.addAttr(
                'constraintFollow', type='float',
                defaultValue=1.0, minValue=0.0, maxValue=1.0, k=1)
        ob.constraintFollow >> ct.attr(ul.get_name(target)+'W0')

@ul.do_function_on('singleLast')
def connect_visibility(ob, target, attrname='Vis'):
    if not hasattr(target, attrname):
        target.addAttr(attrname, type='bool', k=1)
    target.attr(attrname) >> ob.visibility

@ul.do_function_on('last')
def connect_visibility_enum(obs, target, enumAttr='EnumVis'):
    if not hasattr(target, enumAttr):
        target.addAttr(enumAttr, type='enum', enumName=[ob.name().split('_')[-1] for ob in obs], k=1)
    for id, ob in enumerate(obs):
        flogic = pm.nt.Condition()
        flogic.colorIfTrueR.set(1)
        flogic.colorIfFalseR.set(0)
        flogic.outColorR >> ob.visibility
        target.attr(enumAttr) >> flogic.firstTerm
        flogic.secondTerm.set(id)
        yield flogic

@ul.do_function_on('singleLast')
def aim_setup(ctl,loc):
    oldParent = ctl.getParent().getParent()
    orientOffset = create_parent(ctl)
    orientOffset.rename(
        ul.get_name(ctl)+'_orientOffset')
    aimTransform = orientOffset.duplicate(
        name=orientOffset.name().replace('orientOffset','Aim'),po=True,rr=True)[0]
    aimGp = create_parent(aimTransform)
    aimGp.setParent(None)
    if pm.objExists('aimGp'):
        aimGp.setParent(pm.ls('aimGp')[0])
    else:
        pm.group(aimGp, name='aimGp')
    connect_transform(aimTransform, orientOffset, rotate=True)
    pm.aimConstraint(
        loc, aimTransform,
        mo=True, aimVector=[1,0,0],
        upVector=[1, 0, 0], worldUpType="none")
    locConnection = list(
        connect_with_loc(
            ctl, ctl.outputs(type='joint')[0], all=True))
    locGp = locConnection[0].getParent()
    locConnection.append(locGp)
    locGp.setParent(oldParent)
    for c in locConnection:
        c.rename(c.name().replace('loc','aimLoc'))
    return (orientOffset, aimGp, locGp)

@ul.do_function_on()
def create_offset_bone(bone, child=False, suffix='offset_bon'):
    if not ul.get_type(bone) == 'joint':
        log.warning('{} is not joint'.format(bone))
        return
    newname = bone.name().split('|')[-1].split('_')[0] + '_' + suffix
    offsetbone = pm.duplicate(bone, name=newname, po=True)[0]
    offsetbone.drawStyle.set(2)
    oldParent = bone.getParent()
    bone.setParent(offsetbone)
    return offsetbone

@ul.do_function_on()
def create_loc_control(ob, connect=True,**kws):
    obname = ob.name().split('|')[-1]
    loc = pm.spaceLocator(name=obname + '_loc')
    loc.setTranslation(ob.getTranslation('world'), 'world')
    loc.setRotation(ob.getRotation('world'), 'world')
    loc_Gp = create_parent(loc)
    if connect:
        connect_transform(loc, ob, **kws)
    return loc

@ul.do_function_on('oneToOne')
def connect_with_loc(ctl,bon,**kws):
    loc = create_loc_control(bon,**kws)
    pct = pm.pointConstraint(ctl, loc, mo=True)
    oct = pm.orientConstraint(ctl, loc, mo=True)
    log.info('{} connect with {} using {}'.format(ctl,bon,loc))
    return (loc,pct,oct)

@ul.do_function_on(type_filter=['vertex'])
def create_loc_on_vert(vert,name='guideLoc'):
    if isinstance(vert,pm.general.MeshVertex):
        mesh = vert.node()
        uv = ul.get_closest_info(vert.getPosition(), mesh)['Closest UV']
        loc = pm.spaceLocator()
        locGp = create_parent(loc)
        ppconstraint = pm.pointOnPolyConstraint(
            mesh, locGp, mo=False)
        stripname = ul.get_name(mesh.getParent())
        ppconstraint.attr(stripname + 'U0').set(uv[0])
        ppconstraint.attr(stripname + 'V0').set(uv[1])
        return loc

@ul.do_function_on(type_filter=['nurbsCurve'])
def create_locs_on_curve(inputcurve, name='curveLoc', amount=3, constraint=True):
    assert (amount>1), 'Amount Too low, minimum is 2' 
    pm.loadPlugin('matrixNodes.mll')
    inc = 1.0/(amount-1)
    curveShape = inputcurve.getShape()
    locs = []
    for i in range(amount):
        infoNode = pm.nt.PointOnCurveInfo()
        infoNode.rename('{}{:02d}_pointOnCurveInfo'.format(name, i+1))
        curveShape.worldSpace[0] >> infoNode.inputCurve
        infoNode.parameter.set(i*inc)
        infoNode.turnOnPercentage.set(1)
        cross_vector = pm.nt.VectorProduct()
        cross_vector.rename('{}{:02d}_crossVector'.format(name, i+1))
        cross_vector.operation.set(2)
        infoNode.normal >> cross_vector.input1
        infoNode.tangent >> cross_vector.input2
        compose_matrix = pm.nt.FourByFourMatrix()
        compose_matrix.rename('{}{:02d}_composeMatrix'.format(name, i+1))
        connection_dict = dict(
            normalX='in00', normalY='in01', normalZ='in02',
            tangentX='in10', tangentY='in11', tangentZ='in12',
            outputX='in20', outputY='in21', outputZ='in22',
            positionX='in30', positionY='in31', positionZ='in32'
        )
        for srcatr, targetatr in connection_dict.iteritems():
            if srcatr.startswith('output'):
                cross_vector.attr(srcatr) >> compose_matrix.attr(targetatr)
            else:
                infoNode.attr(srcatr) >> compose_matrix.attr(targetatr)
        decompose_matrix = pm.nt.DecomposeMatrix()
        decompose_matrix.rename('{}{:02d}_decomposeMatrix'.format(name, i+1))
        compose_matrix.output >> decompose_matrix.inputMatrix
        loc = pm.spaceLocator()
        loc.rename('{}{:02d}'.format(name, i+1))
        decompose_matrix.outputTranslate >> loc.translate
        decompose_matrix.outputRotate >> loc.rotate
        # pairblend_node = pm.createNode('pairBlend')
        # decompose_matrix.outputTranslate >> pairblend_node.inTranslate2
        # decompose_matrix.outputRotate >> pairblend_node.inRotate2
        # loc.translate >> pairblend_node.inTranslate1
        # loc.rotate >> pairblend_node.inRotate1
        # pairblend_node.outTranslate >> loc.translate
        # pairblend_node.outRotate >> loc.rotate
        loc.addAttr('parameter', at='float', k=1, max=1.0, min=0.0, defaultValue=i*inc)
        loc.parameter >> infoNode.parameter
        locs.append(loc)
    pm.aimConstraint(locs[1], locs[0])
    pm.aimConstraint(locs[-2], locs[-1])
    # constraint_multi(locs[0], locs[1], constraintType='Aim')
    # constraint_multi(locs[-1], locs[-2], constraintType='Aim')
    return locs
# --- Transformation ---

@ul.do_function_on('oneToOne')
def xformTo(ob, target):
    const = pm.parentConstraint(target, ob)
    pm.delete(const)
    log.info('{} match to {}'.format(ob,target))

@ul.do_function_on('oneToOne')
def match_transform(ob, target):
    ob.setMatrix(target.getMatrix(ws=True), ws=True)
    log.info('{} match to {}'.format(ob,target))

@ul.do_function_on('oneToOne')
def connect_transform(ob, target, **kws):
    attrdict = {
        'translate': ['tx', 'ty', 'tz'],
        'rotate': ['rx', 'ry', 'rz'],
        'scale': ['sx', 'sy', 'sz']
    }
    for atr in attrdict:
        if atr not in kws:
            kws[atr] = False
            if 'all' in kws:
                if kws['all']:
                    kws[atr] = True
    for atr, value in attrdict.items():
        if atr in kws:
            if kws[atr] is False:
                continue
            if 'disconnect' in kws:
                if kws['disconnect']:
                    ob.attr(atr) // target.attr(atr)
                    for attr in value:
                        ob.attr(attr) // target.attr(attr)
                        log.info('{} disconnect to {}'.format(
                            ob.attr(attr), target.attr(attr)))
                    continue
            ob.attr(atr) >> target.attr(atr)
            for attr in value:
                ob.attr(attr) >> target.attr(attr)
                log.info('{} connect to {}'.format(
                    ob.attr(attr), target.attr(attr)))

@ul.do_function_on()
def disconnect_transform(ob , attr='all'):
    attrdict = {
        'translate': ['translate','tx', 'ty', 'tz'],
        'rotate': ['rotate','rx', 'ry', 'rz'],
        'scale': ['scale','sx', 'sy', 'sz']
    }
    attrdict['all'] = []
    for key,value in attrdict.items():
        attrdict['all'].extend(value)
    assert (attr in attrdict), 'attribute to connect is not valid, valid value: %s'%str(attrdict.keys())
    for atr in attrdict[attr]:
        ob.attr(atr).disconnect()

# --- Blend Shape ---
@ul.do_function_on(type_filter=["blendShape"])
def rebuild_blendshape_target(
        bsname,
        newBSName='RebuildBS',
        reset_value=False,
        rebuild=False,
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

    if rebuild is True:
        base_ob_node = blendshape.getBaseObjects()[0].getParent().getParent()

        base_ob_name = base_ob_node.name()
        blendshape_name = blendshape.name()
        iter = 1
        target_rebuild_list = []
        if parent != None:
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
        pm.blendShape(name=newBSName)
        blend_reget = rebuild_blendshape_target(blendshape_name)
        blendshape = blend_reget[0]
        target_list = blend_reget[1]
    return (blendshape, target_list)

# --- Skin Cluster ---

@ul.do_function_on(type_filter=['joint'])
def freeze_skin_joint(bon, hi=False):
    bonname = ul.get_name(bon)
    tempBon = pm.duplicate(bon,po=True,rr=True)[0]
    for child in bon.getChildren(type='joint'):
        pm.parent(child, tempBon)
    move_skin_weight(bon, tempBon)
    pm.makeIdentity(bon, apply=True)
    for child in tempBon.getChildren(type='joint'):
        pm.parent(child, bon)
    move_skin_weight(tempBon, bon)
    pm.delete(tempBon)
    # pm.select(bon, r=True)
    # newbp = pm.dagPose(bp=True, save=True)
    # bindPoses = pm.ls(type=pm.nt.DagPose)
    # for bp in bindPoses:
    #     if bp != newbp:
    #         pm.delete(bp)
    reset_bindPose_root(bon)
    if hi:
        bonChain = ul.iter_hierachy(bon)
        bonChain.next()
        try:
            while bonChain:
                bon = bonChain.next()
                freeze_skin_joint(bon)
        except StopIteration:
            return

@ul.do_function_on('oneToOne', type_filter=['joint'])
def move_skin_weight(bon, targetBon, hi=False, reset_bindPose=False):
    '''Move all weights from all skinCluster of one bone to another'''
    skinClusters = bon.outputs(type='skinCluster')
    for skinCluster in skinClusters:
        inflList = skinCluster.getInfluence()
        skinCluster.normalizeWeights.set(1)
        pm.skinCluster(skinCluster,e=True,fnw=True)
        if targetBon not in inflList:
            skinCluster.addInfluence(targetBon, wt=0)
        skinCluster.attr('maintainMaxInfluences').set(False)
        for infl in inflList:
            if infl == bon or infl == targetBon:
                infl.attr('lockInfluenceWeights').set(False)
            else:
                infl.attr('lockInfluenceWeights').set(True)
        if bon in inflList:
            for geo in skinCluster.getGeometry():
                pm.skinPercent(skinCluster,geo.verts,nrm=True,tv=[bon,0])
        for infl in inflList:
            infl.attr('lockInfluenceWeights').set(False)
        try:
            if bon in inflList:
                skinCluster.removeInfluence(bon)
        except (OSError,IOError,RuntimeError) as why:
            pm.warnings(why)
            log.error(why)
    if reset_bindPose:
        pm.select(targetBon, r=True)
        newbp = pm.dagPose(bp=True, save=True)
        bindPoses = pm.ls(type=pm.nt.DagPose)
        for bp in bindPoses:
            if bp != newbp:
                pm.delete(bp)
    if hi:
        bonChain = ul.iter_hierachy(bon)
        targetBonChain = ul.iter_hierachy(targetBon)
        for bon,targetBon in zip(iter(bonChain), iter(targetBonChain)):
            move_skin_weight(bon,targetBon)

@ul.do_function_on(type_filter=['mesh'])
def clean_skin_weight(mesh, offset_bone_name=['offset'] ):
    '''Remove offset Bone Weight'''
    skinCluster = ul.get_skin_cluster(mesh)
    inflList = skinCluster.getInfluence()
    fix_inflPairs = []
    for infl in inflList:
        infl.attr('lockInfluenceWeights').set(True)
        if any(offset_name in infl.split('|')[-1] for offset_name in offset_bone_name):
            childs = [
                child for child in infl.getChildren(type='joint')
                if not any(offset_name in child.split('|')[-1] for offset_name in offset_bone_name)]
            if childs:
                next_infl = childs[0]
                fix_inflPairs.append((infl, next_infl))
            else:
                log.info(pm.skinPercent(skinCluster, mesh.verts,infl, v=True, q=True))
    for infl, next_infl in fix_inflPairs:
        infl.attr('lockInfluenceWeights').set(False)
        next_infl.attr('lockInfluenceWeights').set(False)
        pm.skinPercent(skinCluster,mesh.verts,nrm=True,tv=[infl,0])
        try:
            skinCluster.removeInfluence(infl)
        except (OSError,IOError,RuntimeError) as why:
            pm.warnings(why)
            log.error(why)
        infl.attr('lockInfluenceWeights').set(True)
        next_infl.attr('lockInfluenceWeights').set(True)
    for infl in skinCluster.getInfluence():
        infl.attr('lockInfluenceWeights').set(False)
    pm.skinPercent(skinCluster,mesh,nrm=True)

@ul.do_function_on('singleLast', type_filter=['joint', 'mesh'])
def query_joint_weight(bone, skinmesh):
    skin_cluster = ul.get_skin_cluster(skinmesh)
    assert(skin_cluster), '%s have no skin bind'%skinmesh
    inflList = skin_cluster.getInfluence()
    if bone in inflList:
        weights = [pm.skinPercent(skin_cluster, vert, transform=bone, q=True) for vert in skinmesh.verts]
        return weights

@ul.do_function_on('singleLast', type_filter=['mesh'])
def copy_weight_exact(mesh, targetMesh, useLabel=False):
    try:
        skinCluster = ul.get_skin_cluster(mesh)
        assert (len(mesh.verts) == len(targetMesh.verts))
    except:
        log.error("SourceMesh does not have skinCluster or selected meshes are not identical")
        return
    inflList = skinCluster.getInfluence()
    try: 
        ul.get_skin_cluster(targetMesh)
    except:
        pm.skinCluster(targetMesh, inflList)
    # if useLabel:
    target_skinCluster = ul.get_skin_cluster(targetMesh)
    target_infList = target_skinCluster.getInfluence()
    if useLabel:
        for infl in target_infList:
            label_joint(infl)
            infl.attr('lockInfluenceWeights').set(False)
        target_skinCluster.setNormalizeWeights(2)
        for infl in inflList:
            add_joint_influence(infl, targetMesh)
    else:
        for inf in inflList:
            if inf not in target_infList:
                add_joint_influence(inf, target_infList)
    for vid in range(len(targetMesh.verts)):
        for source_joint in inflList:
            target_joint = source_joint
            if useLabel:
                target_joint = [j for j in target_infList if j.otherType.get() == source_joint.otherType.get()]
                if not target_joint:
                    log.warning('There is no joint in target Mesh match {}'.format(source_joint))
                    continue
                target_joint = target_joint[0]
            weight = pm.skinPercent(skinCluster, mesh.verts[vid], transform=source_joint, q=True)
            pm.skinPercent(target_skinCluster, targetMesh.verts[vid], tv=[target_joint, weight])
    target_skinCluster.setNormalizeWeights(1)
    target_skinCluster.forceNormalizeWeights(True)
    # else:
        # for infl in inflList:
            # target_skinCluster = skinCluster.duplicate(rr=True, ic=True)[0]
            # target_skinCluster.outputGeometry[0] >> targetMesh.getShape().inMesh
            # add_joint_influence(infl, targetMesh)
            # copy_joint_weight([mesh, targetMesh], infl)

@ul.do_function_on('last', type_filter=['joint','mesh'])
def copy_joint_weight(meshes, bone):

    if len(meshes) < 2:
        return
    skinClusters = [ul.get_skin_cluster(mesh) for mesh in meshes]

    inflLists = [skinCluster.getInfluence() for skinCluster in skinClusters]
    source_mesh = meshes[0]
    source_skinCluster = skinClusters[0]
    source_infList = inflLists[0]
    target_meshes = meshes[1:]
    target_skinClusters = skinClusters[1:]
    target_infLists = inflLists[1:]
    if not all([
            source_skinCluster, all([sc for sc in target_skinClusters]),
            all([len(mesh.verts) == len(target_mesh.verts) for target_mesh in target_meshes]), bone in source_infList]):
        return
    weights = query_joint_weight(bone, source_mesh)
    for id, weight in enumerate(weights):
        for target_mesh, target_skinCluster, target_infList in zip(target_meshes, target_skinClusters, target_infLists):
            add_joint_influence(bone, target_mesh)
            for infl in target_infList:
                infl.attr('lockInfluenceWeights').set(False)
            pm.skinPercent(target_skinCluster, target_mesh.verts[id], tv=[bone, weight])

@ul.do_function_on('singleLast', type_filter=['joint', 'mesh'])
def add_joint_influence(bone, skinmesh, remove=False):
    # if not ul.get_skin_cluster(skinmesh):
    #     pm.select(bone)
    #     pm.bindSkin(skinmesh)
    #     return ul.get_skin_cluster(skinmesh)
    skin_cluster = ul.get_skin_cluster(skinmesh)
    assert(skin_cluster), '%s have no skin bind'%skinmesh
    inflList = skin_cluster.getInfluence()
    if remove:
        if bone in inflList:
            skin_cluster.removeInfluence(bone)
            log.info('{} influence remove from {}'.format(bone,skinmesh))
    if bone not in inflList:
        skin_cluster.addInfluence(bone, wt=0)
        log.info('{} influence add to {}'.format(bone,skinmesh))

@ul.do_function_on('oneToOne', type_filter=['mesh', 'joint'])
def skin_weight_filter(ob, joint, min=0.0, max=0.1, select=False):
    '''return vertex with weight less than theshold'''
    skin_cluster = ul.get_skin_cluster(ob)
    ob_shape = ul.get_shape(ob)
    filter_weight = []
    for vtx in ob_shape.vtx:
        weight = pm.skinPercent(skin_cluster, vtx, query=True, transform=joint, transformValue=True)

        if min < weight <= max:
            filter_weight.append(vtx)
    if select:
        pm.select(filter_weight)
    return filter_weight

@ul.do_function_on(type_filter=['mesh'])
def switch_skin_type(ob, type='Linear'):
    type_dict = {
        'Linear': 0,
        'Dual Quartenion': 1,
        'Blended': 2}
    if not ul.get_skin_cluster(ob) and type not in type_dict.keys():
        return
    skin_cluster = ul.get_skin_cluster(ob)
    skin_cluster.setSkinMethod(type_dict[type])
    deform_normal_state = 0 if type_dict[type] is 2 else 1
    skin_cluster.attr('deformUserNormals').set(deform_normal_state)


@ul.do_function_on('lastType', type_filter=['vertex', 'edge', 'face', 'mesh', 'joint'])
def skin_weight_setter(component_list, joints_list, skin_value=1.0, normalized=True, hierachy=False):
    '''set skin weight to skin_value for vert in verts_list to first joint,
       other joint will receive average from normalized weight
       joint is not need to be a influence of Skin Cluster'''

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

    if any([type(component) is pm.nt.Transform for component in component_list]):
            for component in component_list:
                try:
                    skin_cluster = ul.get_skin_cluster(component)
                except:
                    skin_cluster = pm.skinCluster(component.node(), joints_list)
                for joint in joints_list:
                    if joint not in skin_cluster.getInfluence():
                        add_joint_influence(joint,component)
                        reset_bindPose_all()
                try:
                    
                    pm.select(component, r=True)
                    pm.skinPercent(skin_cluster, transformValue=get_skin_weight())

                except RuntimeError as why:
                    log.warning('Set Skin Error:{}'.format(why))
    else:
        for component in component_list:
            verts_list = ul.convert_component(component)
            try:
                skin_cluster = ul.get_skin_cluster(verts_list[0])
            except:
                skin_cluster = pm.skinCluster(verts_list[0].node(), joints_list)

            for joint in joints_list:
                if joint not in skin_cluster.getInfluence():
                    add_joint_influence(joint,component)
                    reset_bindPose_all()
            try:
                if all([skin_cluster, verts_list, joints_list]):
                    pm.select(verts_list, r=True)
                    pm.skinPercent(skin_cluster, transformValue=get_skin_weight())
            except RuntimeError as why:
                log.warning('Set Skin Error:{}'.format(why))

@ul.do_function_on(type_filter=['vertex', 'edge', 'face', 'mesh'])
def dual_weight_setter(component_list, weight_value=0.0, query=False):
    verts_list = ul.convert_component(component_list)
    shape = verts_list[0].node()
    skin_cluster = ul.get_skin_cluster(verts_list[0])
    if query:
        weight_list = []
        for vert in verts_list:
            for vert in vert.indices():
                weight = skin_cluster.getBlendWeights(shape, shape.vtx[vert])
                weight_list.append((ul.get_name(shape.vtx[vert]).split('.')[-1], weight))
        return weight_list
    else:
        for vert in verts_list:
            for vert in vert.indices():
                skin_cluster.setBlendWeights(shape, shape.vtx[vert], [weight_value, weight_value])

                # pm.select(verts_list)
                # skin_cluster.setBlendWeights(shape, verts_list, [weight_value,])

@ul.do_function_on(type_filter=['vertex', 'edge', 'face', 'mesh'])
def fix_bad_weight(ob):
    skin_cluster = ul.get_skin_cluster(ob)
    if skin_cluster:
        skin_cluster.smoothWeights(0.5)
# Bone Utilities
@ul.do_function_on(type_filter=['nurbsCurve'])
def curve_to_bone(inputcurve, amount=3):
    pcvs = ul.get_points_on_curve(inputcurve, amount=amount)
    newBones = []
    pm.select(cl=True)
    for tr, rot in pcvs:
        newBone = pm.joint(p=tr)
        newBones.append(newBone)
    pm.joint(newBones[0], e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
    return newBones

@ul.do_function_on(type_filter=['nurbsCurve'])
def create_bone_on_curve(inputcurve, amount=3, parent=True):
    cvlocs = create_locs_on_curve(inputcurve, amount=amount)
    newBones = []
    tempTr = []
    loclist = []
    for cvloc in cvlocs:
        loclist.append(cvloc)
        if newBones:
            pm.select(newBones[-1], r=True)
        else:
            pm.select(cl=True)
        newBone = pm.joint(p=cvloc.getTranslation('world'))
        temp_transform = pm.nt.Transform()
        temp_transform.setParent(cvloc)
        ul.reset_transform(temp_transform)
        tempTr.append(temp_transform)
        newBones.append(newBone)
        # connect_with_loc(tr,bone)
        # connect_transform(tr, bone, translate=True, rotate=True)
    if not parent:
        for tr, bone in zip(tempTr, newBones):
            bone.setParent(tr)
            tempP = create_parent(bone)
            ul.reset_transform(bone.getParent())
            bone.setParent(tr)
            pm.delete(tempP)
    else:
        pm.joint(newBones[0], e=True, oj='xyz', secondaryAxisOrient='yup', ch=True, zso=True)
        for tr, bone in zip(tempTr, newBones):
            offsetBone = create_offset_bone(bone)
            trParent = create_parent(tr)
            match_transform(trParent, offsetBone)
            pm.parentConstraint(tr, offsetBone)
    result = [(bone,tr,loc) for bone,tr,loc in zip(newBones, tempTr, loclist)]
    return result

@ul.do_function_on(
    'set',
    type_filter=['locator','transform', 'mesh', 'vertex', 'edge', 'face'])
def create_joint(ob_list, parent=None):
    new_joints = []
    for ob in ob_list:
        if type(ob) == pm.general.MeshFace:
            new_joints.append(create_middle_joint(ob))
        else:
            if type(ob) == pm.nt.Transform:
                get_pos = ob.getTranslation('world')
            elif type(ob) == pm.general.MeshVertex:
                get_pos = ob.getPosition(space='world')
            elif type(ob) == pm.general.MeshEdge:
                get_pos = ul.get_pos_center_from_edge(ob)
            pm.select(ob,r=True)
            new_joint = pm.joint(p=get_pos)
            new_joint.setParent(parent)
            new_joints.append(new_joint)
    for new_joint in new_joints:
        pm.joint(new_joint, edit=True, oj='xyz', sao='yup', ch=True, zso=True)
        if new_joint == new_joints[-1]:
            pm.joint(new_joint, edit=True, oj='none', ch=True, zso=True)
    pm.select(new_joints)
    return new_joints

@ul.do_function_on(
    'set',
    type_filter=['locator','transform', 'mesh', 'vertex', 'edge', 'face'])
def create_middle_joint(ob_list, parent=None):
    pos_list = ul.get_points(ob_list)

    if len(pos_list) > 1 and len(pos_list) != 0:
        pos_center = sum(pos_list)/len(pos_list)
    elif len(pos_list) == 1:
        pos_center = pos_list[0]
    else:
        pos_center = [0,0,0]
    new_joint = pm.joint(p=pos_center)
    new_joint.setParent(parent)
    return new_joint

@ul.do_function_on('set', type_filter=['transform','locator','mesh','joint'])
def parent_bone(boneList):
    boneLists = boneList
    while boneLists:
        bone = boneLists.pop()
        if boneLists:
            bone.setParent(boneLists[-1])

@ul.do_function_on(type_filter=['joint'])
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
        # for index, bone in enumerate(joint_list):
        #     try:
        #         pm.rename(bone, "%s%02d" % (joint_name[0], index + 1))
        #     except:
        #         pm.rename(bone, "%s#" % joint_name[0])
    return joint_list

@ul.do_function_on('oneToOne')
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

@ul.do_function_on('oneToOne')
def copy_skin_multi(source_skin_grp, dest_skin_grp, **kwargs):
    '''copy skin for 2 identical group hierachy'''
    source_skins = source_skin_grp.listRelatives(type='transform', ad=1)
    dest_skins = dest_skin_grp.listRelatives(type='transform', ad=1)
    if len(dest_skins) == len(source_skins):

        for skinTR, dest_skinTR in zip(source_skins, dest_skins):
            copy_skin_single(skinTR, dest_skinTR, **kwargs)

    else:


@ul.do_function_on('oneToOne')
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


        kwargs['ds'] = skin_dest.name()
        # pm.copySkinWeights(**kwargs)
        # skin_dest.setSkinMethod(skin.getSkinMethod())

    except AttributeError:


        for ob in [source_skin, dest_skin]:



def reset_bindPose_all():
    newbp = pm.dagPose(bp=True, save=True)
    bindPoses = pm.ls(type=pm.nt.DagPose)
    for bp in bindPoses:
        if bp != newbp:
            pm.delete(bp)

    return newbp

@ul.do_function_on()
def reset_bindPose_root(joint_root):
    joint_childs = joint_root.listRelatives(type=pm.nt.Joint, ad=True)
    for joint in joint_childs:
        if joint.rotate.get() != pm.dt.Vector(0, 0, 0):

            joint.jointOrient.set(joint.rotate.get())
            joint.rotate.set(pm.dt.Vector(0, 0, 0))
    reset_bindPose_all()

def deform_normal_off(state=False):
    skin_clusters = pm.ls(type='skinCluster')
    if not skin_clusters:
        return
    for skin_cluster in skin_clusters:
        skin_cluster.attr('deformUserNormals').set(False)
        log.info('{} Deform User Normals Set To {}'.format(skin_cluster,state))

# --- Joint ---
@ul.do_function_on('set',['mesh'])
def select_influence(objects):
    infs = []
    for ob in objects:
        try:
            skin_cluster = ul.get_skin_cluster(ob)
        except RuntimeError as why:
            log.error(why)
            return
        infs.append(skin_cluster.getInfluence())
    pm.select(infs, r=True)
    return infs

def get_current_chain(ob):
    boneChains = []
    while ob.getChildren():
        childsCount = len(ob.getChildren(type='joint'))
        assert (childsCount==1), 'Joint split to {} at {}'.format(childsCount,ob)
        boneChains.append(ob)
        ob = ob.getChildren(type='joint')[0]
    else:
        boneChains.append(ob)
    return boneChains

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

                return opBone

def check_default_value(node, atrs, defaultValue):
    return any([node.attr(atr).get() != defaultValue for atr in atrs])

def check_bone_transform(bone, returnValueOnly=False):
    rot_atr = ['rx', 'ry', 'rz']
    scl_atr = ['sx', 'sy', 'sz']
    rotate_value = check_default_value(bone, rot_atr, 0.0)
    scale_value = check_default_value(bone, scl_atr, 1.0)
    if returnValueOnly:
        return (rotate_value, scale_value)
    if rotate_value or scale_value:
        freeze_transform = pm.confirmBox(
            'Freeze Transform',
            '{} have rotate or scale value. Do you want to freeze transform the joint?'.format(bone))
        if bone.outputs(type='skinCluster'):
            freeze_transform = pm.confirmBox(
                'Freeze Transform',
                '{} is bound to a skinCluster. Value will be reset to default'.format(bone))
            if freeze_transform:
                ul.reset_transform(bone, translate=False)
        else:
            pm.makeIdentity(bone, apply=True)

@ul.do_function_on(type_filter='joint')
def dup_bone(bone,name='joint1'):
    pm.select(cl=True)
    dupbone = pm.nt.Joint()
    #dupbone = bone.duplicate(rr=True,po=True)[0]
    #dupbone.setParent(None)
    dupbone.rename(name)
    dupbone.radius.set(bone.radius.get()*2)
    # match_transform(dupbone,bone)
    xformTo(dupbone, bone)
    pm.makeIdentity(dupbone, apply=True)
    return dupbone

@ul.do_function_on(type_filter='joint')
def dup_bone_chain(boneRoot,suffix='dup'):
    boneChain = ul.iter_hierachy(boneRoot)
    newChain = []
    for bone in iter(boneChain):
        dupBone= pm.duplicate(bone,po=True,rr=True)[0]
        # dupBone = pm.nt.Joint()
        # xformTo(dupBone, bone)
        dupBone.rename(ul.get_name(bone)+'_%s'%suffix)
        if newChain:
            dupBone.setParent(newChain[-1])
        else:
            dupBone.setParent(None)
        newChain.append(dupBone)
    return newChain

@ul.do_function_on('last', type_filter=['joint'])
def connect_joint(bones, boneRoot, **kwargs):
    for bone in bones:
        pm.connectJoint(bone, boneRoot, **kwargs)

@ul.do_function_on('hierachy', type_filter=['joint'])
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

                if wc in ob.name():
                    wildcard = wc
                    sideid = side_id
                    break
            if wildcard:
                break

        label_name = ob.name().split('|')[-1].replace(wildcard, '')
        while label_name.startswith('_'):
            label_name = label_name[1:]
        # if '|' in label_name:
        #     label_name = label_name.split('|')[-1]
        if remove_prefixes:
            for prefix in remove_prefixes:
                label_name = label_name.replace(prefix, '')
        ob.otherType.set(label_name)
        ob.side.set(sideid)
        log.info('set {} joint label to {}'.format(ob, label_name))
    except AttributeError as why:
        log.error(why)

@ul.do_function_on('set', type_filter=['joint'])
def rename_bonechain(boneRoots, newName, startcollumn=0, startNum=1, suffix='bon'):
    collumNames = list(alphabet)
    collumNames.extend(
        [''.join(list(i)) for i in list(
            product(alphabet, repeat=2))])
    for id, boneRoot in enumerate(boneRoots):
        boneChain = ul.iter_hierachy(boneRoot)
        i = startNum
        assert ((startcollumn+id)<len(collumNames)), 'Maximum Bone Collumn reach, maximum: %d'%len(collumNames)
        collumnName = collumNames[startcollumn+id]
        for bone in iter(boneChain):
            if hasattr(bone,'rename'):
                bone.rename('{}{}{:02d}_{}'.format(
                    newName,
                    collumnName,
                    i,
                    suffix))
                i += 1

@ul.do_function_on(type_filter=['joint'])
def create_roll_joint(oldJoint):
    newJoint = pm.duplicate(oldJoint, rr=1, po=1)[0]
    pm.rename(newJoint, ('%sRoll1' % oldJoint.name()).replace('Left', 'LeafLeft'))
    newJoint.attr('radius').set(2)
    pm.parent(newJoint, oldJoint)
    return newJoint

@ul.do_function_on(type_filter=['joint'])
def create_sub_joint(ob):
    subJoint = pm.duplicate(ob, name='%sSub' % ob.name(), rr=1, po=1, )[0]
    new_pairBlend = pm.createNode('pairBlend')
    subJoint.radius.set(2.0)
    pm.rename(new_pairBlend, '%sPairBlend' % ob.name())
    new_pairBlend.attr('weight').set(0.5)
    ob.rotate >> new_pairBlend.inRotate2
    new_pairBlend.outRotate >> subJoint.rotate
    return (ob, new_pairBlend, subJoint)

@ul.do_function_on(type_filter=['joint'])
def mirror_joint_tranform(bone, translate=False, rotate=True, **kwargs):

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

@ul.do_function_on(type_filter=['joint'])
def mirror_joint_multi(ob):
    pm.mirrorJoint(ob, myz=True, sr=('Left', 'Right'))

# --- Hair System Functions ---

def create_hair_system(name=''):
    hairSys = pm.nt.HairSystem()
    if name:
        hairSys.getParent().rename(name)
    if not pm.ls(type='nucleus'):
        nucleus = pm.nt.Nucleus()
    else:
        nucleus = pm.ls(type='nucleus')[-1]
    if pm.ls(type='time'):
        time = pm.PyNode('time1')
    else:
        time = pm.nt.Time()
    time.outTime >> hairSys.currentTime
    time.outTime >> nucleus.currentTime
    hairSys.currentState >> nucleus.inputActive[len(nucleus.inputActive.get())]
    hairSys.startState >> nucleus.inputActiveStart[len(nucleus.inputActiveStart.get())]
    nucleus.outputObjects[0] >> hairSys.nextState
    nucleus.startFrame >> hairSys.startFrame
    hairSys.active.set(1)
    return (hairSys, nucleus)

@ul.do_function_on(type_filter=['nurbsCurve'])
def make_curve_dynamic(inputcurve, hairSystem=''):
    if hairSystem and pm.objExists(hairSystem):
        allHairSys = pm.ls(type='hairSystem')
        if pm.PyNode(hairSystem).getShape() in allHairSys:
            hairSys = pm.PyNode(hairSystem).getShape()
    if 'hairSys' not in locals():
        if hairSystem:
            hairSys = create_hair_system(name=hairSystem)[0]
        else:
            if pm.ls(type='hairSystem'):
                hairSys = pm.ls(type='hairSystem')[-1]
            else:
                hairSys = create_hair_system()[0]
    hair_id = len(hairSys.inputHair.listConnections())
    outputcurve = pm.duplicate(inputcurve,name=inputcurve.name()+'_dynamic',rr=1)[0]
    outputcurveGp = pm.nt.Transform(name=inputcurve.name()+'_outputCurveGp')
    #outputcurve.duplicate()
    outputcurve.setParent(outputcurveGp)
    pm.makeIdentity(outputcurve,apply=True)
    outputcurve_shape = outputcurve.getShape()
    follicle  = pm.nt.Follicle()
    #pm.refresh()
    inputcurve_shape = inputcurve.getShape()
    inputcurve_shape.local >> follicle.startPosition
    inputcurve.worldMatrix >> follicle.startPositionMatrix
    follicle.outHair >> hairSys.inputHair[hair_id]
    hairSys.outputHair[hair_id] >> follicle.currentPosition
    #pm.refresh()
    follicle.outCurve >> outputcurve_shape.create
    #pm.refresh()
    follicle.startDirection.set(1)
    follicle.restPose.set(1)
    #follicle.fixedSegmentLength.set(1)
    #follicle.segmentLength.set(5)
    follicleGp = pm.nt.Transform(name=inputcurve.name()+'_follicleGp')
    follicle.getParent().setParent(follicleGp)
    inputcurve.setParent(follicle.getParent())
    pm.refresh()
    return (outputcurve_shape, follicle, hairSys)

#--- Rigging Body Controls Methods ---
@ul.do_function_on()
def create_prop_control(bone, parent='ctlGp', useLoc=False, customShape=None):
    # check_bone_transform(bone)
    if 'gp' not in bone.name().lower():
        bonGp = create_offset_bone(bone)
    ctlname = ul.get_name(bone).replace('bon', 'ctl')
    if customShape:
        ctl = customShape()
        ctl.rename(ctlname)
    else:
        ctl = createPinCircle(
            ctlname,
            step=4,
            sphere=True,
            radius=2,
            length=0)
    ctlGp = create_parent(ctl)
    xformTo(ctlGp, bone)
    if useLoc:
        connect_with_loc(ctl, bone, all=True)
    else:
        connect_transform(ctl, bone, all=True)
    control_tagging(ctl, metaname='PropControlsSet_MetaNode')
    if parent:
        if pm.objExists(parent):
            ctlGp.setParent(parent)
        else:
            pm.group(ctlGp,name=parent)
    return ctl

@ul.do_function_on()
def create_free_control(bone, parent='ctlGp',useLoc=False, customShape=None):
    # check_bone_transform(bone)
    if 'gp' not in bone.name().lower():
        bonGp = create_offset_bone(bone)
    for suf in ['bone', 'bon']:
        bonname = ul.get_name(bone).replace(suf,'')
    ctlname = bonname+'ctl'
    if customShape:
        ctl = customShape()
        ctl.rename(ctlname)
    else:
        ctl = createPinCircle(
                ctlname,
                step=24,
                sphere=True,
                radius=2,
                length=0)
    ctlGp = create_parent(ctl)
    xformTo(ctlGp, bone)
    if useLoc:
        connect_with_loc(ctl, bone, all=True)
    else:
        connect_transform(ctl, bone, all=True)
    control_tagging(ctl, metaname='FreeControlsSet_MetaNode')
    if parent:
        if pm.objExists(parent):
          ctlGp.setParent(parent)
        else:
            pm.group(ctlGp,name=parent)
    return ctl

@ul.do_function_on()
def create_parent_control(boneRoot, parent='ctlGp', useLoc=False, customShape=None):
    ctls = []
    boneChain = ul.iter_hierachy(boneRoot)
    for bone in iter(boneChain):
        # check_bone_transform(bone)
        if hasattr(bone, 'getChildren'):
            if not bone.getChildren(type='joint'):
                continue
        else:
            continue
        if not ul.get_type(bone) == 'joint':
            continue
        if 'offset' not in ul.get_name(bone):
            if bone.getParent():
                if 'offset' not in ul.get_name(bone.getParent()):
                    create_offset_bone(bone)
            else:
                create_offset_bone(bone)
            name = ul.get_name(bone)
            if customShape:
                ctl = customShape()
            else:
                ctl = createPinCircle(name)
            if name.endswith('_bon'):
                name = name.replace('_bon', '')
            ctl.rename(name + '_ctl')
            ctlGp = create_parent(ctl)
            ctlGp.rename(name + '_ctlGp')
            match_transform(ctlGp,bone)
            control_tagging(ctl, metaname='ParentControlsSet_MetaNode')
            if ctls:
                ctlGp.setParent(ctls[-1])
            ctls.append(ctl)
            connect_transform(ctl, bone, all=True )
    ctlRoot = ctls[0].getParent()
    if useLoc:
        loc = connect_with_loc(
            ctls[0],
            ctls[0].outputs(type='joint')[0], all=True)
        loc[0].getParent().setParent(ctls[0].getParent())
    if parent:
        if pm.objExists(parent):
            ctlRoot.setParent(parent)
        else:
            pm.group(ctlRoot,name=parent)
    result = (ctls,loc[0]) if useLoc else ctls
    return result

#--- Rigging Hair Control Methods ---
@ul.do_function_on()
def create_dynamic_chain(boneRoot, hairSystem=''):
    def create_ctl(b, name='circle', radius=1, color=[1,1,0,0]):
        ctl = pm.circle(name=name, radius=radius)[0]
        ctl.rotateY.set(90)
        ul.setColor(ctl.getShape(),color=color)
        pm.makeIdentity(ctl, apply=True)
        xformTo(ctl, b)
        return ctl
    bones = list(ul.iter_hierachy(boneRoot))
    bname = boneRoot.split('|')[-1]
    crv = ul.convert_to_curve(bones)
    crv.rename(bname+'_animCurve')
    dynamicSys = make_curve_dynamic(crv)
    dynaCrv = dynamicSys[0]
    dynaCrv.rename(bname+'_dynamicCurve')
    foc = dynamicSys[1]
    foc.getParent().rename(bname+'_focllicle')
    ctls = []
    pinLocs = []
    boneLocs = []
    ctlGrp = pm.nt.Transform(name=bname+'_rootCtlGp')
    pinGrp = pm.nt.Transform(name=bname+'_dynamicLocGp')
    rootCtl = create_ctl(bones[0], name=bname+'_dynamicAxis', radius=2.0)
    rootCtlGp = create_parent(rootCtl)
    rootCtlGp.setParent(ctlGrp)
    oldParent = foc.getParent().getParent()
    foc.getParent().setParent(rootCtl)
    pm.delete(oldParent)
    for bone, pos in zip(bones, [b.getTranslation('world') for b in bones]):
        boneName = bone.split('|')[-1]
        loc = create_loc_control(bone, connect=False)
        loc.rename(loc.replace('loc','pin'))
        if pinLocs:
            pm.aimConstraint(loc, pinLocs[-1])
        pinLocs.append(loc)
        remove_parent(loc)
        loc.setParent(pinGrp)
        ul.snap_to_curve(loc, dynaCrv)
        ctl = create_ctl(bone, name=boneName+'_ctl', color=[1,0,0,0])
        ctlGp = create_parent(ctl)
        ctlOffset = create_parent(ctl)
        ctlOffset.rename(boneName+'_offset_ctl')
        if ctls:
            ctlGp.setParent(ctls[-1])
        else:
            ctlGp.setParent(ctlGrp)
        ctls.append(ctl)
        offsetBoneGp = create_offset_bone(bone)
        offsetBoneGp.rename(boneName+'_rootOffset')
        offsetBone = create_offset_bone(bone)
        offsetBoneGp.rename(boneName+'_offset')
        connect_transform(ctl, bone, all=True)
        boneLoc = connect_with_loc(loc, ctlOffset, translate=True, rotate=True)[0]
        boneLoc.translate >> offsetBone.translate
        boneLoc.rotate >> offsetBone.rotate
        if boneLocs:
            boneLoc.getParent().setParent(boneLocs[-1])
        else:
            boneLoc.getParent().setParent(ctlGrp)
        boneLocs.append(boneLoc)
        #boneLoc.getParent().setTranslation(pos, 'world')
        ctlGp.setTranslation(pos, 'world')
        offsetBoneGp.setTranslation(pos, 'world')
    pm.aimConstraint(pinLocs[-2], pinLocs[-1])

@ul.do_function_on()
def create_long_hair(boneRoot, hairSystem='', circle=True, simplifyCurve=False, customShape=None):
    dynamicBones = dup_bone_chain(boneRoot, suffix='dynamic')
    boneGp = create_parent(boneRoot)
    dupBoneGp = create_parent(dynamicBones[0])
    bonChain = ul.iter_hierachy(boneRoot)
    dupBoneChain = ul.iter_hierachy(dynamicBones[0])
    for bone, dupbone in zip(iter(bonChain),iter(dupBoneChain)):
        tranformBool = any([0<bone.attr(atr).get() or bone.attr(atr).get()>0 for atr in ['rx','ry','rz', 'sx','sy','sz']])
        if tranformBool:
            log.info('%s contain value in rotate or scale. Commencing freeze transform'%bone)
            freeze_skin_joint(bone)
            pm.makeIdentity(dupbone, apply=True)
        offsetBone = create_offset_bone(bone)
        offsetMeta = as_meta(offsetBone)
        offsetMeta.connectChild(dupbone.name(), 'dynamicBone', 'drivenBone')
        #pm.orientConstraint(dupbone, offsetBone, mo=True)
        connect_transform(dupbone, offsetBone,rotate=True)
    ikhandle, ikeffector, ikcurve = pm.ikHandle(
        sj=dynamicBones[0], ee=dynamicBones[-1], solver='ikSplineSolver', ns=3, scv=simplifyCurve)
    ikhandle.setParent(dupBoneGp)
    ikcurve.rename(ul.get_name(boneRoot).replace('bon','ikCurve'))
    hairSystem = make_curve_dynamic(ikcurve, hairSystem=hairSystem)
    dynamicCurve, follicle, hairSys = [i for i in hairSystem]
    dynamicCurve.worldSpace[0] >> ikhandle.inCurve
    controls, rootLoc = create_parent_control(boneRoot, parent='',useLoc=True)
    nurbShapes = []
    if circle:
        for control in controls:
            if customShape:
                tempShape = customShape()
            else:
                tempShape = pm.circle(radius=2)
                tempShape[0].setRotation([0,90,0])
                pm.makeIdentity(tempShape[0], apply=True)
                nurbShapes.append(tempShape[1])
            ul.parent_shape(tempShape[0], control)
            control.addAttr('radius', type='float', defaultValue=2, k=1)
            control.radius >> tempShape[1].radius
            ul.setColor(control, color=[1,0,0,0])
            #pm.delete(tempShape)
    controlGp = create_parent(controls[0].getParent())
    controlGp = controlGp.rename(controlGp.name().split('_')[0]+'_root_ctlGp')
    controlRoot = pm.circle(radius=3)
    controlRoot[0].rename(controls[0].replace('ctl','axis'))
    controlRoot[0].setRotation([0,90,0])
    pm.makeIdentity(controlRoot[0], apply=True)
    controlRoot[0].addAttr('radius', type='float', defaultValue=3, k=1)
    controlRoot[0].addAttr('subRadius', type='float', defaultValue=2, k=1)
    controlRoot[0].radius >> controlRoot[1].radius
    controlRoot = controlRoot[0]
    xformTo(controlRoot, controlGp)
    controlRoot.setParent(controlGp)
    ul.setColor(controlRoot, color=[1,1,0,0])
    for control in controls:
        if hasattr(control, 'radius'):
            controlRoot.subRadius >> control.radius
    # controlRoot.addAttr('subRadius',type='float',defaultValue=2)
    # for sh in nurbShapes:
    #     controlRoot.subRadius >> sh.radius

    #loc.getParent().setParent(controlGp)
    dupBoneGp.setParent(controlRoot)
    focGp = follicle.getParent().getParent()
    follicle.getParent().setParent(controlRoot)
    pm.delete(focGp)
    pm.parentConstraint(dynamicBones[0],create_parent(controls[0]))
    hairSysMeta = as_meta(hairSys)
    hairSysMeta.connectChildren(
        [c.name() for c in controls],
        'boneControl', 'hairSystem', srcSimple=True)
    locs = []
    for ctl, dynamicBone in zip(controls[1:], dynamicBones[1:]):
        offset = create_parent(ctl)
        control_tagging(ctl, metaname='DynamicHairControlsSet_MetaNode')
        loc = connect_with_loc(dynamicBone, offset,all=True)[0]
        loc.getParent().setParent(dynamicBone.getParent())
        locs.append(loc)

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
    rootLoc.getParent().setParent(controlGp)
    if pm.objExists('ctlGp'):
        controlGp.setParent('ctlGp')
    else:
        pm.group(controlGp,name='ctlGp')
    if pm.objExists('miscGp'):
        hairMiscGp.setParent('miscGp')
    else:
        pm.group(hairMiscGp,name='miscGp')
    # add ctl tag
    control_tagging(controlRoot, metaname='DynamicHairControlsSet_MetaNode')

@ul.do_function_on()
def create_splineIK(bone, midCtls=2,addFK=False, addSway=False, simplifyCurve=False, customShape=None):
    bones = ul.recurse_collect(ul.iter_hierachy(bone, filter='joint'))
    if len(bones) < 2:
        log.warning('Bone Chains have less than 2 joints')
        return
    bonename = ul.get_name(bone)
    startBone = bones[0]
    endBone = bones[-1]
    ikhandle, ikeffector, ikcurve = pm.ikHandle(
        sj=startBone, ee=endBone,solver='ikSplineSolver', ns=3, scv=simplifyCurve)
    ikhandle.rename(bonename+'_ikhandle')
    ikeffector.rename(bonename+'_ikeffector')
    ikcurve.rename(bonename+'_ikCurve')
    #sbonetop.setParent(bone.getParent())
    boneTops = []
    ctls = []
    pncInfo = ul.get_points_on_curve(ikcurve, amount=midCtls)
    for i, (tr, rot) in enumerate(pncInfo):
        mboneTop = pm.nt.Joint(
                name = '{}_topBone_{:02d}'.format(bonename,i+1))
        mboneTop.rename(mboneTop.replace('__','_'))
        mboneTop.setParent(None)
        mboneTop.radius.set(1.1)
        mboneTop.setTranslation(tr)
        mboneTop.setRotation(rot)
        if i > 0:
            ctl = create_free_control(mboneTop,useLoc=True, customShape=customShape)
            ctls.append(ctl)
        else:
            create_parent(mboneTop)
        boneTops.append(mboneTop)
    endCtl = ctls[-1]
    endCtl.addAttr('roll', type='float',k=1)
    endCtl.roll >> ikhandle.roll
    endCtl.addAttr('twist', type='float',k=1)
    endCtl.twist >> ikhandle.twist

    # pm.select(boneTops,r=True)
    # pm.select(ikcurve,add=True)
    # curveSkin = pm.skinCluster(wd=1,dr=4,tsb=1)
    curveSkin = pm.skinCluster(*ul.recurse_collect(boneTops, ikcurve),wd=1,dr=4,tsb=1)
    if addFK:
        circleShape = ul.partial(
            createPinCircle,
            'control',
            axis='YZ',
            radius=2,
            step=8,
            sphere=False,
            length=0)
        endCtl.addAttr(
            'ikFkSwitch', type='float',
            defaultValue=1, minValue=0, maxValue=1, k=1)
        endCtl.ikFkSwitch >> ikhandle.ikBlend
        pCtls = create_parent_control(startBone, customShape=circleShape)
        endCtl.addAttr(
            'fkvis', type='bool', defaultValue=False, k=1
        )
    if addSway:
        endCtl.fkvis >> pCtls[0].getParent().visibility
        constraint_multi(pCtls[0], endCtl, constraintType='Aim')
        time = pm.PyNode('time1')
        mul = pm.nt.MultiplyDivide()
        ocontraint = endCtl.outputs(type='orientConstraint')[0]
        for at in ['X','Y','Z']:
            atName = 'swaySpeed%s'%at
            endCtl.addAttr(
                atName, type='float',
                defaultValue=0.1, minValue=0, k=1)
            time.outTime >> mul.attr('input1%s'%at)
            endCtl.attr(atName) >> mul.attr('input2%s'%at)
            mul.attr('output%s'%at) >> ocontraint.attr('offset%s'%at)
        # constraint_multi(en)
        ikmiscGp = group([ikcurve, ikhandle], grpname=bonename+'_ikMisc')
        bonGp = group([b.getParent() for b in boneTops], grpname=bonename+'_topBonGp')
        return (boneTops)

@ul.do_function_on()
def create_simpleIK(boneRoot, customShape=None):
    bones = ul.recurse_collect(ul.iter_hierachy(boneRoot, filter='joint'))
    if len(bones) < 2:
        log.warning('Bone Chains have less than 2 joints')
        return
    bonename = ul.get_name(boneRoot)
    startBone = bones[0]
    endBone = bones[-1]
    ikhandle, ikeffector = pm.ikHandle(
        sj=startBone, ee=endBone, ns=3)
    ikhandle.rename(bonename+'_ikhandle')
    ikeffector.rename(bonename+'_ikeffector')
    ctl = create_free_control(ikhandle, useLoc=True, customShape=customShape)
    ctl.addAttr('roll', type='float', k=1)
    ctl.roll >> ikhandle.twist
    return ctl

@ul.do_function_on(type_filter=['nurbsCurve'])
def create_stretchIK(inputcurve, ctlAmount=3, boneAmount=3):
    boneCVs = create_bone_on_curve(inputcurve, amount=boneAmount, parent=False)
    sphereShape = ul.partial(
        createPinCircle,
        'control',
        axis='YZ',
        radius=1,
        step=24,
        sphere=True,
        length=0)
    ctls =[]
    ctlLocs =[]
    for id,(bone,tr,loc) in enumerate(boneCVs):
        ctlLoc = loc.duplicate(po=True,rr=True)[0]
        connect_transform(loc, ctlLoc, all=True)
        ctl = create_free_control(bone, customShape=sphereShape)
        ctl.getParent().setParent(ctlLoc)
        ctls.append(ctl)
        ctlLocs.append(ctlLoc)
    boneTops = []
    topCtls = []
    pncInfo = ul.get_points_on_curve(inputcurve, amount=ctlAmount)
    for i, (tr, rot) in enumerate(pncInfo):
        pm.select(cl=True)
        mboneTop = pm.nt.Joint(
            name = 'topBone_{:02d}'.format(i+1),
            p=tr)
        mboneTop.setParent(None)
        mboneTop.radius.set(1.1)
        # mboneTop.setTranslation(tr)
        # mboneTop.setRotation(rot)
        ctl = create_free_control(mboneTop)
        topCtls.append(ctl)
        boneTops.append(mboneTop)
    curveSkin = pm.skinCluster(*ul.recurse_collect(boneTops, inputcurve),wd=1,dr=4,tsb=1)
    # topCtls[0].rotate >> ctls[0].getParent.rotate