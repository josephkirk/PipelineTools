#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""

import pymel.core as pm
import pymel.util as pu
import pymel.util.path as pp
import maya.cmds as cm
import maya.mel as mm
import shutil
import os
import random as rand
import asset_class as asset
from pymel.util.enum import Enum
from functools import wraps, partial
from time import sleep, time
import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

#reload(ac)

#global var
prefpath = 'C:/Users/nphung/Documents/maya/2017/prefs/userPrefs.mel'
### decorator
def timeit(func):
    """time a function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        t= time()
        result = func(*args, **kwargs)
        log.debug(func.__name__,'took: ',time()-t)
        return result
    return wrapper

def error_alert(func):
    """print Error if function fail"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            t=time()
            result = func(*args, **kwargs)
            log.info('{} OK and return {}, took: {}'.format(func.__name__, result, time()-t))
            return result
        except (IOError, OSError, pm.MayaNodeError, pm.MayaAttributeError, AssertionError, TypeError,AttributeError) as why:
            msg = []
            msg.append(''.join([
                func.__name__,':',
                '\nargs:\n',','.join([str(a) for a in args]),
                '\nkwargs:\n',','.join(['{}={}'.format(key,value) for key,value in kwargs.items()]),
                'create Error:']))
            for cause in why:
                msg.append(str(why))    
            msg = '\n'.join(msg)
            log.error(msg)
    return wrapper


def do_function_on(mode='single', type_filter=[], return_list=True):
    def decorator(func):
        """wrap a function to operate on select object or object name string according to mode
                mode: single, double, set, singlelast, last, doubleType"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if ((kwargs.has_key('clearSelect') and kwargs['clearSelect'] == True) or
                (kwargs.has_key('cl') and kwargs['cl'] == True)):
                pm.select(cl=True)
                try:
                    del kwargs['clearSelect']
                except:
                    pass
                try:
                    del kwargs['cl']
                except:
                    pass
            nargs = []
            for arg in args:
                if any([isinstance(arg,t) for t in [list, tuple, set]]):
                    nargs.extend(list(arg))
                else:
                    nargs.append(arg)
            args=nargs
            ########
            #Extend Arguments with selection object
            ########
            sel=[]
            for arg in args:
                if isinstance(arg,str):
                    arg = get_node(arg)
                if isinstance(arg,pm.PyNode):
                    sel.append(arg)
                    args.pop()
            sel.extend(pm.selected())
            object_list = []
            for ob in sel:
                try:
                    if type_filter:
                        assert any([isinstance(ob,typ) for type in type_filter]), '{} not match type {}'.format(ob,str(type_filter))
                except:
                    log.debug('{} not match type {}'.format(ob,str(type_filter)))
                    continue 
                if ob not in object_list:
                    object_list.append(ob) ### search if arg is valid object
            if not object_list:
                log.error('no object select')
                return
            #print object_list
            #print arg
            ##########
            #Define function mode
            ##########
            #@error_alert
            def do_single(): # do function for every object in object_list
                #print object_list
                for ob in object_list:
                    print ob
                    yield func(ob,*args, **kwargs)
            #@error_alert
            def do_hierachy(): # do function for every object and childs in object_list
                for ob in object_list:
                    ob_list = [ob]
                    ob_list.extend(ob.getChildren(allDescendents=True))
                    for obchild in ob_list:
                        yield func(obchild,*args, **kwargs)
            #@error_alert
            def do_double(): # do function for first in object_list to affect last
                if len(object_list)>1:
                    yield func(sel[0], sel[-1],*args, **kwargs)
            #@error_alert
            def do_set(): # do function directly to object_list
                return func(object_list,*args, **kwargs)
            #@error_alert
            def do_last(singlelast=False): # set last object in object_list to affect others
                if len(object_list)>1:
                    op_list = object_list[:-1]
                    target = object_list[-1]
                    if singlelast is True:
                        for op in op_list:
                            yield func(op, target,*args, **kwargs)
                    else:
                        yield func(op_list, target,*args, **kwargs)
            #@error_alert
            def do_double_type(): # like 'last' mode but last object must be a different type from other
                if len(object_list) > 1:
                    object_type2 = pm.ls(
                        object_list,
                        type=type_filter[-1],
                        orderedSelection=True)
                    if object_type2:
                        object_type1 = [
                            object for object in pm.ls(object_list, type=type_filter[:-1])
                            if type(object) != type(object_type2[0])]
                        yield func(object_type1, object_type2,*args, **kwargs)
            ########
            #Define function mode dict
            ########
            function_mode = {
                'single':do_single,
                'set':do_set,
                'hierachy':do_hierachy,
                'double': do_double,
                'last': do_last,
                'singlelast': partial(do_last, True),
                'doubletype': do_double_type
            }
            ########
            #Return function result
            ########
            result = function_mode[mode]()
            if return_list and result:
                return [r for r in list(result) if r!=None]
            else:
                return result
        return wrapper
    return decorator

###misc function
def reloadTexture(udim=True):
    mm.eval('AEReloadAllTextures;')
    if udim:
        mm.eval('generateAllUvTilePreviews;')

def list_join(*args):
    newList = []
    for arg in args:
        if type(arg) is not list:
            arg = list(arg)
        newList.extend(arg)
    return newList

@error_alert
def assert_key(key,message, **kws):
    assert kws.has_key, message

@error_alert
def assert_type(ob, typelist=[]):
    assert(any([isinstance(ob, typ) for typ in typelist])),"Object %s does not match any in type:%s"%(ob, ",".join([str(t) for t in typelist]))
    #return ''.join([ob,'match one of:',','.join(types)])

####misc function 
def offcastshadow(wc='*eyeref*'):
    ob_list = pm.ls(wc,s=True)
    for ob in ob_list:
        eye.castsShadows.set(False)

def clean_userprefs(path_to_userprefs=prefpath, searchlines=[1000, 3000]):
    '''
    Disappearing shelf buttons in Maya 2016 and up?

    One reason for disappearing shelf buttons its entry exists multiple times in userPrefs.mel
    what confuses the loading. There might be a shelf entry with ; at the end and one without. Both valid
    but overwriting each other.

    This script runs through the .mel file and tries to remove any line with duplicates.
    Besides "shelfName" entries that are filtered are associated "shelfVersion", "shelfFile", "shelfLoad and
    "shelfAlign" entries
    Args:
        path_to_userprefs: file path to userPrefs.mel. Windows usually "C:/Users/username/Documents/maya/20xx/prefs/userPrefs.mel"
        searchlines:
            Limited to speed up script, if you need to modify will depend on  our file.
            Start and end line of  to process for search process. You can search "shelf" in userPrefs.mel
            in text editor to find the section
    Usage:
        Run the script, then reopen shelf (or restart maya)

        import mo_Utils.mo_fileSystemUtils as sysUtils
        sysUtils.clean_disappearingshelf_userprefs("C:/Users/monika/Documents/maya/2017/prefs/userPrefs.mel", searchlines=[2000, 2200])

    Returns: Error warning text or True

    '''
    if not os.path.isfile(path_to_userprefs):
        return pm.warning('Error. File not found (%s). Windows usually '
                          '"C:/Users/username/Documents/maya/20xx/prefs/userPrefs.mel"'%path_to_userprefs)

    # start and end line to filter search
    startline = searchlines[0]
    endline = searchlines[1]
    filepath = path_to_userprefs
    filepathnew = filepath.split('.mel')[0] + "New.mel"

    # this can be turned off for debugging and will leave the filtered file as filepath New.mel
    replace_with_backup=True

    # create new file
    open(filepathnew, "w+").close()

    with open(filepath, "r") as f, open(filepathnew, "a") as fnew:
        data = f.readlines()
        shelf_files = []
        skip_indices = []
        i = startline

        # - # find duplicates by looking for shelfName entries with same value
        # - # we store the shelf index as an int so we can also find and remove other linked
        # - # entries like shelfVersion and shelfFile
        for line in data[startline:endline]:
            words = line.split()
            if len(words) > 1:
                if words[1][1:10] == 'shelfName':
                    shelf_file = words[2].split('"')[1]

                    if shelf_file not in shelf_files:
                        print 'adding' + shelf_file
                        shelf_files.append(shelf_file)
                    else:
                        skip_indices.append(int(filter(str.isdigit, words[1])))  # add skip number

        # if no items were added to skip_indices, there i nothing to remove so we exit
        if len(skip_indices) == 0 :
            print 'No duplicate entries found. Try deleting and restoring the affected shelf manually.'
            os.remove(filepathnew)
            return False

        # - # adding the 1. block (till the startline) to the new file
        for line in data[:startline]:
            fnew.writelines(line)

        # - # 2. block, for each line, check for other setting for this shelf we need to remove via the Index
        # - # if it is not a duplicate we append the line to the new file
        for line in data[startline:endline]:
            skipline = False
            words = line.split()
            if len(words) > 1:
                if "shelfFile" in words[1] or "shelfAlign" in words[1] or "shelfLoad" in words[1] or "shelfVersion" in \
                        words[1] or "shelfName" in words[1]:
                    nrsearch = int(filter(str.isdigit, words[1]))
                    for sl in skip_indices:
                        if nrsearch == sl:
                            skipline = True

            # write if not skipping
            if skipline is False:
                fnew.writelines(line)
            else:
                print 'Duplicate found. Removing line %s' % words

            i += 1

        # - # adding the 3. block (everything after endline) to the new file
        for line in data[endline:]:
            fnew.writelines(line)

    # - # rename, backup old file .melOld
    if replace_with_backup:
        filepathold = filepath.split('.mel')[0] + ".melOld"
        os.rename(filepath, filepathold)
        os.rename(filepathnew, filepath)

    print 'Done. Removed %s duplicates. \n' \
          'New file: %s \nOld file backup: %s'%(len(skip_indices), filepath, filepathold)

    return True

def reset_floating_window():
    '''reset floating window position'''
    window_list = pm.lsUI(windows=True)
    for window in window_list:
        if window != "MayaWindow" and window != "scriptEditorPanel1Window":
            pm.deleteUI(window)
            pm.windowPref(window, remove=True)
            print window, " reset"

def add_suffix(ob, suff="_skinDeform"):
    pm.rename(ob, ob.name()+str(suff))

#### utility function
@error_alert
def get_closest_component(ob, mesh_node, uv=True, pos=False):
    ob_pos = ob.getTranslation(space='world')
    closest_info = get_closest_info(ob,mesh_node)
    closest_vert_pos = closest_info['Closest Vertex'].getPosition(space='world')
    closest_components = [closest_vert_pos, closest_info['Closest Mid Edge']]
    distance_cmp = [ob_pos.distanceTo(cp) for cp in closest_components]
    if distance_cmp[0] < distance_cmp[1]:
        result = closest_info['Closest Vertex']
        if pos:
            result = result.getPosition(space='world')
            uv = False
        if uv:
            vert_uv = pm.polyListComponentConversion(result,fv=True, tuv=True)
            result = pm.polyEditUV(vert_uv,q=True)
    else:
        result = closest_info['Closest Edge']
        if pos:
            result = closest_info['Closest Mid Edge']
            uv = False
        if uv:
            edge_uv = pm.polyListComponentConversion(result,fe=True, tuv=True)
            edge_uv_coor = pm.polyEditUV(edge_uv,q=True)
            mid_edge_uv = ((edge_uv_coor[0] + edge_uv_coor[2])/2,(edge_uv_coor[1] + edge_uv_coor[3])/2)
            result = mid_edge_uv
    return result
@error_alert
def get_closest_info(ob, mesh_node):
    if not isinstance(ob, pm.nt.Transform):
        return
    ob_pos = ob.getTranslation(space='world')
    mesh_node = get_shape(pm.PyNode(mesh_node))
    temp_node = pm.nt.ClosestPointOnMesh()
    temp_loc = pm.spaceLocator(p=ob_pos)
    mesh_node.worldMesh[0] >> temp_node.inMesh
    temp_loc.worldPosition[0] >> temp_node.inPosition
    temp_loc.worldMatrix[0] >> temp_node.inputMatrix
    #temp_node.inPosition.set(ob_pos)
    results = {}
    results['Closest Vertex'] = mesh_node.vtx[temp_node.closestVertexIndex.get()]
    results['Closest Face'] = mesh_node.f[temp_node.closestFaceIndex.get()]
    edges = results['Closest Face'].getEdges()
    mid_point_list = [
        (mesh_node.e[edge],
        (mesh_node.e[edge].getPoint(0, space='world')+mesh_node.e[edge].getPoint(1, space='world'))/2)
        for edge in edges]
    
    distance = [(mid_point[0], mid_point[1], ob_pos.distanceTo(mid_point[1])) for mid_point in mid_point_list]
    distance.sort(key=lambda d:d[2])
    results['Closest Edge'] = distance[0][0]
    results['Closest Mid Edge'] = distance[0][1]
    results['Closest Point'] = mesh_node.getClosestPoint(pm.dt.Point(ob_pos), space='world')[0]
    #closest_uv = mesh_node.getUVAtPoint(results['Closest Point'], space='world', uvSet=mesh_node.getCurrentUVSetName())
    #print closest_uv
    #results['Closest UV'] = closest_uv
    results['Closest UV'] = (temp_node.parameterU.get(), temp_node.parameterV.get())
    pm.delete([temp_node,temp_loc])
    return results

@error_alert
def get_node(node_name, unique_only=True, type_filter=None, verpose=False):
    msg=[]
    try:
        if unique_only:
            assert(pm.uniqueObjExists(node_name)),"object name %s is not unique or not exist"%node_name
            node = pm.PyNode(node_name)
            if type_filter:
                assert(isinstance(node, type_filter)),'node %s with %s does not exist' %(node_name,type_filter)
            msg.append("%s exists, is type %s" % (node, type(node)))
            return node
        else:
            node = pm.ls('*%s*'%node_name, type=type_filter) 
            msg.append("found %d object:" % (len(node)))
            for n in node:
                msg.append(node.name())
        return node
    except pm.MayaNodeError:
        msg.append('node %s does not exist' % node_name)
    except pm.MayaAttributeError:
        msg.append('Attibute %s does not exist' % node_name)
    except AssertionError as why:
        msg.append(why)
    if verpose:
        print '/n'.join(msg)

@error_alert
def get_skin_cluster(ob):
    '''return skin cluster from ob, if cannot find raise error'''
    ob_shape = get_shape(ob)
    try:
        shape_connections = ob_shape.listConnections(type=['skinCluster', 'objectSet'])
        for connection in shape_connections:
            if 'skinCluster' in connection.name():
                if isinstance(connection, pm.nt.SkinCluster):
                    return connection
                try_get_skinCluster = connection.listConnections(type='skinCluster')
                if try_get_skinCluster:
                    return try_get_skinCluster[0]
                else:
                    msg = '{} have no skin bind'.format(ob)
                    return pm.error(msg)
    except:
        msg = 'Cannot get skinCluster from {}'.format(ob)
        return pm.error(msg)

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
        try:
            if issubclass(ob.node().__class__, pm.nt.Shape):
                return ob.node()
        except:
            print('object have no shape')

###function
@do_function_on('singlelast')
def snap_nearest(ob, mesh_node):
    closest_component_pos = get_closest_component(ob, mesh_node, uv=False, pos=True)
    ob.setTranslation(closest_component_pos,'world')

@do_function_on(mode='single',type_filter=['float3'])
def convert_edge_to_curve(edge):
    pm.polySelect(edge.node(), el=edge.currentItemIndex())
    pm.polyToCurve(degree=1)
@do_function_on('single')
def reset_transform(ob):
    for atr in ['translate', 'rotate', 'scale']:
        reset_value = [0,0,0] if atr is not 'scale' else [1,1,1]
        ob.attr(atr).set(reset_value)

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

def hair_from_curve(input_curve, hair_system=""):
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

@error_alert
@do_function_on(mode='double')
def parent_shape(src, target, delete_src=True, delete_oldShape=True):
    '''parent shape from source to target'''
    #pm.parent(src, world=True)
    pm.makeIdentity(src, apply=True)
    pm.delete(src.listRelatives(type='transform'))
    pm.refresh()
    pm.parent(src.getShape(), target, r=True, s=True)
    print target
    if delete_src:
        pm.delete(src)
    if delete_oldShape:
        pm.delete(get_shape(target), shape=True)

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
def lock_transform(ob, lock=True, pivotToOrigin=True):
    for at in ['translate','rotate','scale','visibility','tx','ty','tz','rx','ry','rz','sx','sy','sz']:
        ob.attr(at).unlock()
    if pivotToOrigin:
        pm.makeIdentity(ob, apply=True)
        pm.xform(ob,pivots=(0,0,0),ws=True,dph=True,ztp=True)
    if lock is True:
        for at in ['translate','rotate','scale']:
            ob.attr(at).lock()

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
    for atr in ob.listAttr(ud=True):
        try:
            atr.delete()
            print "%s is deleted" % atr.name()
        except:
            pass

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

@do_function_on()
@error_alert
def getInfo(ob):
    print ob.name()
    for mod in dir(ob):
        print mod
        print ("-"*100+"\n")*2

def send_current_file(scene=True,suffix='_vn', lastest=True, render=False, tex=True, extras=['psd','uv', 'zbr', 'pattern'], version=1, verbose=True):
    src = pm.sceneName()
    scene_src = src.dirname()
    status = []
    todayFolder = pm.date(f='YYMMDD')
    if version>1:
        todayFolder = "{}_{:02d}".format(todayFolder,int(version))
    status.append('Send File to {}'.format(todayFolder))
    scene_dest = pm.util.path(scene_src.replace('Works','to/{}/Works'.format(todayFolder))).truepath()
    files = scene_src.files('*.mb')
    files.extend(scene_src.files('*.ma'))
    #print files
    files.sort(key=lambda f:f.getmtime())
    lastestfile = files[-1]
    try:
        status.append('Scene Sending status:')
        if lastest:
            src = lastestfile
            status.append('send latest file')
        dest = scene_dest.__div__(src.basename().replace(src.ext,'{}{}'.format(suffix, src.ext)))
        if scene:
            checkDir(dest)
            pm.sysFile(src, copy=dest)
            status.append("%s copy to %s" % (src,dest))
        if render:
            render_str = ['rend','Render','render','Rend']
            rend_src = []
            print src.dirname().dirs()
            for test_str in render_str:
                for dir in src.dirname().dirs():
                    if test_str in dir.basename():
                        print dir.basename()
                        rend_src = dir
                        break
                break
            if rend_src:
                rend_dest = dest.dirname().__div__(test_str)
                status.append(sysCop(rend_src, rend_dest))
    except (IOError, OSError, shutil.Error) as why:
        msg = "Scene Copy Error\n{}".format(','.join(why))
        status.append(msg)
    if tex or extras:
        if all([src.dirname().dirname().dirname().basename() != d for d in ['CH','BG','CP']]) and src.dirname().dirname().basename()!='CP': 
            scene_src = scene_src.dirname()
            scene_dest = scene_dest.dirname()
            print scene_src
        tex_src = pm.util.path(scene_src.replace('scenes','sourceimages')).truepath()
        tex_files = tex_src.files('*.jpg')
        tex_extra = {}
        for extra in extras:
            tex_extra[extra] = tex_src.__div__(extra)
        tex_dest = pm.util.path(scene_dest.replace('scenes','sourceimages'))
        status.append('Texture Sending status:')
        try:
            if tex:
                for tex_file in tex_files:
                    src = tex_file
                    dest = tex_dest.__div__(tex_file.basename())
                    checkDir(dest)
                    pm.sysFile(src, copy=dest)
                    status.append("%s copy to %s" % (src,dest))
            if extras:
                for name, path in tex_extra.items():
                    status.append('%s Sending status:'%name)
                    dest = tex_dest.__div__(name)
                    status.append(sysCop(path,dest))
        except (IOError, OSError, shutil.Error) as why:
            msg = "Tex Copy Error:\n{}".format(','.join(why))
            status.append(msg)
    pm.informBox(title='Send File Status', message = '\n'.join(status))

def GetAssetPath(Assetname, versionNum):
    ''' get AssetPath Relate to Character'''
    try:
        CH = asset.Character(Assetname)
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
    msg = []
    if not os.path.exists(os.path.dirname(pa)):
        os.makedirs(os.path.dirname(pa))
        msg.append("create directory %s"%pa)
    else:
        if force:
            if os.path.isdir(pa):
                shutil.rmtree(os.path.dirname(pa))
                os.makedirs(os.path.dirname(pa))
                msg.append("forcing remove and create directory %s"%pa)
            elif os.path.isfile(pa):
                os.remove(pa)
                msg.append("forcing remove %s"%pa)
        else:
            msg.append("%s exists"%pa)
    return '\n'.join(msg)

def sysCop(src, dest):
    checkDir(dest)
    status =[]
    try:
        if os.path.isdir(src):
            shutil.copytree(src,dest)
            msg = "copying " + dest
            status.append(msg)
            for file in os.listdir(dest):
                if os.path.isdir(src+"/"+file):
                    msg = "%s folder Copied" % file
                    status.append(msg)
                else:
                    msg = "%s file Copied" % file
                    status.append(msg)
        elif os.path.isfile(src):
            shutil.copy(src,dest)
            msg = "%s copied" % dest
            status.append(msg)
        else:
            msg = "%s does not exist" % src
            status.append(msg)
    except (IOError,OSError,WindowsError) as why:
        msg = 'Copy Error\n{} to {}\n{}'.format(src,dest,why)
        status.append(msg)
    return ','.join(status)


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