import pymel.core as pm
import pymel.util as pu
import maya.cmds as cm
import maya.mel as mm
import shutil
import os
import random as rand

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
def rebuildControl(ob, obshape='circle', ra=1):
    '''rebuild Hair Tube Control to specific type'''
    if not type(ob) == pm.nodetypes.Transform:
        return
    obOldShape = ob.listRelatives(shapes=1)[0]
    shapeType = {'circle':(3, 8), 'triangle':(1, 3)}
    obNewShape = pm.circle(c=(0, 0, 0),
                           nr=(0, 1, 0),
                           sw=360, r=ra,
                           d=shapeType[obshape][0],
                           ut=0, tol=5.77201e-008,
                           s=shapeType[obshape][1],
                           ch=1,
                           name="HairProfileCurve#")
    for a in [('overrideEnabled', 1), ('overrideRGBColors', 1), ('overrideColorRGB', (0.2, 1, 0))]:
        obNewShape[0].listRelatives(shapes=1)[0].attr(a[0]).set(a[1])
    pm.parent(obNewShape[0].listRelatives(shapes=1)[0], ob, r=1, s=1)
    pm.delete(obOldShape)
    pm.delete(obNewShape)

def createPointParent(ob, name="PointParent#", shapeReplace=False, r=1):
    '''Create a Parent of selected'''
    obOldParent = ob.getParent()
    obNewParent = pm.polySphere(name=name, subdivisionsAxis=6, subdivisionsHeight=4, radius=r/3)
    for a in [('castsShadows', 0),
              ('receiveShadows', 0),
              ('smoothShading', 0),
              ('primaryVisibility', 0),
              ('visibleInReflections', 0),
              ('visibleInRefractions', 0),
              ('overrideEnabled', 1),
              ('overrideShading', 0),
              ('overrideTexturing', 0),
              ('overrideRGBColors', 1),
              ('overrideColorRGB', (1, 0, 0))]:
        obNewParent[0].listRelatives(shapes=1)[0].attr(a[0]).set(a[1])
    if not shapeReplace:
        pm.xform(obNewParent[0], ws=1, t=pm.xform(ob, q=1, ws=1, t=1))
        pm.xform(obNewParent[0], ws=1, ro=pm.xform(ob, q=1, ws=1, ro=1))
        #pm.color(obNewParent[0],rgb=(1,0,0))
        #obNewParent.setAttr("translate",obPos)
        if obOldParent:
            pm.parent(obNewParent[0], obOldParent)
        pm.parent(ob, obNewParent[0])
    else:
        pm.parent(obNewParent[0].listsRelatives(shapes=1)[0], ob, r=1, s=1)
        pm.delete(obNewParent)
def createHairMesh(profilesList,
                   name="hairMesh#",
                   cSet="hairCrease",
                   mat="",
                   lengthDivs=7,
                   widthDivs=4):
    '''create a Hair Tube with auto crease and material from list of Curve Profiles'''
    print profilesList
    if not profilesList or all(
            [type(o.listRelatives(shapes=1)[0]) != pm.nodetypes.NurbsCurve for o in profilesList]):
        print "no Profiles"
        return
    pm.select(profilesList)
    pm.nurbsToPolygonsPref(pt=1, un=4, vn=7, f=2, ut=2, vt=2)
    HairMesh = pm.loft(n=name, po=1, ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, rsn=True)
    ###
    #custom Attribute add
    HairMesh[0].addAttr('lengthDivisions', min=1, at='long', dv=lengthDivs)
    HairMesh[0].addAttr('widthDivisions', min=4, at='long', dv=widthDivs)
    HairMesh[0].setAttr('lengthDivisions', e=1, k=1)
    HairMesh[0].setAttr('widthDivisions', e=1, k=1)
    HairTess = pm.listConnections(HairMesh)[-1]
    HairMesh[0].connectAttr('widthDivisions', HairTess+".uNumber")
    HairMesh[0].connectAttr('lengthDivisions', HairTess+".vNumber")
    HairMeshShape = HairMesh[0].listRelatives(shapes=1)[0]
    ###
    #set Crease
    pm.select(HairMeshShape.e[0, 2], r=1)
    pm.runtime.SelectEdgeLoopSp()
    sideEdges = pm.selected()
    if bool(pm.ls(cSet, type=pm.nodetypes.CreaseSet)):
        hsSet = pm.ls(cSet, type=pm.nodetypes.CreaseSet)[0]
    else:
        hsSet = pm.nodetypes.CreaseSet(name=cSet)
        hsSet.setAttr('creaseLevel', 2.0)
    for e in sideEdges:
        pm.sets(hsSet, forceElement=e)
    #assign Texture
    HairUV = HairMeshShape.map
    pm.polyEditUV(HairUV, pu=0.5, pv=0.5, su=0.3, sv=1)
    pm.polyEditUV(HairUV, u=rand.uniform(-0.1, 0.1))
    ###
    #Add Vray OpenSubdiv
    pm.select(HairMesh[0], r=1)
    addVrayOpenSubdivAttr()
    ###
    #set Smoothness
    pm.displaySmoothness(po=3)
    ###
    #set Material
    if bool(pm.ls(mat, type=pm.nodetypes.ShadingEngine)):
        pm.sets(pm.ls(mat)[0], forceElement=HairMesh[0])
    return HairMesh

def makeHairMesh(name="HairMesh#",
                 mat="",
                 cSet="hairCrease",
                 reverse=False,
                 lengthDivs=7,
                 widthDivs=4,
                 Segments=4,
                 width=1,
                 curveDel=False,
                 cShape='triangle'):
    '''Create a Hair Tube From Select Curve line or Edge or IsoPram'''
    sel = pm.selected()
    if not sel:
        print "Select some Curves or Edges or isopram"
        return
    if type(sel[0]) == pm.general.MeshEdge:
        pm.runtime.CreateCurveFromPoly()
        pathTransform = pm.selected()[0]
    elif type(sel[0]) == pm.general.NurbsSurfaceIsoparm:
        pm.runtime.DuplicateCurve()
        pathTransform = pm.selected()[0]
    pathTransform = [t for t in pm.selected() if type(t) == pm.nodetypes.Transform]
    pm.select(pathTransform, r=1)
    pathShape = pm.listRelatives(shapes=True)
    if type(pathShape[0]) == pm.nodetypes.NurbsCurve:
        minscale = [0.001, 0.001, 0.001]
        pathCurve = [(i, pathShape[pathTransform.index(i)]) for i in pathTransform]
        if pm.objExists("HairBaseProfileCurve"):
            profileCurve = pm.ls("HairBaseProfileCurve")[0]
            print profileCurve.listRelatives()[0].listConnections()[0]
            profileCurve.listRelatives()[0].listConnections()[0].setRadius(width)
            pm.showHidden(profileCurve, a=1)
        else:
            shapeType = {'circle':(3, 8), 'triangle':(1, 3)}
            profileCurve = pm.circle(c=(0, 0, 0),
                                     nr=(0, 1, 0),
                                     sw=360,
                                     r=width,
                                     d=shapeType[cShape][0],
                                     ut=0, tol=5.77201e-008,
                                     s=shapeType[cShape][0],
                                     ch=1,
                                     name="HairBaseProfileCurve")
            for a in [('overrideEnabled', 1),
                      ('overrideRGBColors', 1),
                      ('overrideColorRGB', (0.2, 1, 0))]:
                profileCurve[0].listRelatives(shapes=1)[0].attr(a[0]).set(a[1])
        pm.select(d=1)
        for crv in pathCurve:
            print crv
            pm.rebuildCurve(crv[0], kep=1)
            if reverse:
                pm.reverseCurve(crv[0])
            #profileInstance = instance(profileCurve,n="pCrv_instance"+string(pathCurve.index(crv)))
            if pm.objExists("HairCtrlGroup"):
                hairOncsGroup = pm.ls("HairCtrlGroup")[0]
            else:
                hairOncsGroup = pm.group(name="HairCtrlGroup")
            #pm.parent(hairOncGroup,crv[0])
            mPath = pm.pathAnimation(profileCurve,
                                     crv[0], fa='y',
                                     ua='x',
                                     stu=1,
                                     etu=Segments*10,
                                     b=1)
            HairProfile = []
            hairOncGroup = pm.group(name="HairCtrls#")
            pm.parent(hairOncGroup, hairOncsGroup, r=1)
            for u in range(Segments+1):
                pm.currentTime(u*10)
                profileInstance = pm.duplicate(profileCurve,
                                               n=(crv[0]+"HairProFileCrv_"+str(u)),
                                               rr=1)[0]
                pm.parent(profileInstance, hairOncGroup, r=1)
                HairProfile.append(profileInstance)
                if u == 0 or u == Segments:
                    pm.scale(profileInstance, minscale, a=1, os=1)
            HairMesh = createHairMesh(
                HairProfile,
                name=name,
                cSet=cSet,
                mat=mat,
                lengthDivs=lengthDivs,
                widthDivs=widthDivs)
            pm.rename(hairOncGroup, hairOncGroup.name()+HairMesh[0].name())
            pm.delete(profileCurve, mp=1)
            pm.delete(profileCurve)
            pm.xform(
                hairOncsGroup,
                ws=1,
                piv=pm.xform(
                    hairOncsGroup.getChildren()[-1],
                    q=1, ws=1, piv=1)[:3])
        if curveDel:
            pm.delete(pathTransform, hi=1)

def selHair(
        selectTip=False,
        selectRoot=False,
        selectAll=False,
        setPivot=True,
        returnInfo=False,
        rebuild=[False, 7, 4], cShape=(False, 'circle', 1)):
    '''Select Hair Controls'''
    sel = pm.selected()
    if not sel:
        return
    ### check for right Selection
    hairMeshes = []
    for o in sel:
        #print o.getParent() == pm.ls('HairCtrlGroup')[0]
        if type(o.getShape()) == pm.nodetypes.NurbsCurve or o.getParent() == pm.ls('HairCtrlGroup')[0]:
            try:
                if o.getParent() == pm.ls('HairCtrlGroup')[0]:
                    o = o.listRelatives(type=pm.nodetypes.Transform)[0]
                hairLoft = o.getShape().listConnections(type=pm.nodetypes.Loft)[0]
                hairTes = hairLoft.listConnections(type=pm.nodetypes.NurbsTessellate)[0]
                hair = hairTes.listConnections(type=pm.nodetypes.Transform)[0]
            except:
                continue
        elif (type(o.getShape()) == pm.nodetypes.Mesh and
              o.listConnections(type=pm.nodetypes.NurbsTessellate)):
            hair = o
            hairTes = o.listConnections(type=pm.nodetypes.NurbsTessellate)[0]
            hairLoft = hairTes.listConnections(type=pm.nodetypes.Loft)[0]
            print hair, hairTes, hairLoft
        else:
            continue
        if all([hair, hairTes, hairLoft]):
            hairMeshes.append((hair, hairTes, hairLoft))
        else:
            print "Something wrong with getting hair Tesselate and Loft"
            return
    if hairMeshes:
        #print hairMeshes
        ### getting all Controls
        Cgroups = []
        for hair in hairMeshes:
            try:
                #print hair
                hairLoft = hair[2]
                ctrls = [c for c in hairLoft.listConnections() if type(c) == pm.nt.Transform]
                ControlGroup = ctrls[0].getParent()
                #print ControlGroup
                if setPivot:
                    pm.xform(
                        ControlGroup,
                        ws=1,
                        piv=pm.xform(
                            ControlGroup.listRelatives(type=pm.nodetypes.Transform)[0],
                            q=1, ws=1, piv=1)[:3])
                if rebuild[0]:
                    NewControls = ControlGroup.listRelatives(type=pm.nodetypes.Transform)
                    print NewControls
                    if cShape[0]:
                        for c in NewControls:
                            rebuildControl(c, obshape=cShape[1], ra=cShape[2])
                    oldname = hair[0].name()
                    oldParent = hair[0].getParent()
                    curMaterial = hair.getShape().listConnections(
                        type=pm.nodetypes.ShadingEngine)[0].name()
                    pm.rename(hair, '_'.join([oldname, 'old']))
                    newHair = createHairMesh(
                        NewControls,
                        name=oldname,
                        mat=curMaterial,
                        lengthDivs=rebuild[1], widthDivs=rebuild[2])
                    pm.parent(newHair[0], oldParent)
                    #pm.delete(hair[0])
                    #del hair
                    hair = newHair[0]
            except:
                continue
            if ControlGroup:
                #print ControlGroup
                Cgroups.append((hair,ControlGroup))
        ### select as Requested
        if Cgroups:
            #print Cgroups
            if not returnInfo:
                pm.select(d=1)
                for cGroup in Cgroups:
                    #print cGroup[1]
                    if selectTip:
                        hairTipsList = cGroup[1].listRelatives(type=pm.nt.Transform)[-1]
                        pm.select(hairTipsList, add=1)
                    elif selectRoot:
                        hairRootsList = cGroup[1].listRelatives(type=pm.nt.Transform)[0]
                        pm.select(hairRootsList, add=1)
                    elif selectAll:
                        pm.select(cGroup[1].listRelatives(type=pm.nt.Transform), add=1)
                    else:
                        pm.select(cGroup[1], add=1)
            else:
                return Cgroups

def splitHairCtrl(d='up'):
    '''add Hair Controls'''
    sel = pm.selected()
    if not sel:
        return
    directionDict = {
        'up':1,
        'down':-1}
    if not directionDict.has_key(d):
        return
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    #print hairInfo[0][0]
    #print hairInfo
    for selOb in sel:
        pm.select(selOb, r=1)
        hairInfo = hairInfoAll[sel.index(selOb)]
        ctrls = hairInfo[1].listRelatives(type=pm.nt.Transform)
        hair = hairInfo[0][0]
        for ctrl in ctrls:
            pm.rename(ctrl, '_'.join([ctrl.name(), "old"]))
        ctrlID = ctrls.index(selOb)
        if ctrlID == 0:
            directionDict[d] = 1
        elif ctrlID == (len(ctrls)-1):
            directionDict[d] = -1
        newCtrl = pm.duplicate(ctrls[ctrlID])[0]
        pm.move(
            newCtrl,
            (ctrls[ctrlID].getTranslation(space='world') +
             ctrls[ctrlID+directionDict[d]].getTranslation(space='world'))/2,
            a=1, ws=1)
        pm.scale(
            newCtrl,
            (ctrls[ctrlID].attr('scale').get() + 
             ctrls[ctrlID+directionDict[d]].attr('scale').get())/2,
            a=1)
        ctrls.insert(ctrlID+(directionDict[d]+1)/2, newCtrl)
        for ctrl in ctrls:
            pm.rename(
                ctrl,
                '_'.join([ctrl.name().split('_')[0],
                str(ctrls.index(ctrl)+1)]))
            pm.parent(ctrl, w=1)
            pm.parent(ctrl, hairInfo[1])
        oldname = hair.name()
        oldParent = hair.getParent()
        curMaterial = hair.getShape().listConnections(
            type=pm.nodetypes.ShadingEngine)[0].name()
        pm.rename(hair, '_'.join([oldname, 'old']))
        newHair = createHairMesh(
            ctrls,
            name=oldname,
            mat=curMaterial,
            lengthDivs=hair.attr('lengthDivisions').get(),
            widthDivs=hair.attr('widthDivisions').get())
        pm.parent(newHair[0], oldParent)
        pm.delete(hair)
        pm.select(newCtrl)
        pm.setToolTo('moveSuperContext')

def dupHairMesh(mirror=False):
    '''duplicate a HairTube'''
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    Cgroups = []
    for hair in hairInfoAll:
        pm.select(hair[0][0],hair[1])
        ctrls=hair[1].listRelatives(type=pm.nt.Transform)
        pm.duplicate(ic=1, un=1)
        if mirror:
            pm.scale(hair[1], -1, smn=1, p=(0,0,0), ws=1)
            pm.polyNormal(hair[0][0], nm=3)
            if not hair[1].isVisible():
                    c.show()
            for c in ctrls:
                if not c.isVisible():
                    c.show()
                c.centerPivots(val=True)
                c.hide()
            hair[1].hide()
        pm.select(hair[0][0], r=1)
        selHair(setPivot=True)
        Cgroups.append(hair[1])
    pm.select(Cgroups, r=1)

def delHair(dType='self', keepHair=False):
    ''' delete Hair with Controls or Control only'''
    sel = pm.selected()
    newAttr =['lengthDivisions','widthDivisions']
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    Cgroups = [h[1] for h in hairInfoAll]
    hairMeshes = [h[0][0] for h in hairInfoAll]
    if not keepHair:
        pm.delete(hairMeshes)
        pm.delete(Cgroups)
    else:
        if dType == 'all':
            for hair in hairMeshes:
                pm.select(hair, r=1)
                selHair(setPivot=True)
                pm.xform(hair,ws=1,piv=pm.xform(Cgroups[hairMeshes.index(hair)],q=1,ws=1,piv=1)[:3])
                pm.delete(hair,ch=True)
                for a in newAttr:
                    if (pm.attributeQuery(a, exists=1, node=hair)):
                        pm.deleteAttr(hair+"."+a)
            pm.delete(Cgroups)
        elif (dType == 'self' or dType == 'above' or dType == 'below'):
            for ob in sel:
                ctrls = Cgroups[sel.index(ob)].listRelatives(type=pm.nt.Transform)
                if ctrls.count(ob):
                    if dType == 'self' or ctrls.index(ob) == 0 or ctrls.index(ob) == (len(ctrls)-1):
                        pm.delete(ob)
                    elif dType == 'above':
                        pm.delete(ctrls[ctrls.index(ob)+1:])
                        pm.scale(ctrls[ctrls.index(ob)], [0.001,0.001,0.001], a=1)
                    elif dType == 'below':
                        pm.delete(ctrls[:ctrls.index(ob)])
                        pm.scale(ctrls[ctrls.index(ob)], [0.001,0.001,0.001], a=1)
            for hair in hairMeshes:
                pm.select(hair)
                selHair(rebuild=[True,
                                 hair.attr('lengthDivisions').get(),
                                 hair.attr('widthDivisions').get()])

def cleanHairMesh():
    ''' remove All Hair Control in scene'''
    allMesh = pm.ls(g=1)
    allMeshTransform = [m.getParent() for m in allMesh]
    pm.select(allMeshTransform, r=1)
    delHair(keepHair=True)
    pm.select(d=1)
    if pm.objExists("HairCtrlGroup"):
        pm.delete("HairCtrlGroup",hi='below')
    if pm.objExists("HairBaseProfileCurve"):
        pm. delete("HairBaseProfileCurve")

def ToggleHairCtrlVis(state='switch'):
    hairCtrlsGroup=pm.ls('HairCtrlGroup')[0]
    if not hairCtrlsGroup:
        return
    if state=='switch':
        pass
    elif state=='show':
        pm.showHidden(hairCtrlsGroup,below=True)
    elif state=='hide':
        pm.hide([ctrl.getChildren() for ctrl in hairCtrlsGroup.getChildren()])

def pickWalkHairCtrl(d='right', add=False):
    '''Pick Walk and hide Controls'''
    sel=pm.selected()
    hairInfoAll = selHair(returnInfo=True)
    if not hairInfoAll:
        return
    ToggleHairCtrlVis(state='hide')
    if d == 'up':
        pm.select([h[0][0] for h in hairInfoAll])
        selHair()
        for o in pm.selected():
            o.show()
    elif d == 'down':
        pm.select([h[0][0] for h in hairInfoAll])
        selHair(selectTip=True)
        for o in pm.selected():
            o.show()
    else:
        ctrlGroups= [h[1] for h in hairInfoAll]
        for ob in sel:
            ctrls = ctrlGroups[sel.index(ob)].listRelatives(type=pm.nt.Transform)
            if ctrls.count(ob):
                for c in ctrls:
                    c.show()
                pm.select(ob, add=1)
            else:
                selHair(selectTip=True)
                for c in ctrls:
                    c.show()
        pm.pickWalk(d=d)

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
def sysCop(src,dest):
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
    except (IOError,OSError) as why:
        print src
        print dest
        print "Copy error\n",why
def mirrorUV(dir='Left'):
    if dir=='Left':
        pm.polyEditUV(u=-0.5)
    else:
        pm.polyEditUV(u=0.5)
    pm.polyFlipUV()
def rotateUV():
    sel=pm.selected()
    for o in sel:
        selShape=o.listRelatives(shapes=1)[0]
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
def getSceneRelatedData(getPath=True):
    CHPath= 'Model/CH'
    texexts=['jpg','png']
    psdexts=['psd','psb']
    sceneNameData=pm.sceneName().split('/')[-1].split('_')
    CHPathDict={}
    CHPathDict['Projectname']=sceneNameData[0]
    CHPathDict['CHname']=sceneNameData[1]
    CHPathDict['CHversion']=sceneNameData[2]
    CHPathDict['fileDir'] = os.path.normpath(os.path.join(pm.workspace.path,'scenes'))
    CHPathDict['texDir'] = os.path.normpath(os.path.join(pm.workspace.path,'sourceimages'))
    if getPath:
        for dirName, subdirList, fileList in os.walk(CHPathDict['fileDir']):
            #print dirName,subdirList,fileList
            if dirName.rfind(CHPathDict['CHname'])!=-1 :
                CHPathDict['scenes'] = dirName
                for subdir in subdirList:
                    fullPath = os.path.join(dirName,subdir)
                    if subdir.startswith(CHPathDict['CHname']):
                        sceneFileList=[]
                        for f in os.listdir(fullPath):
                            if os.path.isfile(os.path.join(fullPath,f)) and f.endswith('mb'):
                                sceneFileList.append(os.path.join(fullPath,f))
                            if os.path.isdir(os.path.join(fullPath,f)):
                                subdirFullPath=os.path.join(fullPath,f)
                                for subfile in os.listdir(subdirFullPath):
                                    if os.path.isfile(os.path.join(subdirFullPath,subfile)) and subfile.endswith('mb'):
                                        sceneFileList.append(os.path.join(subdirFullPath,subfile))
                        CHPathDict['sceneFiles']=sorted(sceneFileList,key=os.path.getmtime,reverse=True)
                break
        for dirName, subdirList, fileList in os.walk(CHPathDict['texDir']):
            #print dirName,subdirList,fileList
            if dirName.rfind(CHPathDict['CHname'])!=-1 :
                CHPathDict['sourceimages'] = dirName
                for subdir in subdirList:
                    fullPath = os.path.join(dirName,subdir)
                    #if subdir.startswith(CHPathDict['CHname']):
                    texFilesList=[]
                    for f in os.listdir(fullPath):
                        if os.path.isfile(os.path.join(fullPath,f)) and any([f.endswith(ext) for ext in texexts]):
                            texFilesList.append(os.path.join(fullPath,f))
                        if os.path.isdir(os.path.join(fullPath,f)):
                            subdirFullPath=os.path.join(fullPath,f)
                            for subfile in os.listdir(subdirFullPath):
                                if os.path.isfile(os.path.join(subdirFullPath,subfile)) and any([subfile.endswith(ext) for ext in psdexts]):
                                    texFilesList.append(os.path.join(subdirFullPath,subfile))
                    CHPathDict['texFile']=texFilesList
                break
    return CHPathDict
def setTexture():
    for m in oHairSG:
        fileList=[file for file in m.listConnections() if type(file)==pm.nodetypes.File]
    for f in fileList:
        for d in f.listAttr():
            try:
                if d.longName(fullPath=False).lower().endswith('texturename'):
                    print d,d.get()
                    d.set(d.get().replace('KG','IB'))
                    print d.get()
            except:
                continue