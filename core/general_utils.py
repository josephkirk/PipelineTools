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
log.setLevel(logging.ERROR)

# Global var #

prefpath = 'C:/Users/nphung/Documents/maya/2017/prefs/userPrefs.mel'

# Global misc function #
def clean_outliner():
    outliners = pm.getPanel(type='outlinerPanel')
    for outliner in outliners:
        pm.outlinerEditor(outliner, e=True, setFilter="defaultSetFilter")

def reload_texture(udim=True):
    mm.eval('AEReloadAllTextures;')
    if udim:
        mm.eval('generateAllUvTilePreviews;')

def deleteUnknowPlugin():
    oldplugins = pm.unknownPlugin(q=True, list=True)
    if oldplugins:
        log.info('Found {} unknown plugins'.format(len(oldplugins)))
        for plugin in oldplugins:
            try:
                pm.unknownPlugin(plugin, remove=True)
                log.info('%s removed succesfully'%plugin)
            except:
                log.info('Cannot remove %s'%plugin)

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

def error_alert(func):
    """print Error if function fail"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        quiet_mode = False
        if 'quiet' in kwargs:
            quiet_mode = kwargs['quiet']
            del kwargs['quiet']
        try:
            t=time()
            result = func(*args, **kwargs)
            log.info('{} OK and return {}, took: {}'.format(func.__name__, result, time()-t))
            return result
        except (
                IOError,OSError,
                pm.MayaNodeError, pm.MayaAttributeError,
                AssertionError, TypeError,AttributeError) as why:
            msg = []
            msg.append(''.join([
                func.__name__,':',
                '\nargs:\n',','.join([str(a) for a in args]),
                '\nkwargs:\n',','.join(['{}={}'.format(key,value) for key,value in kwargs.items()]),
                'create Error:']))
            for cause in why:
                msg.append(str(why))
            msg = '\n'.join(msg)
            if not quiet_mode:
                log.error(msg)
                raise
    return wrapper

def do_function_on(mode='single', type_filter=['locator','transform', 'mesh', 'nurbsCurve', 'joint']):
    """Decorator that feed function with selected object
        :Parameter mode: String indicate how to feed selecled object
            to function. Valid String value is:

        :string: 'single'    : feed each selected object to function.
        :string: 'oneToOne'  : feed first and last selected to function.
        :string: 'hierachy'  : feed all children of selected object to function.
        :string: 'set'       : feed selected objects as a list to function.
        :string: 'singlelast': feed each selected object
                               that is not the last selected and
                               the last selected object to function.
        :string: 'last'      : feed a list of selected object
                               that is not the last selected and
                               the last selected object to function.
        :string: 'lastType'  : feed each member of 2 sets of different type.
        :string: 'multitype' : feed list of object of different type.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # test for decorator keywords
            selected = False
            filter_args = False
            do_mode = mode

            for k in ['selected', 'sl']:
                if k in kwargs:
                    selected = kwargs[k]
                    del kwargs[k]
            for k in ['filter_args', 'fta']:
                if k in kwargs:
                    filter_args = kwargs['filter_args']
                    del kwargs['filter_args']
            if 'mode' in kwargs:
                do_mode = kwargs['mode']
                del kwargs['mode']

            if not selected:
                if filter_args:
                    return func(*filter_type(args, type_filter), **kwargs)
                else:
                    return func(*args, **kwargs)
            # Select feed Class
            class DoFunc:
                def __init__(self):
                    self.mode = do_mode
                    self.func = func
                    self.filter = type_filter
                    self.args = args
                    self.kwargs = kwargs
                    self.results = []
                    self.function_modes = {
                        'single':self.single,
                        'set':self.obset,
                        'hierachy':self.hierachy,
                        'oneToOne': self.one_to_one,
                        'last': self.to_last,
                        'singleLast': partial(self.to_last, True),
                        'lastType': self.to_last_type,
                        'multiType': self.different_type,
                    }
                    self._get_oblist()

                def _get_oblist(self):
                    '''get selected object as PyNode'''
                    if self.filter:
                        self.oblist = filter_type(pm.selected(), self.filter)
                    else:
                        self.oblist = pm.selected()
                    if not self.oblist:
                        msg = '''No selected objects or type input in type_filter is unknown!
                        Type Filter :\n%s 
                        Selection :\n%s'''%(
                            str(self.filter),
                            str([(i, i.nodeType()) for i in pm.selected()]))
                        log.error(msg)
                        raise RuntimeError(msg)
                    return self.oblist
                # @error_alert
                def single(self):
                    '''Feed function with each selected object yield result'''
                    for ob in self.oblist:
                        # self.args.insert(0,ob)
                        # print self.args
                        result = self.func(ob,*self.args, **self.kwargs)
                        self.results.append(result)
                    return self.results

                def hierachy(self):
                    '''Feed function with each object and all its childrens and yield result'''
                    for ob in self.oblist:
                        # print ob
                        for child in iter_hierachy(ob):
                            # print child
                            self.results.append(self.func(child, *self.args, **self.kwargs))
                    return self.results

                def one_to_one(self):
                    '''Feed function with a set of first and last selected object and yield result'''
                    if len(self.oblist)%2:
                        msg = 'Selected Object Count should be power of 2.\n \
                            Current Object Counts:%d'%(len(self.oblist))
                        log.warning(msg)
                        raise RuntimeWarning(msg)
                    objects_set2 = [o for id, o in enumerate(self.oblist)
                                    if id%2]
                    objects_set1 = [o for id, o in enumerate(self.oblist)
                                    if not id%2]
                    for ob1, ob2 in zip(objects_set1, objects_set2):
                        self.results.append(self.func(ob1, ob2, *self.args, **self.kwargs))
                    return self.results

                def obset(self):
                    '''Feed function directly with list of selected objects'''
                    self.results.append(func(self.oblist, *self.args, **self.kwargs))
                    return self.results

                def to_last(self, singlelast=False):
                    '''Feed function list of selected objects before the last select object and
                    the last object'''
                    if len(self.oblist) < 2:
                        msg = 'Select more than two objects!'
                        log.error(msg)
                        raise RuntimeWarning(msg)
                    op_list = self.oblist[:-1]
                    target = self.oblist[-1]
                    if singlelast:
                        for op in op_list:
                            self.results.append(self.func(op, target, *self.args, **self.kwargs))
                    else:
                        self.results.append(self.func(op_list, target, *self.args, **self.kwargs))
                    return self.results

                def to_last_type(self):
                    '''like 'last' mode but last object must be a different type from other'''
                    if len(self.oblist) < 2 or len(self.filter) < 2:
                        msg = 'Select more than two objects of diffent type!\n \
                            Current Selection:\n%s \
                            Current Type Filter:\n%s '%(
                                str(self.oblist),
                                str(self.filter))
                        log.error(msg)
                        raise RuntimeWarning(msg)
                    source_type_set = [
                        o for o in self.oblist
                        if o.nodeType() != self.filter[-1]]
                    target_type_set = [
                        o for o in self.oblist
                        if o.nodeType() == self.filter[-1]]
                    self.results.append(func(
                        source_type_set,
                        target_type_set,
                        *args, **kwargs))
                    return self.results

                def different_type(self):
                    '''like 'last' mode but last object must be a different type from other'''
                    if len(self.oblist) < 2 or len(self.filter) < 2:
                        msg = 'Select more than %s objects of %s diffent type!\n \
                            Current Selection:\n%s \
                            Current Type Filter:\n%s '%(
                                len(self.filter), len(self.filter),
                                str(self.oblist),
                                str(self.filter))
                        log.error(msg)
                        raise RuntimeWarning(msg)
                    obtype_list = []
                    for t in self.filter:
                        obtypes = []
                        for o in self.oblist:
                            otype = get_type(o)
                            if otype == t:
                                obtypes.append(o)
                        obtype_list.append(obtypes)
                    assert all(obtype_list), \
                        'One or more object set belong to a type in type Filter is empty'
                    for ob_set in zip(*obtype_list):
                        nargs = list(ob_set)
                        nargs.extend(self.args)
                        self.results.append(self.func(*nargs, **self.kwargs))
                    return self.results

                @classmethod
                def do(cls):
                    return recurse_collect(cls().function_modes[cls().mode]())

            result = DoFunc.do()
            log.debug('%s Wrap by do_function_on decorator and return %s'%(func.__name__,str(result)))
            return result
        return wrapper
    return decorator

# Utility functions #
# --- Path --- #

def collect_files(topdir, latestOnly=False):
    pass

def collect_dirs(topdir):
    pass

def send_current_file(
        scene=True,
        suffix='_vn',
        lastest=True,
        render=False,
        tex=True,
        extras=['psd', 'uv', 'zbr', 'pattern'],
        version=1,
        verbose=True):
    src = pm.sceneName()
    scene_src = src.dirname()
    path_root = ''
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
        if all([src.dirname().dirname().dirname().basename() != d for d in ['CH','BG','CP']]) and \
                src.dirname().dirname().basename()!='CP':
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
def filter_type(ob_list, type_list):
    filter_result = []
    for o in ob_list:
        otype = get_type(o)
        if otype in type_list:
            if otype == 'vertex':
                vList = [o.node().vtx[vid] for vid in o.indices()]
                for v in vList:
                    if v not in filter_result:
                        filter_result.append(v)
            elif otype == 'edge':
                eList = [o.node().e[eid] for eid in o.indices()]
                for e in eList:
                    if e not in filter_result:
                        filter_result.append(e)
            elif otype == 'face':
                fList = [o.node().f[fid] for fid in o.indices()]
                for f in fList:
                    if f not in filter_result:
                        filter_result.append(f)
            else:
                filter_result.append(o)
    return filter_result

@error_alert
def get_type(ob):
    try:
        otype = ob.getShape().nodeType()
        assert (otype is not None)
    except AttributeError, AssertionError:
        otype = ob.nodeType()
    component_dict = {
        'vertex': pm.general.MeshVertex,
        'edge': pm.general.MeshEdge,
        'face': pm.general.MeshFace
    }
    for typ, ptyp in component_dict.items():
        if isinstance(ob,ptyp):
            otype = typ
    return otype

@error_alert
def get_name(ob):
    assert hasattr(ob,'name'), 'Cannot get name for %s'%ob
    return ob.name().split('|')[-1] 

@error_alert
def recurse_trees(root, list_branch_callback, callback,*args,**kwargs):
    '''Recursive do a callback function'''
    collectors = []
    def recurse(node):
        if list_branch_callback(node):
            for child in list_branch_callback(node):
                collectors.append(recurse(child))
        else:
            collectors.append(callback(node,*args,**kwargs))
    recurse(root)
    filter_collectors = [i for i in collectors if i]
    return filter_collectors

#@error_alert
def recurse_collect(*args, **kwargs):
    '''Recursive throught iterator to yield list elemment'''
    collectors = []
    def recurse(alist):
        if hasattr(alist,'__iter__'):
            for elemen in alist:
                if hasattr(elemen,'has_key'):
                    for key, value in elemen.iteritems():
                        collectors.append(key)
                        recurse(value)
                else:
                    recurse(elemen)
        else:
            # yield eleme
            collectors.append(alist)
    for arg in args:
        recurse(arg)
    if 'filter' in kwargs:
        assert kwargs['filter'], 'Filter Type is empty'
        collectors = [
            i for i in collectors
            if any([isinstance(i, _type) for _type in kwargs['filter']])]
    return collectors

@error_alert
def iter_hierachy(root, filter='transform'):
    '''yield hierachy generator object with stack method'''
    stack = [root]
    level = 0
    while stack:
        level +=1
        node = stack.pop()
        yield node
        if hasattr(node, 'getChildren'):
            childs = node.getChildren( type=filter )
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
    closest_info = get_closest_info(ob_pos,mesh_node)
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
def get_closest_info(ob_pos, mesh_node):
    mesh_node = get_shape(pm.PyNode(mesh_node))
    temp_node = pm.nt.ClosestPointOnMesh()
    temp_loc = pm.spaceLocator(p=ob_pos)
    mesh_node.worldMesh[0] >> temp_node.inMesh
    temp_loc.worldPosition[0] >> temp_node.inPosition
    mesh_node.worldMatrix[0] >> temp_node.inputMatrix
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
def get_points_on_curve(inputcurve, amount=3):
    infoNode = pm.PyNode(pm.pointOnCurve(inputcurve, ch=True, top=True))
    try:
        inc = 1.0/(amount-1)
        for i in range(amount):
            infoNode.parameter.set(i*inc)
            pos = infoNode.position.get()
            norm = infoNode.normal.get()
            tang = infoNode.tangent.get()
            crossV = norm.cross(tang)
            pmatrix = pm.dt.Matrix(
                norm.x, norm.y, norm.z, 0,
                tang.x, tang.y, tang.z, 0,
                crossV.x, crossV.y, crossV.z, 0,
                pos.x, pos.y, pos.z, 0)
            yield (pmatrix.translate, pmatrix.rotate)
    except ZeroDivisionError:
        log.error('Amount is too low, current:{}, minimum:{}'.format(amount, 2))
        raise
    finally:
        pm.delete(infoNode)

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
        getSkin = [c for c in ob_shape.listHistory(type='skinCluster')]
        if getSkin:
            return getSkin[0]
        else:
            msg = '{} have no skin bind'.format(ob)
            return pm.error(msg)
            # if 'skinCluster' in connection.name():
        # shape_connections = ob_shape.inputs(type=['skinCluster', 'objectSet'])
        # for connection in shape_connections:
        #     # if 'skinCluster' in connection.name():
        #     if isinstance(connection, pm.nt.SkinCluster):
        #         return connection
        #     try_get_skinCluster = connection.listConnections(type='skinCluster')
        #     if try_get_skinCluster:
        #         return try_get_skinCluster[0]
        #     else:
        #         msg = '{} have no skin bind'.format(ob)
        #         return pm.error(msg)
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

@error_alert
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
        vert_pos = sum([v.getPosition('world') for v in list(verts_set)])/len(verts_set)
        return vert_pos

@error_alert
def get_points(sellist):
    '''
    Get all Point position from a list of define object type
    '''
    transformtype = [
        ob.getTranslation('world')
        for ob in filter_type(sellist,['transform', 'joint', 'mesh'])
        if hasattr(ob, 'getTranslation')]
    vertextype = [
        get_closest_info(cpn.getPosition('world'), cpn.node())['Closest Point']
        for cpn in filter_type(sellist,['vertex'])]
    edgetype = [
        get_closest_info(pm.dt.center(*[cpn.getPoint(i,'world')
        for i in range(2)]), cpn.node())['Closest Mid Edge']
        for cpn in filter_type(sellist,['edge'])]
    flist = [mfn.node().f[mfid] for mfn in filter_type(sellist,['face']) for mfid in mfn.indices()]
    print flist
    facetype = [
        get_closest_info(pm.dt.center(*[mf.getPoint(i,'world')
        for i in range(4)]), mf.node())['Closest Point']
        for mf in flist
    ]
    return (transformtype + vertextype + edgetype + facetype)
# --- Transformation and Shape --- #
def getIntersectPoint(p1, p2, mesh):
    """Return intersection on mesh between 2 points
        :param p1: Position 1
        :type p1: pm.dt.Point3
        :param p2: Position 2
        :type p2: pm.dt.Point3
        :param mesh: Intesected Mesh
        :type mesh: pm.nt.Mesh
        :rtype: False or pm.dt.Point3
    """
    src = p1
    dirVector = t2-t1
    lenVector = dirVector.length()
    dirVector.normalize()
    isintesect, points, _ = mesh.intersect(src, dir, 1e-1000000)
    if not isintersect:
        return False
    for p in points:
        if src.distanceTo(p) <= lenVector:
            return p
    return False



@do_function_on()
def setColor(control, color=[1,0,0,0]):
    try:
        control.overrideEnabled.set(True)
        control.overrideRGBColors.set(True)
        control.overrideColorRGB.set(color[:-1])
        sg = control.shadingGroups()[0] if control.shadingGroups() else None
        if sg:
            shdr = sg.inputs()[0]
            shdr.outColor.set(color)
            shdr.outTransparency.set([color[-1] for i in range(3)])
    except AttributeError as why:
        log.error(why)

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

def rename_shape():
    for ob in pm.ls():
        if hasattr(ob,'getShape'):
            try:
                if ob.getShape():
                    for obShape in ob.listRelatives(shapes=True):
                        obShape.rename(get_name(ob)+'Shape')
            except RuntimeError:
                log.warning("Can't perform rename for {}".format(ob.getShape()))

def remove_number(string):
    for index, character in enumerate(string):
        if character.isdigit():
            return (string[:index], int(string[index:] if string[index:].isdigit() else string[index:]))
@error_alert
def convert_component(
        components_list,
        toVertex=True,
        toEdge=False,
        toFace=False):
    '''
    Convert tranform to component or from component to other component type
    '''
    # check if arg contain tranform node, if True return Shape Vertex
    filter_transform = [
        o for o in components_list if type(o) is pm.nt.Transform]
    if filter_transform:
        converts = []
        for tr in filter_transform:
            if getShape(tr):
                convert = getShape(tr).vtx
                for vert in getShape(tr).vtx:
                    for vertid in vert.indices():
                        converts.append(getShape(tr).vtx[vertid])
        return converts
    filter_component = [c for c in components_list if hasattr(c,'__apicomponent__')]
    if filter_component:
        converts = pm.polyListComponentConversion(
            filter_component,
            fromFace=True, fromEdge=True, fromVertex=True,
            toFace=toFace, toEdge=toEdge, toVertex=toVertex)
        converts = [pm.PyNode(convert) for convert in converts]
        if toFace:
            result = []
            for face in result:
                for faceid in face.indices():
                    converts.append(face.node().f[faceid])
            return result
        if toEdge:
            result = []
            for edge in converts:
                for edgeid in edge.indices():
                    result.append(edge.node().e[edgeid])
            return result
        if toVertex:
            result = []
            for vert in converts:
                for vertid in vert.indices():
                    result.append(vert.node().vtx[vertid])
            return result


@do_function_on(
    'set')
def convert_to_curve(sellist, name='converted_curve', smoothness=1):
    '''
    Connect object in list with a Nurbs Curve
    '''
    # print sellist
    if any([
            get_type(ob) == typ for ob in sellist
            for typ in ['transform', 'joint', 'mesh','nurbsCurve']]):
        # print sellist
        cvpMatrix = [ob.getTranslation('world') for ob in sellist if hasattr(ob, 'getTranslation')]
    if any([get_type(cpn) == 'vertex' for cpn in sellist]):
        cvpMatrix = [get_closest_info(cpn.getPosition('world'), cpn.node())['Closest Point'] for cpn in sellist]
    if any([get_type(cpn) == 'edge' for cpn in sellist]):
        cvpMatrix = [get_closest_info(pm.dt.center(*[cpn.getPoint(i,'world') for i in range(2)]), cpn.node())['Closest Mid Edge'] for cpn in sellist]
    if any([get_type(cpn) == 'face' for cpn in sellist]):
        flist = []
        for mfn in sellist:
            for mfid in mfn.indices():
                mf = mfn.node().f[mfid]
                if mf not in flist:
                    flist.append(mf)
        cvpMatrix = [
            get_closest_info(pm.dt.center(*[mf.getPoint(i,'world') for i in range(4)]), mf.node())['Closest Point']
            for mf in flist
        ]
    assert 'cvpMatrix' in locals(), 'Cannot create curve for input {}'.format(sellist)
    # cvpMatrix.sort()
    # temp_list = [cvpMatrix[0]]
    # id = 0
    # while id<(len(cvpMatrix)-1):
    #     distancelist = [(ncvp, cvpMatrix[id].distanceTo(ncvp)) for ncvp in cvpMatrix]
    #     distancelist.sort(key=lambda x:x[1])
    #     shortest = distancelist[0][0] if distancelist[0][0]!=temp_list[-1] else distancelist[1][0]
    #     cvpMatrix.remove(shortest)
    #     temp_list.append(shortest)
    #     id += 1
    # cvpMatrix = temp_list
    if smoothness > 1:
        cvpMatrix = [cvpMatrix[0]]+cvpMatrix+[cvpMatrix[-1]]
    key = range(len(cvpMatrix)+smoothness-1)
    crv = pm.curve(d=smoothness, p=cvpMatrix, k=key)
    crv.rename(name)
    return crv

@do_function_on('singleLast', type_filter=['locator','transform', 'mesh', 'joint'])
def snap_nearest(ob, mesh_node,constraint=False):
    if constraint:
        closest_uv = get_closest_component(ob, mesh_node)
        constraint = pm.pointOnPolyConstraint(
            mesh_node, ob, mo=False)
        stripname = mesh_node.split('|')[-1]
        constraint.attr(stripname + 'U0').set(closest_uv[0])
        constraint.attr(stripname + 'V0').set(closest_uv[1])
        return constraint
    closest_component_pos = get_closest_component(ob, mesh_node, uv=False, pos=True)
    ob.setTranslation(closest_component_pos,'world')

@do_function_on('singleLast', type_filter=['locator','transform', 'mesh', 'nurbsCurve', 'joint'])
def snap_to_curve(ob, curve_node, pin=True, query=False):
    npc = pm.createNode('nearestPointOnCurve')
    poc = pm.createNode('pointOnCurveInfo')
    npc.result.parameter >> poc.parameter
    curve_node.worldSpace[0] >> npc.inputCurve
    curve_node.worldSpace[0] >> poc.inputCurve
    npc.inPosition.set(ob.getTranslation('world'))
    pm.delete(npc)
    if query:
        result = poc.result.position.get()
        pm.delete(poc)
        return result
    if pin:
        poc.result.position >> ob.translate
    else:
        ob.setTranslation(poc.result.position.get(),'world')
        pm.delete(poc)

@do_function_on(type_filter=['transform', 'mesh', 'nurbsCurve'])
def mirror_transform(ob, axis="x",xform=[0,4]):
    axisDict = {
        "x":('tx', 'ry', 'rz', 'sx'),
        "y":('ty', 'rx', 'rz', 'sy'),
        "z":('tz', 'rx', 'ry', 'sz')}
    #print obs
    for at in axisDict[axis][xform[0]:xform[1]]:
        ob.attr(at).set(ob.attr(at).get()*-1)
    pm.makeIdentity(ob,s=True,apply=True)
    if get_shape(ob):
        pm.polyNormal(ob, nm=0)
        pm.bakePartialHistory(ob, all=True)
    for obs in ob.listRelatives(type='transform'):
        if get_shape(obs):
            pm.polyNormal(obs, nm=0)
            pm.bakePartialHistory(obs, all=True)
    pm.select(ob)

@do_function_on()
def lock_transform(
        ob,
        lock=True,
        pivotToOrigin=True):
    '''reset pivot to 0 and toggle transform lock'''
    for at in ['translate','rotate','scale','visibility','tx','ty','tz','rx','ry','rz','sx','sy','sz']:
        ob.attr(at).unlock()
    if pivotToOrigin:
        oldParent = ob.getParent()
        ob.setParent(None)
        pm.xform(ob,pivots=(0,0,0),wd=True, ws=True,dph=True,ztp=True)
        ob.setParent(oldParent)
        pm.makeIdentity(ob, apply=True)
    if lock is True:
        for at in ['translate','rotate','scale']:
            ob.attr(at).lock()

@do_function_on()
def reset_transform(ob, translate=True, rotate=True, scale=True):
    resetAtr = []
    if translate:
        resetAtr.extend(['tx','ty','tz'])
    if rotate:
        resetAtr.extend(['rx','ry','rz'])
    if scale:
        resetAtr.extend(['sx','sy','sz'])
    for at in resetAtr:
        try:
            ob.attr(at).set(0)
            if at.startswith('s'):
                ob.attr(at).set(1)
        except RuntimeError as why:
            log.warning(why)

@do_function_on('oneToOne')
def parent_shape(src, target, delete_src=True, delete_oldShape=True):
    '''parent shape from source to target'''
    #pm.parent(src, world=True)
    print src,target
    pm.makeIdentity(src, apply=True)
    pm.delete(src.listRelatives(type='transform'))
    pm.refresh()
    if delete_oldShape:
        pm.delete(get_shape(target), shape=True)
    if delete_src:
        pm.parent(src.getShape(), target, r=True, s=True)
        pm.delete(src)
    else:
        temp = src.duplicate()[0]
        pm.parent(temp.getShape(), target, r=True, s=True)
        pm.delete(temp)


@do_function_on()
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

@do_function_on()
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
def removeAllReferenceEdits():
    for ref in pm.listReferences():
        for editType in ['addAttr', 'deleteAttr', 'setAttr', 'disconnectAttr']:
            ref.removeReferenceEdits(editCommand=editType, force=True)

@do_function_on()
def lock_node(node, lock=True, query=False):
    if query:
        result = pm.lockNode(node, q=query)
        log.info(result)
        return result
    pm.lockNode(node, lock=lock)
    return lock

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

@do_function_on()
def add_vray_opensubdiv(ob):
    '''add Vray OpenSubdiv attr to enable smooth mesh render'''
    if str(pm.getAttr('defaultRenderGlobals.ren')) == 'vray':
        obShape = ob.getShape()
        pm.vray('addAttributesFromGroup', obShape, "vray_opensubdiv", 1)
        pm.setAttr(obShape+".vrayOsdPreserveMapBorders", 2)

@do_function_on()
def clean_attributes(ob):
    '''clean all Attribute'''
    for atr in ob.listAttr(ud=True):
        try:
            atr.delete()
            print "%s is deleted" % atr.name()
        except:
            pass

@do_function_on()
def find_instances(
    ob,
    instanceOnly=True):
    allTransform = [tr for tr in pm.ls(type=pm.nt.Transform) if tr.getShape()]
    instanceShapes =[]
    if instanceOnly:
        pm.select(cl=True)
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
