import pymel.core as pm
import pymel.util as pu
import pymel.util.path as pp
import maya.cmds as cm
import maya.mel as mm
import shutil
import os
import random as rand
import PipelineTools.customClass as cc
reload(cc)
###misc function

###function
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

def mirrorTransform(obs, axis="x",xform=[0,4]):
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

def lockTransform(obs,lock=True):
    if not obs:
        print "no object to mirror"
        return
    if type(obs) != list:
        obs = [obs]
    for ob in obs:
        for at in ['translate','rotate','scale']:
            ob.attr(at).set(lock=lock)

def addVrayOpenSubdivAttr():
    '''add Vray OpenSubdiv attr to enable smooth mesh render'''
    sel = pm.selected()
    if not sel:
        return
    for o in sel:
        if str(cm.getAttr('defaultRenderGlobals.ren')) == 'vray':
            obShape = pm.listRelatives(o, shapes=True)[0]
            cm.vray('addAttributesFromGroup', obShape, "vray_opensubdiv", 1)
            pm.setAttr(obShape+".vrayOsdPreserveMapBorders", 2)

####

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
        CHHairFiles = pp(CHversion.path['..']).files('*.mb')
        CHHairFiles.sort(key=os.path.getmtime)
        CHPath['hair'] = CHHairFiles[-1]
        try:
            CHClothFiles = pp(CHversion.path['clothes']).files('*.mb')
            CHClothFiles.sort(key=os.path.getmtime)
            CHPath['cloth'] = CHClothFiles[-1]
        except:
            pass
            # print "No folder 'clothes' in %s " % CH.path
        try:
            CHPath['render'] = CHversion.path['rend']
        except:
            pass
            # print "No folder 'render' in %s " % CHversion.path['..']
        CHPath['tex'] = pp(CHversion.texPath['..'])
        for k in ['pattern','uv','zbr']:
            try:
                CHPath[k] = pp(CHversion.texPath[k])
            except:
                pass
                # print "no folder '%s' in %s " % (k, CHPath['tex'])
    except:
        print "Character %s has no version" % Assetname
    return CHPath

def sendFile(CH,
             ver,
             num=0,
             destdrive="",
             sendFile={
                 'hair':False,
                 'cloth':False,
                 'render':False,
                 'uv':False,
                 'zbr':False,
                 'tex':False,
                 'pattern':False,
                 '_common':False}):
    '''send NS57 File'''
    AllPath = GetAssetPath(CH, ver)
    #print AllPath
    todayFolder = pm.date(f='YYYYMMDD')
    if num and num != 1:
        todayFolder = "_".join([todayFolder, ('%02d' % num)])
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
            texFiles = [f for f in AllPath[k].files()
                        if (any([f.endswith(c) for c in ['jpg',
                                                         'png',
                                                         'tif',
                                                         'tiff']])
                            and CH in f.basename())]
            if texFiles:
                copFiles(texFiles)
            else:
                print "no Texture Files"
            psdDir = [d for d in AllPath[k].dirs()
                      if 'psd' in d]
            if psdDir:
                psdFiles = [f for f in psdDir.files()
                            if(any([f.endswith(c) for c in ['psd', 'psb']])
                               and CH in f.basename())]
                copFiles(psdFiles)
            else:
                print "no Psd Files"
        else:
            print "no %s folder" % k
    for key, value in sendFile.iteritems():
        if key == 'tex' or key == '_common':
            if value and key == 'tex':
                sendTexFile('tex')
            if value and key == '_common':
                sendTexFile('_common')
        else:
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