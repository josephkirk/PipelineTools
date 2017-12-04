#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymel.core as pm
import pymel.util as pu
import pymel.util.path as pp
import maya.cmds as cm
import maya.mel as mm
import shutil
import os
import types
import random as rand
from pymel.util.enum import Enum
import maya.OpenMayaUI as OpenMayaUI
from PySide2 import QtCore, QtWidgets
from pymel.core.uitypes import pysideWrapInstance as wrapInstance
from functools import wraps, partial
from time import sleep, time
import logging
from string import ascii_uppercase as alphabet

# Logging initialize #

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# Global var #

prefpath = 'C:/Users/nphung/Documents/maya/2017/prefs/userPrefs.mel'

# Global misc function #

def reload_texture(udim=True):
    mm.eval('AEReloadAllTextures;')
    if udim:
        mm.eval('generateAllUvTilePreviews;')

def get_maya_window():
    '''Return QMainWindow for the main maya window'''
    winptr = OpenMayaUI.MQtUtil.mainWindow()
    if winptr is None:
        raise RuntimeError('No Maya window found.')
    window = wrapInstance(winptr)
    assert isinstance(window, QtWidgets.QMainWindow)
    return window

def clean_userprefs(path_to_userprefs=prefpath, searchlines=[1000, 3000]):
    '''
    Disappearing shelf buttons in Maya 2016 and up?

    One reason for disappearing shelf buttons its entry exists
    multiple times in userPrefs.mel what confuses the loading.
    There might be a shelf entry with ;
    at the end and one without. Both valid
    but overwriting each other.

    This script runs through the .mel file and
    tries to remove any line with duplicates.
    Besides "shelfName" entries that are filtered are associated
    "shelfVersion", "shelfFile", "shelfLoad and "shelfAlign" entries
    Args:
        path_to_userprefs: file path to userPrefs.mel.
        Windows usually "C:/Users/username/Documents/maya/20xx/prefs/userPrefs.mel"
        searchlines:
            Limited to speed up script, if you need to modify will depend on  our file.
            Start and end line of  to process for search process.
            You can search "shelf" in userPrefs.mel
            in text editor to find the section
    Usage:
        Run the script, then reopen shelf (or restart maya)

        import mo_Utils.mo_fileSystemUtils as sysUtils
        sysUtils.clean_disappearingshelf_userprefs(
            "C:/Users/monika/Documents/maya/2017/prefs/userPrefs.mel", searchlines=[2000, 2200])

    Returns: Error warning text or True

    '''
    if not os.path.isfile(path_to_userprefs):
        return pm.warning('Error. File not found (%s). Windows usually '
                          '"C:/Users/username/Documents/maya/20xx/prefs/userPrefs.mel"'% \
                          path_to_userprefs)

    # start and end line to filter search
    startline = searchlines[0]
    endline = searchlines[1]
    filepath = path_to_userprefs
    filepathnew = filepath.split('.mel')[0] + "New.mel"

    # this can be turned off for debugging and will leave the filtered file as filepath New.mel
    replace_with_backup = True

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

# Decorators #

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
            raise
    return wrapper

def do_function_on(mode='single', type_filter=[]):
    """Decorator that feed function with selected object
    :Parameter mode: String indicate how to feed selecled object
        to function. Valid String value is:
            'single': feed each selected object to function
            'oneToOne': feed first and last selected to function
            'hierachy': feed all children of selected object to function
            'set': feed selected objects as a list to function
            'singlelast': feed each selected object
                that is not the last selected and
                the last selected object to function
            'last': feed a list of selected object
                that is not the last selected and
                the last selected object to function
            'lastType': feed each member of 2 sets of different type
            'multitype': feed list of object of different type
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # test keywords for 'selected' or 'sl' keyword
            try:
                selected = kwargs['selected']
            except KeyError:
                try:
                    selected = kwargs['sl']
                except KeyError:
                    # both 'selected' and 'sl' are not found in keyword
                    return func(*args, **kwargs)
            for k in ['selected', 'sl']:
                try:
                    del kwargs[k]
                except:
                    pass
            if not selected:
                # if selected keyword are False
                return func(*args, **kwargs)
            # get selected object as PyNode
            object_list = pm.selected(type=type_filter)
            if not object_list:
                log.error('No selected objects or type input in type_filter is unknown!')
                raise
            ##########
            #Define function mode
            ##########

            def do_single():
                '''Feed function with each valid selected object and yield result'''
                for ob in object_list:
                    yield func(ob, *args, **kwargs)

            def do_hierachy():
                '''Feed function with each object and all its childrens and yield result'''
                for ob in object_list:
                    print ob
                    for child in iter_hierachy(ob):
                        print child
                        yield func(child, *args, **kwargs)

            def do_one_to_one():
                '''Feed function with a set of first and last selected object and yield result'''
                if len(object_list)%2:
                    msg = 'Selected Object Count should be power of 2.\n \
                           Current Object Counts:%d'%(len(object_list))
                    log.warning(msg)
                    raise RuntimeWarning(msg)
                objects_set1 = [o for id, o in enumerate(object_list)
                                if id%2]
                objects_set2 = [o for id, o in enumerate(object_list)
                                if not id%2]
                for ob1, ob2 in zip(objects_set1, objects_set2):
                    yield func(ob1, ob2, *args, **kwargs)

            def do_set():
                '''Feed function directly with list of selected objects'''
                return func(object_list, *args, **kwargs)

            def do_to_last(singlelast=False):
                '''Feed function list of selected objects before the last select object and
                the last object'''
                if len(object_list) < 2:
                    msg = 'Select more than two objects!'
                    log.error(msg)
                    raise RuntimeWarning(msg)
                op_list = object_list[:-1]
                target = object_list[-1]
                if singlelast:
                    for op in op_list:
                        yield func(op, target, *args, **kwargs)
                else:
                    yield func(op_list, target, *args, **kwargs)

            def do_to_last_type():
                '''like 'last' mode but last object must be a different type from other'''
                if len(object_list) < 2 or len(type_filter) < 2:
                    msg = 'Select more than two objects of diffent type!'
                    log.error(msg)
                    raise RuntimeWarning(msg)
                source_type_set = [o for o in object_list if o.nodeType() !=  type_filter[-1]]
                target_type_set = [o for o in object_list if o.nodeType() == type_filter[-1]]
                return func(source_type_set, target_type_set,*args, **kwargs)

            def do_different_type():
                '''like 'last' mode but last object must be a different type from other'''
                if len(object_list) < 2 or len(type_filter) < 2:
                    log.error('Select more than two objects of diffent type!')
                    raise
                obtype_list = []
                for t in type_filter:
                    obtype_list.append([o for o in object_list if o.nodeType() == t])
                for ob_set in zip(*nargs):
                    nargs = list(ob_set)
                    nargs.append(args)
                    yield func(*nargs, **kwargs)
            ########
            #Define function mode dict
            ########
            function_mode = {
                'single':do_single,
                'set':do_set,
                'hierachy':do_hierachy,
                'oneToOne': do_one_to_one,
                'last': do_to_last,
                'singleLast': partial(do_to_last, True),
                'lastType': do_to_last_type,
                'multitype': do_different_type,
            }
            ########
            #Return function result
            ########
            result = function_mode[mode]()
            if isinstance(result, types.GeneratorType):
                result = list(result)
            log.debug('%s Wrap by do_function_on decorator and return %s'%(func.__name__,str(result)))
            return result
        return wrapper
    return decorator

# Utility functions #
# --- Path --- #

def send_current_file(
    scene=True,
    suffix='_vn',
    lastest=True,
    render=False,
    tex=True,
    extras=['psd','uv', 'zbr', 'pattern'],
    version=1,
    verbose=True):
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
            check_dir(dest)
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
                status.append(sys_cop(rend_src, rend_dest))
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
                    check_dir(dest)
                    pm.sysFile(src, copy=dest)
                    status.append("%s copy to %s" % (src,dest))
            if extras:
                for name, path in tex_extra.items():
                    status.append('%s Sending status:'%name)
                    dest = tex_dest.__div__(name)
                    status.append(sys_cop(path,dest))
        except (IOError, OSError, shutil.Error) as why:
            msg = "Tex Copy Error:\n{}".format(','.join(why))
            status.append(msg)
    pm.informBox(title='Send File Status', message = '\n'.join(status))

def check_dir(pa,force=True):
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

def sys_cop(src, dest):
    check_dir(dest)
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

# --- Query Infos --- #

@error_alert
def get_name(ob):
    assert hasattr(ob,'name'), 'Cannot get name for %s'%ob
    return ob.name().split('|')[-1] 

@error_alert
def recurse_hierachy(root, callback,*args,**kwargs):
    '''Recursive do a callback function'''
    def recurse(node):
        callback(node,*args,**kwargs)
        for child in node.getChildren(type='transform'):
            recurse(child)
    recurse(root)

#@error_alert
def iter_hierachy(root):
    '''yield hierachy generator object with stack method'''
    stack = [root]
    level = 0
    while stack:
        level +=1
        node = stack.pop()
        yield node
        childs = node.getChildren( type='transform' )
        if len(childs) > 1:
            log.debug('\nsplit to %s, %s'%(len(childs),str(childs)))
            for child in childs:
                subStack = iter_hierachy(child)
                for subChild in subStack:
                    yield subChild
        else:
            stack.extend( childs )

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

@error_alert
def get_shape(ob):
    '''return shape from ob, if cannot find raise error'''
    try:
        return ob.getShape()
    except AttributeError:
        try:
            assert issubclass(ob.node().__class__, pm.nt.Shape)
            return ob.node()
        except AttributeError, AssertionError:
            log.error('%s have no shape'%ob)
            raise

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

# --- Transformation and Shape --- #

def rename( ob, prefix="", suffix="" , separator='_'):
    try:
        pm.PyNode(ob)
    except pm.MayaNodeError as why:
        if pm.ls(ob):
            warning_msg = \
                'Scenes contain %d with name %s'%(
                     len(pm.ls(ob)), ob )
            log.warning( [why, warning_msg] )
            for o in pm.ls(ob):
                try:
                   o.rename(separator.join([prefix, ob, suffix]))
                except AttributeError:
                    log.error("Can't perform rename for %s"%o)
                    raise

def remove_number(string):
    for index, character in enumerate(string):
        if character.isdigit():
            return (string[:index], int(string[index:] if string[index:].isdigit() else string[index:]))

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

def convert_edge_to_curve(edge):
    pm.polySelect(edge.node(), el=edge.currentItemIndex())
    pm.polyToCurve(degree=1)

def snap_nearest(ob, mesh_node):
    closest_component_pos = get_closest_component(ob, mesh_node, uv=False, pos=True)
    ob.setTranslation(closest_component_pos,'world')

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

def lock_transform(
        ob,
        lock=True,
        pivotToOrigin=True):
    '''reset pivot to 0 and toggle transform lock'''
    for at in ['translate','rotate','scale','visibility','tx','ty','tz','rx','ry','rz','sx','sy','sz']:
        ob.attr(at).unlock()
    if pivotToOrigin:
        pm.makeIdentity(ob, apply=True)
        pm.xform(ob,pivots=(0,0,0),ws=True,dph=True,ztp=True)
    if lock is True:
        for at in ['translate','rotate','scale']:
            ob.attr(at).lock()

def reset_transform(ob):
    for atr in ['translate', 'rotate', 'scale']:
        try:
            reset_value = [0,0,0] if atr is not 'scale' else [1,1,1]
            ob.attr(atr).set(reset_value)
        except RuntimeError as why:
            log.warning(why)

def parent_shape(src, target, delete_src=True, delete_oldShape=True):
    '''parent shape from source to target'''
    #pm.parent(src, world=True)
    print src,target
    pm.makeIdentity(src, apply=True)
    pm.delete(src.listRelatives(type='transform'))
    pm.refresh()
    pm.parent(src.getShape(), target, r=True, s=True)
    if delete_src:
        pm.delete(src)
    if delete_oldShape:
        pm.delete(get_shape(target), shape=True)

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

# --- Scenes Mangement --- #

def transfer_material(obs, obSrc):
    try:
        obSrc_SG = obSrc.getShape().listConnections(type=pm.nt.ShadingEngine)[0]
    except:
        obSrc_SG = None
    if obSrc_SG:
        for ob in obs:
            set_material(ob,obSrc_SG)

def set_material(ob, SG):
    if type(SG) == pm.nt.ShadingEngine:
        try:
            pm.sets(SG,forceElement=ob)
        except:
            print "cannot apply %s to %s" % (SG.name(), ob.name())
    else:
        print "There is no %s" % SG.name()

def add_vray_opensubdiv(ob):
    '''add Vray OpenSubdiv attr to enable smooth mesh render'''
    if str(pm.getAttr('defaultRenderGlobals.ren')) == 'vray':
        obShape = ob.getShape()
        pm.vray('addAttributesFromGroup', obShape, "vray_opensubdiv", 1)
        pm.setAttr(obShape+".vrayOsdPreserveMapBorders", 2)

def clean_attributes(ob):
    '''clean all Attribute'''
    for atr in ob.listAttr(ud=True):
        try:
            atr.delete()
            print "%s is deleted" % atr.name()
        except:
            pass

def find_instances(
    obs,
    instanceOnly=True):
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

def export_cameras_to_fbx():
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
