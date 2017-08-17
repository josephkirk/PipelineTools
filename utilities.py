import pymel.core as pm
import pymel.util as pu
import pymel.util.path as pp
import maya.cmds as cm
import maya.mel as mm
import shutil
import os
import random as rand
import PipelineTools.customClass as cc
from functools import wraps
reload(cc)
### decorator
def error_alert(func):
    """print Error if function fail"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except (IOError, OSError) as why:
            print func.__name__, "create error:"
            print why
    return wrapper

def do_function_on(mode='single', type_filter=[]):
    def decorator(func):
        """wrap a function to operate on select object or object name string according to mode
                mode: single, double, set, singlelast, last, doubleType"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            sel = pm.selected()
            #pm.select(cl=True)
            for arg in args:
                if type(arg) == list:
                    sel.append(arg)
                else:
                    sel.extend(arg)
            #print args_list
            object_list = list(set(pm.ls(sel,type=type_filter)))
            if object_list:
                results = []
                if mode is 'single': # do function for every object in object_list
                    for ob in object_list:
                        result = func(ob, **kwargs)
                        results.append(result)
                elif mode is 'double': # do function for first in object_list to affect last
                    if len(object_list)>1:
                        result = func(sel[0], sel[-1], **kwargs)
                        results.append(result)
                    else:
                        pm.warning('Select two objects')
                elif mode is 'sets': # do function directly to object_list
                    result = func(object_list, **kwargs)
                    results.append(result)
                elif 'last' in mode: # set last object in object_list to affect others
                    if len(object_list)>1:
                        op_list = object_list[:-1]
                        target = object_list[-1]
                        if mode is 'singlelast':
                            for op in op_list:
                                result = func(op, target, **kwargs)
                                results.append(result)
                        else:
                            result = func(op_list, target, **kwargs)
                            results.append(result)
                    else:
                        pm.warning('Select affect objects then target object')
                elif mode is 'doubleType':
                    if len(object_list) > 1:
                        object_type2 = pm.ls(object_list,
                                             type=type_filter[-1],
                                             orderedSelection=True)
                        if object_type2:
                            object_type1 = [
                                object for object in pm.ls(object_list, type=type_filter[:-1])
                                if type(object) != type(object_type2[0])]
                            result = func(object_type1, object_type2, **kwargs)
                            results.append(result)
                        else:
                            pm.warning('Object type "%s" is not in selection or argument'
                                       %type_filter[-1])
                    else:
                        pm.warning('Select more than 2 object of 2 kind ',
                                   'and input those kind into type_filter keyword')
                return results
            else:
                pm.error('no object to operate on')
        return wrapper
    return decorator

###misc function
def convert_component(components_list, toVertex=True, toEdge=False, toFace=False):
    test_type = [o for o in components_list if type(o) is pm.nt.Transform]
    
    if test_type:
        converts = []
        for match in test_type:
            convert = match.getShape().vtx
            converts.append(convert)
        return converts
    converts = pm.polyListComponentConversion(components_list,
                                              fromFace=True, fromEdge=True, fromVertex=True,
                                              toFace=toFace, toEdge=toEdge, toVertex=toVertex)
    print converts
    return pm.ls(converts)

def remove_number(string):
    for index, character in enumerate(string):
        if character.isdigit():
            return (string[:index], int(string[index:] if string[index:].isdigit() else string[index:]))

def get_pos_center_from_edge(edge):
    if type(edge) == pm.general.MeshEdge:
        t_node = edge.node()
        verts_set= set()
        edge_loop_list = pm.ls(pm.polySelect(t_node, edgeLoop=edge.currentItemIndex(), ns=True, ass=True))
        for ed in edge_loop_list:
            unpack_edges = [t_node.e[edg] for edg in ed.indices()]
            for true_edge in unpack_edges:
                for vert in true_edge.connectedVertices():
                    verts_set.add(vert)
        vert_pos = sum([v.getPosition() for v in list(verts_set)])/len(verts_set)
        return vert_pos

def get_shape(ob):
    '''return shape from ob, if cannot find raise error'''
    if hasattr(ob, 'getShape'):
        return ob.getShape()
    else:
        if issubclass(ob.node().__class__, pm.nt.Shape):
            return ob.node()
        else:
            pm.error('object have no shape')

def get_skin_cluster(ob):
    '''return skin cluster from ob, if cannot find raise error'''
    ob_shape = get_shape(ob)
    try:
        shape_connections = ob_shape.listConnections(type=['skinCluster', 'objectSet'])
        for connection in shape_connections:
            if 'skinCluster' in connection.name():
                if type(connection) == pm.nt.SkinCluster:
                    return connection
                try_get_skinCluster = connection.listConnections(type='skinCluster')
                if try_get_skinCluster:
                    return try_get_skinCluster[0]
                else:
                    pm.error('Object have no skin bind')
    except:
        pm.error('Cannot get skinCluster from object')

###Rigging
@do_function_on(mode='singlelast')
def skin_weight_filter(ob, joint,min=0.0, max=0.1, select=False):
    '''return vertex with weight less than theshold'''
    skin_cluster = get_skin_cluster(ob)
    ob_shape = get_shape(ob)
    filter_weight = []
    for vtx in ob_shape.vtx:
        weight = pm.skinPercent(skin_cluster, vtx, query=True, transform=joint, transformValue=True)
        #print weight
        if min < weight <= max:
            filter_weight.append(vtx)
    if select:
        pm.select(filter_weight)
    return filter_weight

@do_function_on(mode='single')
def switch_skin_type(ob,type='classis'):
    type_dict = {
        'Classis':0,
        'Dual':1,
        'Blend':2}
    if not get_skin_cluster(ob) and type not in type_dict.keys():
        return
    skin_cluster = get_skin_cluster(ob)
    skin_cluster.setSkinMethod(type_dict[type])
    deform_normal_state = 0 if type_dict[type] is 2 else 1
    skin_cluster.attr('deformUserNormals').set(deform_normal_state)

@do_function_on(mode='doubleType', type_filter=['float3', 'transform', 'joint'])
def skin_weight_setter(component_list, joints_list, skin_value=1.0, normalized=True, hierachy=False):
    '''set skin weight to skin_value for vert in verts_list to first joint,
       other joint will receive average from normalized weight,
       can be use to set Dual Quarternion Weight'''
    def get_skin_weight():
        skin_weight = []
        if normalized:
            skin_weight.append((joints_list[0], skin_value))
            if len(joints_list) > 1:
                skin_normalized = (1.0-skin_value)/(len(joints_list)-1)
                for joint in joints_list[1:]:
                    skin_weight.append((joint, skin_normalized))
            return skin_weight
        for joint in joints_list:
            skin_weight.append((joint,skin_value))
        return skin_weight
    if hierachy:
        child_joint = joints_list[0].listRelatives(allDescendents=True)
        joints_list.extend(child_joint)
        print joints_list

    if any([type(component) is pm.nt.Transform for component in component_list]):
        for component in component_list:
            skin_cluster = get_skin_cluster(component)
            pm.select(component, r=True)
            pm.skinPercent(skin_cluster, transformValue=get_skin_weight())
            print component_list
        pm.select(component_list,joints_list)
    else:
        verts_list = convert_component(component_list)
        skin_cluster = get_skin_cluster(verts_list[0])
        if all([skin_cluster, verts_list, joints_list]):
            pm.select(verts_list)
            pm.skinPercent(skin_cluster, transformValue=get_skin_weight())
            pm.select(joints_list, add=True)
        #print verts_list
        #print skin_weight
        #skin_cluster.setWeights(joints_list,[skin])


@do_function_on(mode='sets', type_filter=['float3'])
def dual_weight_setter(component_list, weight_value=0.0, query=False):
    verts_list = convert_component(component_list)
    shape = verts_list[0].node()
    skin_cluster = get_skin_cluster(verts_list[0])
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
                skin_cluster.setBlendWeights(shape, shape.vtx[vert], [weight_value,weight_value])
        #     print skin_cluster.getBlendWeights(shape, vert)
        #pm.select(verts_list)
        #skin_cluster.setBlendWeights(shape, verts_list, [weight_value,])

@do_function_on(mode='single', type_filter=['float3', 'transform'])
def create_joint(ob_list):
    new_joints = []
    for ob in ob_list:
        if type(ob) == pm.nt.Transform:
            get_pos = ob.translate.get()
        elif type(ob) == pm.general.MeshVertex:
            get_pos = ob.getPosition(space='world')
        elif type(ob) == pm.general.MeshEdge:
            get_pos = get_pos_center_from_edges(ob)
        new_joint = pm.joint(p=get_pos)
        new_joints.append(new_joint)
    for new_joint in new_joints:
        pm.joint(new_joint, edit=True, oj='xyz', sao='yup', ch=True, zso=True)
        if new_joint == new_joints[-1]:
            pm.joint(new_joint, edit=True, oj='none', ch=True, zso=True)

@error_alert
@do_function_on(mode='single')
def insert_joint(joint, num_joint=2):
    og_joint = joint
    joint_child = joint.getChildren()[0] if joint.getChildren() else None
    joint_child.orientJoint('none')
    joint_name = remove_number(joint.name())
    if joint_child:
        distance = joint_child.tx.get()/(num_joint+1)
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
                pm.rename(bone, "%s%02d"%(joint_name[0], index+1))
            except:
                pm.rename(bone, "%s#"%joint_name[0])

@do_function_on(mode='double')
def parent_shape(src, target, delete_src=True):
    '''parent shape from source to target'''
    pm.parent(src.getShape(), target, r=True, s=True)
    if delete_src:
        pm.delete(src)

@do_function_on(mode='single')
def un_parent_shape(ob):
    '''unParent all shape and create new trasnform for each shape'''
    shapeList = ob.listRelatives(type=pm.nt.Shape)
    if shapeList:
        for shape in shapeList:
            newTr = pm.nt.Transform(name=(shape.name()[:shape.name().find('Shape')]))
            newTr.setMatrix(ob.getMatrix(ws=True), ws=True)
            pm.parent(shape, newTr, r=True, s=True)
    if type(ob) != pm.nt.Joint:
        pm.delete(ob)

@do_function_on(mode='double')
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

@do_function_on(mode='double')
def copy_skin_multi(source_skin_grp, dest_skin_grp):
    '''copy skin for 2 identical group hierachy'''
    source_skins = source_skin_grp.listRelatives(type='transform', ad=1)
    dest_skins = dest_skin_grp.listRelatives(type='transform', ad=1)
    if len(dest_skins) == len(source_skins):
        print '---Copying skin from %s to %s---'%(source_skin_grp, dest_skin_grp)
        for skinTR, dest_skinTR in zip(source_skins, dest_skins):
            if skinTR.name().split(':')[-1] != dest_skinTR.name().split(':')[-1]:
                print skinTR.name().split(':')[-1], dest_skinTR.name().split(':')[-1]
            else:
                try:
                    skin = skinTR.getShape().listConnections(type='skinCluster')[0]
                    dest_skin = dest_skinTR.getShape().listConnections(type='skinCluster')[0]
                    pm.copySkinWeights(ss=skin.name(), ds=dest_skin.name(),
                                       noMirror=True, normalize=True,
                                       surfaceAssociation='closestPoint',
                                       influenceAssociation='closestJoint')
                    dest_skin.setSkinMethod(skin.getSkinMethod())
                    print skinTR, 'copied to', dest_skinTR, '\n'
                except:
                    print '%s cannot copy skin to %s'%(skinTR.name(), dest_skinTR.name()), '\n'
        print '---Copy Skin Finish---'
    else:
        print 'source and target are not the same'
@error_alert
@do_function_on(mode='double')
def copy_skin_single(source_skin,dest_skin):
    '''copy skin for 2 object, target object do not need to have skin Cluster'''
    skin = source_skin.getShape().listConnections(type='skinCluster')[0]
    dest_skin = dest_skin.getShape().listConnections(type='skinCluster')[0]
    print skin,dest_skin
    pm.copySkinWeights(ss=skin.name(),ds=dest_skin.name(),
                       nm=True,nr=True,sm=True,sa='closestPoint',ia=['closestJoint','name'])
    dest_skin.setSkinMethod(skin.getSkinMethod())

@do_function_on(mode='double')
def parent_shape(src,target):
    if src.getShape():
        pm.parent(src.getShape(), target, r=True, s=True)
        pm.delete(src)

@do_function_on(mode='single')
def un_parent_shape(ob):
    shapeList = ob.listRelatives(type=pm.nt.Shape)
    if shapeList:
        for shape in shapeList:
            newTr = pm.nt.Transform(name=(shape.name()[:shape.name().find('Shape')]))
            newTr.setMatrix(ob.getMatrix(ws=True),ws=True)
            pm.parent(shape,newTr,r=True,s=True)
    if type(ob) != pm.nt.Joint:
        pm.delete(ob)

@do_function_on(mode='last')
def connect_joint(bones,boneRoot,**kwargs):
    for bone in bones:
        pm.connectJoint(bone, boneRoot, **kwargs)

@do_function_on(mode='single')
def create_roll_joint(oldJoint):
    newJoint = pm.duplicate(oldJoint,rr=1,po=1)[0]
    pm.rename(newJoint,('%sRoll1'%oldJoint.name()).replace('Left','LeafLeft'))
    newJoint.attr('radius').set(2)
    pm.parent(newJoint, oldJoint)
    return newJoint

@do_function_on(mode='single')
def create_sub_joint(ob):
    subJoint = pm.duplicate(ob,name='%sSub'%ob.name(),rr=1,po=1,)[0]
    new_pairBlend = pm.createNode('pairBlend')
    subJoint.radius.set(2.0)
    pm.rename(new_pairBlend,'%sPairBlend'%ob.name())
    new_pairBlend.attr('weight').set(0.5)
    ob.rotate >> new_pairBlend.inRotate2
    new_pairBlend.outRotate >> subJoint.rotate
    return (ob,new_pairBlend,subJoint)

@do_function_on(mode='single')
def reset_joint_orient(bone):
    if type(bone) != pm.nt.Joint:
        return
    attrList = ["jointOrientX", "jointOrientY", "jointOrientZ"]
    for at in attrList[:-1]:
        bone.attr(at).set(0)

@do_function_on(mode='single')
def add_suffix(ob,suff="_skinDeform"):
    pm.rename(ob,ob.name()+str(suff))

@do_function_on(mode='single')
def mirror_joint_tranform(bone, translate=False, rotate=True, **kwargs):
    #print bone
    opbone = get_opposite_joint(bone, customPrefix=(kwargs['customPrefix']if kwargs.has_key('customPrefix') else None))
    offset = 1
    if not opbone:
        opbone = bone
        offset = -1
        translate = False
    if all([type(b) == pm.nt.Joint for b in [bone, opbone]]):
        if rotate:
            pm.joint(opbone, edit=True, ax=pm.joint(bone, q=True, ax=True),
                     ay=pm.joint(bone, q=True, ay=True)*offset,
                     az=pm.joint(bone, q=True, az=True)*offset)
        if translate:
            bPos = pm.joint(bone, q=True, p=True)
            pm.joint(opbone, edit=True, p=(bPos[0]*-1, bPos[1], bPos[2]),
                     ch=kwargs['ch'] if kwargs.has_key('ch') else False,
                     co=not kwargs['ch'] if kwargs.has_key('ch') else True)

#@do_function_on
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
        for index,mp in enumerate(mirrorprefix):
            if mp in bone.name():
                opBoneName = bone.name().replace(mirrorprefix[index], mirrorprefix[index-1])
                opBone = pm.ls(opBoneName)[0] if pm.ls(opBoneName) else None
                if select:
                    if opBoneOnly:
                        pm.select(opBone)
                    else:
                        pm.select(bone, opBone)
                print opBoneName
                return opBone

def reset_bindPose():
    newbp = pm.dagPose(bp=True, save=True)
    bindPoses = pm.ls(type=pm.nt.DagPose)
    for bp in bindPoses:
        if bp != newbp:
            pm.delete(bp)

###function
@do_function_on(mode='single')
def set_material_attr(mat,mat_type='dielectric',**kwargs):
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

@do_function_on(mode='single')
def assign_curve_to_hair(abc_curve,hair_system="",preserve=False):
    '''assign Alembic curve Shape or tranform contain multi curve Shape to hairSystem'''
    curve_list = detach_shape(abc_curve, preserve=preserve)
    for curve in curve_list:
        hair_from_curve(curve,hair_system=hair_system)

def hair_from_curve(input_curve, hair_system="") :
    '''
    Assign curve to Hair System
    Modify Function from 
    Author: Tyler Hurd, www.tylerhurd.com '''
    print input_curve
    for attr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz'] :
        if 's' in attr and pm.getAttr('%s.%s'%(input_curve,attr)) != 1.0 :
            pm.warning('Transform values found! "%s.%s" is set to %s! Freeze transformations for expected results.'%(input_curve,attr,pm.getAttr('%s.%s'%(input_curve,attr))))
        elif not 's' in attr and pm.getAttr('%s.%s'%(input_curve,attr)) != 0 :
            pm.warning('Transform values found! "%s.%s" is set to %s! Freeze transformations for expected results.'%(input_curve,attr,pm.getAttr('%s.%s'%(input_curve,attr))))

    # duplicate driver curve for hair and follicle
    hair_curve = pm.rename(pm.duplicate(input_curve,rr=1),'%s_HairCurve'%input_curve)
    follicle = pm.rename(pm.createNode('follicle',ss=1,n='%s_FollicleShape'%input_curve).getParent(),'%s_Follicle'%input_curve)
    follicle.restPose.set(1)
    # if no hair system given create new hair system, if name given and it doesn't exist, give it that name
    if hair_system == '' :
        if pm.ls(type='hairSystem'):
            hair_system = pm.ls(type='hairSystem')[0]
        else:
            hair_system = pm.rename(pm.createNode('hairSystem',ss=1,n='%s_HairSystemShape'%input_curve).getParent(),'%s_HairSystem'%input_curve)
            pm.PyNode('time1').outTime >> hair_system.getShape().currentTime
            pm.select(hair_system)
            mm.eval('addPfxToHairSystem;')
    elif hair_system and not pm.objExists(hair_system) :
        hair_system = pm.rename(pm.createNode('hairSystem',ss=1,n='%sShape'%hair_system).getParent(),hair_system)
        pm.PyNode('time1').outTime >> hair_system.getShape().currentTime
        pm.select(hair_system)
        mm.eval('addPfxToHairSystem;')
    hair_system = pm.PyNode(hair_system)
    #hair_system = pm.PyNode(hair_system)
    hair_ind = len(hair_system.getShape().inputHair.listConnections())
    if not pm.objExists('%s_follicles'%hair_system):
        pm.group(name='%s_follicles'%hair_system)
    # connections
    pm.parent(input_curve,follicle)
    pm.parent(follicle,'%s_follicles'%hair_system)
    input_curve.getShape().worldSpace[0] >> follicle.getShape().startPosition
    follicle.getShape().outCurve >> hair_curve.getShape().create
    follicle.getShape().outHair >> hair_system.getShape().inputHair[hair_ind]
    hair_system.getShape().outputHair[hair_ind] >> follicle.getShape().currentPosition
    
    return [input_curve,hair_curve,follicle,hair_system]

#@do_function_on(mode='single')
def detach_shape(ob, preserve=False):
    '''detach Multi Shape to individual Object'''
    result= []
    if preserve:
        ob = pm.duplicate(ob, rr=True)[0]
    obShape = ob.listRelatives(type='shape')
    result.append(ob)
    if len(obShape)>1:
        for shape in obShape[1:]:
            transformName = "newTransform01"
            newTransform = pm.nt.Transform(name=transformName)
            pm.parent(shape, newTransform, r=1, s=1)
            result.append(newTransform)
    return result

def exportCam():
    '''export allBake Camera to FBX files'''
    FBXSettings = [
        "FBXExportBakeComplexAnimation -v true;"
        "FBXExportCameras -v true;"
        "FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager -v false;"
        "FBXProperty Export|AdvOptGrp|UI|GenerateLogData -v false;"
    ]
    for s in FBXSettings:
        mm.eval(s)
    excludedList = ['frontShape', 'sideShape', 'perspShape', 'topShape']
    cams = [
        (cam, pm.listTransforms(cam)[0])
        for cam in pm.ls(type='camera') if str(cam.name()) not in excludedList]
    scenePath = [str(i) for i in pm.sceneName().split("/")]
    stripScenePath = scenePath[:-1]
    sceneName = scenePath[-1]
    print sceneName
    filename = "_".join([sceneName[:-3], 'ConvertCam.fbx'])
    stripScenePath.append(filename)
    filePath = "/".join(stripScenePath)
    for c in cams:
        pm.select(c[1])
        oldcam = c[1]
        newcam = pm.duplicate(oldcam, rr=True)[0]
        startFrame = int(pm.playbackOptions(q=True, minTime=True))
        endFrame = int(pm.playbackOptions(q=True, maxTime=True))
        pm.parent(newcam, w=True)
        for la in pm.listAttr(newcam, l=True):
            attrName = '.'.join([newcam.name(), str(la)])
            pm.setAttr(attrName, l=False)
        camconstraint = pm.parentConstraint(oldcam, newcam)
        pm.bakeResults(newcam, at=('translate', 'rotate'), t=(startFrame, endFrame), sm=True)
        pm.delete(camconstraint)
        pm.select(newcam, r=True)
        cc = 'FBXExport -f "%s" -s' % filePath
        mm.eval(cc)

@do_function_on(mode='single')
def mirror_transform(obs, axis="x",xform=[0,4]):
    if not obs:
        print "no object to mirror"
        return
    axisDict = {
        "x":('tx', 'ry', 'rz', 'sx'),
        "y":('ty', 'rx', 'rz', 'sy'),
        "z":('tz', 'rx', 'ry', 'sz')}
    #print obs
    if type(obs) != list:
        obs = [obs]
    for ob in obs:
        if type(ob) == pm.nt.Transform:
            for at in axisDict[axis][xform[0]:xform[1]]:
                ob.attr(at).set(ob.attr(at).get()*-1)

@do_function_on(mode='last')
def transfer_material(obs, obSrc):
    try:
        obSrc_SG = obSrc.getShape().listConnections(type=pm.nt.ShadingEngine)[0]
    except:
        obSrc_SG = None
    if obSrc_SG:
        for ob in obs:
            set_material(ob,obSrc_SG)

#@do_function_on(mode='single')
def set_material(ob, SG):
    if type(SG) == pm.nt.ShadingEngine:
        try:
            pm.sets(SG,forceElement=ob)
        except:
            print "cannot apply %s to %s" % (SG.name(), ob.name())
    else:
        print "There is no %s" % SG.name()

@do_function_on(mode='single')
def lock_transform(ob,lock=True):
    for at in ['translate','rotate','scale']:
        ob.attr(at).set(lock=lock)

@do_function_on(mode='single')
def add_VrayOSD(ob):
    '''add Vray OpenSubdiv attr to enable smooth mesh render'''
    if str(pm.getAttr('defaultRenderGlobals.ren')) == 'vray':
        obShape = ob.getShape()
        pm.vray('addAttributesFromGroup', obShape, "vray_opensubdiv", 1)
        pm.setAttr(obShape+".vrayOsdPreserveMapBorders", 2)

@do_function_on(mode='single')
def clean_attr(ob):
    '''clean all Attribute'''
    for atr in ob.listAttr():
        try:
            atr.delete()
            print "%s is deleted" % atr.name()
        except:
            pass
####
@do_function_on(mode='set')
def find_instance(obs,instanceOnly=True):
    allTransform = [tr for tr in pm.ls(type=pm.nt.Transform) if tr.getShape()]
    instanceShapes =[]
    if instanceOnly:
        pm.select(cl=True)
    for ob in obs:
        obShape = ob.getShape()
        if obShape.name().count('|'):
            obShapeName = obShape.name().split('|')[-1]
            for tr in allTransform:
                shape = tr.getShape()
                if obShapeName == shape.name().split('|')[-1] and tr != ob:
                    #pm.select(ob,add=True)
                    instanceShapes.append(tr)
        #else:
            #print "%s have no Instance Shape" % ob
    pm.select(instanceShapes,add=True)
    return instanceShapes

def loc42Curve():
    sel = pm.selected()
    if len(sel)>3:
        posList = [o.translate.get() for o in sel]
        pm.curve(p=posList)

def randU(offset=0.1):
    sel=pm.selected()
    if not sel:
        return
    for o in sel:
        pm.polyEditUV(o.map,u=rand.uniform(-offset,offset))

def mirrorUV(dir='Left'):
    if dir=='Left':
        pm.polyEditUV(u=-0.5)
    else:
        pm.polyEditUV(u=0.5)
    pm.polyFlipUV()

def rotateUV():
    sel=pm.selected()
    for o in sel:
        selShape=o.getShape()
        pm.select(selShape.map,r=1)
        pm.polyEditUV(rot=1,a=180,pu=0.5,pv=0.5)
    pm.select(sel,r=1)

def getInfo():
    sel= pm.selected()[0]
    if not sel:
        return
    print type(sel)
    for a in dir(sel):
        print str(a)+": "
        try:
            print eval('sel.%s.__module__\n' % a)
            #print eval('sel.%s.__method__\n' % a)
            print eval('sel.%s.__doc__\n' % a)
        except:
            continue
        print ("-"*100+"\n")*2

def send_current_file(drive='N', version=1, verbose=True):
    src = pm.sceneName()
    todayFolder = pm.date(f='YYMMDD')
    if version>1:
        todayFolder = "_".join([todayFolder,
                               ('%02d' % version)])
    dest = src.replace(drive+':',
                       '%s:/to/%s' % (drive, todayFolder))
    try:
        checkDir(dest)
        pm.sysFile(src, copy=dest)
        if verbose:
            print "%s copy to %s" % (src,dest)
    except (IOError, OSError) as why:
        print "Copy Error"
        print why

def GetAssetPath(Assetname, versionNum):
    ''' get AssetPath Relate to Character'''
    try:
        CH = cc.Character(Assetname)
    except:
        print "get Asset not possible"
        return
    CHPath = {}
    CHPath['_common'] = pp(CH.texCommon)
    try:
        CHversion = CH[versionNum-1]
        if CHversion.path.has_key('..'):
            CHHairFiles = pp(CHversion.path['hair']).files('*.mb')
            if CHHairFiles:
                CHHairFiles.sort(key=os.path.getmtime)
                CHPath['hair'] = CHHairFiles[-1]
            if CHversion.path.has_key('clothes'):
                CHClothFiles = pp(CHversion.path['clothes']).files('*.mb')
                if CHClothFiles:
                    CHClothFiles.sort(key=os.path.getmtime)
                    CHPath['cloth'] = CHClothFiles[-1]
                    # print "No folder 'clothes' in %s " % CH.path
            try:
                CHPath['clothRender'] = CHversion.path['clothRender']
                CHPath['hairRender'] = CHversion.path['hairRender']
            except:
                pass
                # print "No folder 'render' in %s " % CHversion.path['..']
        if CHversion.texPath.has_key('..'):
            CHPath['tex'] = CHversion.texPath['..']
            for k in ['pattern','uv','zbr']:
                try:
                    CHPath[k] = pp(CHversion.texPath[k])
                except:
                    pass
                    # print "no folder '%s' in %s " % (k, CHPath['tex'])
    except (IOError, OSError) as why:
        print "Character %s has no version or \n\%s" % (Assetname,why)
    return CHPath

def sendFile(CH,
             ver,
             num=0,
             destdrive="",
             sendFile={
                 'Send':False,
                 'hair':False,
                 'cloth':False,
                 'xgen':False,
                 'uv':False,
                 'zbr':False,
                 'tex':False,
                 'pattern':False,
                 '_common':False}):
    '''send NS57 File'''
    def getDest(pa):
        paSplit = pa.splitall()[1:]
        projectSplit = pm.workspace.path.splitall()[1:-2]
        return "/".join([element for element in paSplit
                         if element not in projectSplit])
    def doCop(fodPath):
        if destdrive:
            drive = destdrive+":"
        else:
            drive = fodPath.drive
        dest = os.path.normpath("/".join([
            drive,
            "to",
            todayFolder,
            getDest(fodPath)]))
        #print fodPath,'-->',dest
        sysCop(fodPath, dest)
    def sendDir(k):
        if AllPath.has_key(k):
            doCop(pp(AllPath[k]))
        else:
            print "no %s folder" % k

    def sendTexFile(k):
        def copFiles(fileList):
            for t in fileList:
                doCop(t)
        if AllPath.has_key(k):
            try:
                # texFiles = [f for f in os.listdir(AllPath[k])
                #             if (os.path.isfile(os.path.join(AllPath[k],f))
                #                 and CH in f)]
                # texPath = r'%s' % unicode(AllPath[k])
                # print os.listdir(texPath)
                texFiles = [f for f in pp(AllPath[k]).files()
                        if (any([f.endswith(c) for c in ['jpg',
                                                         'png',
                                                         'tif',
                                                         'tiff']])
                            and CH in f.basename())]
                if texFiles:
                    copFiles(texFiles)
                else:
                    print "no Texture Files"
                psdDir = [d for d in pp(AllPath[k]).dirs()
                          if 'psd' in d]
                if psdDir:
                    psdDir = psdDir[0]
                    psdFiles = [f for f in psdDir.files()
                                if(any([f.endswith(c) for c in ['psd', 'psb']])
                                and CH in f.basename())]
                    copFiles(psdFiles)
                else:
                    print "no Psd Files"
            except (IOError, OSError) as why:
                #print AllPath[k] 
                print why
        else:
            print "no %s folder" % k
    if sendFile['cloth']:
        sendFile['clothRender'] = True
    if sendFile['hair']:
        sendFile['hairRender'] = True
    if sendFile['Send'] == True:
        AllPath = GetAssetPath(CH, ver)
        #print AllPath
        todayFolder = pm.date(f='YYMMDD')
        if num and num != 1:
            todayFolder = "_".join([todayFolder, ('%02d' % num)])
        for key, value in sendFile.iteritems():
            if key == 'tex' or key == '_common':
                if value and key == 'tex':
                    sendTexFile('tex')
                if value and key == '_common':
                    sendTexFile('_common')
            elif key != 'Send':
                if value:
                    sendDir(key)

def checkDir(pa,force=True):
    if not os.path.exists(os.path.dirname(pa)):
        os.makedirs(os.path.dirname(pa))
    else:
        if force:
            if os.path.isdir(pa):
                shutil.rmtree(os.path.dirname(pa))
                os.makedirs(os.path.dirname(pa))
            elif os.path.isfile(pa):
                os.remove(pa)
        else:
            print "%s exists" % pa
    print "checked"


def sysCop(src, dest):
    checkDir(dest)
    try:
        if os.path.isdir(src):
            shutil.copytree(src,dest)
            print "copying " + dest
            for file in os.listdir(dest):
                if os.path.isdir(src+"/"+file):
                    print "%s folder Copied" % file
                else:
                    print "%s file Copied" % file
        elif os.path.isfile(src):
            shutil.copy(src,dest)
            print "%s copied" % dest
        else:
            print "%s does not exist" % src
    except (IOError,OSError,WindowsError) as why:
        print src
        print dest
        print "Copy error\n",why


def setTexture():
    for m in oHairSG:
        fileList=[file for file in m.listConnections()
                  if type(file)==pm.nodetypes.File]
    for f in fileList:
        for d in f.listAttr():
            try:
                if d.longName(fullPath=False).lower().endswith('texturename'):
                    print d,d.get()
                    d.set(d.get().replace('KG','IB'))
                    print d.get()
            except:
                continue