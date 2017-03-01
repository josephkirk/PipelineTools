import pymel.core as pm
import maya.cmds as cm
import maya.mel as mm
import shutil
import os
import random as rand

###misc function

###function
def exportCam():
    FBXSettings = [
        "FBXExportBakeComplexAnimation -v true;"
        "FBXExportCameras -v true;"
        "FBXProperty Export|AdvOptGrp|UI|ShowWarningsManager -v false;"
        "FBXProperty Export|AdvOptGrp|UI|GenerateLogData -v false;"
    ]
    for s in FBXSettings:
        mm.eval(s)
    excludedList= ['frontShape','sideShape','perspShape','topShape']
    cams= [(cam,pm.listTransforms(cam)[0]) for cam in pm.ls(type='camera') if str(cam.name()) not in excludedList]
    scenePath =  [str(i) for i in pm.sceneName().split("/")]
    stripScenePath = scenePath[:-1]
    sceneName = scenePath[-1]
    print sceneName
    filename = "_".join([sceneName[:-3],'ConvertCam.fbx'])
    stripScenePath.append(filename)
    filePath = "/".join(stripScenePath)
    for c in cams:
        pm.select(c[1])
        oldcam = c[1]
        newcam=pm.duplicate(oldcam,rr=True)[0]
        startFrame = int(pm.playbackOptions(q=True,minTime=True))
        endFrame = int(pm.playbackOptions(q=True,maxTime=True))
        pm.parent(newcam,w=True)
        for la in pm.listAttr(newcam,l=True):
            attrName= '.'.join([newcam.name(),str(la)])
            pm.setAttr(attrName,l=False)
        camconstraint = pm.parentConstraint(oldcam,newcam)
        pm.bakeResults(newcam,at=('translate','rotate'),t=(startFrame,endFrame),sm=True)
        pm.delete(camconstraint)
        pm.select(newcam,r=True)
        cc = 'FBXExport -f "%s" -s' % filePath
        mm.eval(cc)
        
def addVrayOpenSubdivAttr():
    sel = pm.selected()
    if not sel:
        return
    for o in sel:
        if str(cm.getAttr('defaultRenderGlobals.ren'))=='vray':
                    obShape = pm.listRelatives(o,shapes=True)[0]
                    cm.vray('addAttributesFromGroup', obShape, "vray_opensubdiv", 1)
                    pm.setAttr(obShape+".vrayOsdPreserveMapBorders",2)

def createPointParent(ob,name="PointParent#",shapeReplace=False,r=1):
    obOldParent = ob.getParent()
    obNewParent = pm.polySphere(subdivisionsAxis=6,subdivisionsHeight=4,radius=r)
    for a in [('castsShadows',0),('receiveShadows',0),('smoothShading',0),('primaryVisibility',0),('visibleInReflections',0),('visibleInRefractions',0),('overrideEnabled',1),('overrideShading',0),('overrideTexturing',0),('overrideRGBColors',1),('overrideColorRGB',(1,0,0))]:
        obNewParent[0].listRelatives(shapes=1)[0].attr(a[0]).set(a[1])
    if not shapeReplace:
        pm.xform(obNewParent[0],ws=1,t=pm.xform(ob,q=1,ws=1,t=1))
        pm.xform(obNewParent[0],ws=1,ro=pm.xform(ob,q=1,ws=1,ro=1))
        #pm.color(obNewParent[0],rgb=(1,0,0))
        #obNewParent.setAttr("translate",obPos)
        if obOldParent:
            pm.parent(obNewParent[0],obOldParent)
        pm.parent(ob,obNewParent[0])
    else:
        pm.parent(ob.listsRelatives(shapes=1)[0],obNewParent,r=1,s=1)
        pm.delete(obNewParent)
def makeHairMesh(name="HairMesh#",mat="",cSet=["hairSideCrease","hairPointCrease"],reverse=False,lengthDivs=7,widthDivs=4,Segments=4,width=1,curveDel=False):
    sel = pm.selected()
    if not sel:
        print "Select some Curves or Edges or isopram"
        return
    if type(sel[0])==pm.general.MeshEdge:
        pm.runtime.CreateCurveFromPoly()
        pathTransform=pm.selected()[0]
    elif type(sel[0])==pm.general.NurbsSurfaceIsoparm:
        pm.runtime.DuplicateCurve()
        pathTransform=pm.selected()[0]
    pathTransform=[t for t in pm.selected() if type(t)==pm.nodetypes.Transform]
    pm.select(pathTransform,r=1)
    pathShape = pm.listRelatives(shapes=True)
    if type(pathShape[0])==pm.nodetypes.NurbsCurve:
        pathCurve=[(i,pathShape[pathTransform.index(i)]) for i in pathTransform]
        if pm.objExists("HairBaseProfileCurve"):
            profileCurve = pm.ls("HairBaseProfileCurve")[0]
            print profileCurve.listRelatives()[0].listConnections()[0]
            profileCurve.listRelatives()[0].listConnections()[0].setRadius(width)
            pm.showHidden(profileCurve,a=1)
        else:
            profileCurve = pm.circle(c=(0,0,0), nr=(0,1,0), sw=360, r=width, d=3, ut=0, tol=5.77201e-008, s=8, ch=1, name="HairBaseProfileCurve")
            for a in [('overrideEnabled',1),('overrideRGBColors',1),('overrideColorRGB',(.2,1,0))]:
                profileCurve[0].listRelatives(shapes=1)[0].attr(a[0]).set(a[1])
        pm.select(d=1)
        for crv in pathCurve:
            print crv
            pm.rebuildCurve(crv[0],kep=1)
            if reverse:
                pm.reverseCurve(crv[0])
            #profileInstance = instance(profileCurve,n="pCrv_instance"+string(pathCurve.index(crv)))
            if pm.objExists("HairCtrlGroup"):
                hairOncsGroup=pm.ls("HairCtrlGroup")[0]
            else:
                hairOncsGroup=pm.group(name="HairCtrlGroup")
            #pm.parent(hairOncGroup,crv[0])
            mPath=pm.pathAnimation(profileCurve,crv[0],fa='y',ua='x',stu=1,etu=Segments*10,b=1)
            HairProfile =[]
            hairOncGroup=pm.group(name="HairCtrls#")
            pm.parent(hairOncGroup,hairOncsGroup,r=1)
            for u in range(Segments+1):
                pm.currentTime(u*10)
                #profileInstance=pm.instance("HairBaseProfileCurve",n=(crv[0]+"HairProFileCrv_"+str(u)))[0]
                profileInstance=pm.duplicate(profileCurve,n=(crv[0]+"HairProFileCrv_"+str(u)),rr=1)[0]
                pm.parent(profileInstance,hairOncGroup,r=1)
                #profileTransform=pm.createNode('transform',n=(crv[0]+"HairProFileTF_"+str(u)),p=profileInstance)
                HairProfile.append(profileInstance)
                if u==0:
                    pm.scale(profileInstance,[0.01,0.01,0.01],a=1,os=1)
                    createPointParent(profileInstance,name=crv[0]+"HairRoot_Ctrl_"+str(pathCurve.index(crv)),r=width)
                if u==Segments:
                    pm.scale(profileInstance,[0.01,0.01,0.01],a=1,os=1)
                    createPointParent(profileInstance,name=crv[0]+"HairTop_Ctrl_"+str(pathCurve.index(crv)),r=width)
            pm.select(HairProfile,r=1)
            pm.nurbsToPolygonsPref(pt=1,un=4,vn=7,f=2)
            HairMesh=pm.loft(n=name,po=1,ch=1,u=1,c=0,ar=1,d=3,ss=1,rn=0,rsn=True)
            pm.rename(hairOncGroup,hairOncGroup.name()+HairMesh[0].name())
            HairMesh[0].addAttr('lengthDivisions',min=1,at='long',dv=lengthDivs)
            HairMesh[0].addAttr('widthDivisions',min=4,at='long',dv=widthDivs)
            HairMesh[0].setAttr('lengthDivisions',e=1,k=1)
            HairMesh[0].setAttr('widthDivisions',e=1,k=1)
            HairTess= pm.listConnections(HairMesh)[-1]
            HairMesh[0].connectAttr('widthDivisions',HairTess+".uNumber")
            HairMesh[0].connectAttr('lengthDivisions',HairTess+".vNumber")
            HairMeshShape= HairMesh[0].listRelatives(shapes=1)[0]
            pm.select(HairMeshShape.e[0,2])
            pm.runtime.SelectEdgeLoopSp()
            sideEdges=pm.selected()
            pm.select(HairMeshShape.e[0])
            pm.runtime.SelectEdgeRingSp()
            pointEdges=pm.selected()
            if bool(pm.ls(cSet[0],type=pm.nodetypes.CreaseSet)):
                hsSet=pm.ls(cSet[0],type=pm.nodetypes.CreaseSet)[0]
            else:
                hsSet = pm.nodetypes.CreaseSet(name=cSet[0])
                hsSet.setAttr('creaseLevel',1.6)
            if bool(pm.ls(cSet[1],type=pm.nodetypes.CreaseSet)):
                hpSet=pm.ls(cSet[1],type=pm.nodetypes.CreaseSet)[0]
            else:
                hpSet = pm.nodetypes.CreaseSet(name=cSet[1])
                hpSet.setAttr('creaseLevel',2.0)
            for e in sideEdges:
                pm.sets(hsSet,forceElement=e)
            for e in pointEdges:
                pm.sets(hpSet,forceElement=e)
            pm.delete(profileCurve,mp=1)
            pm.delete(profileCurve)
            pm.xform(hairOncsGroup,pivots=HairProfile[0].getTranslation(space='world'),ws=1)
            pm.select(HairMesh[0],r=1)
            HairUV = HairMeshShape.map
            pm.polyEditUV(HairUV,pu=0.5,pv=0.5,su=0.3,sv=1)
            pm.polyEditUV(HairUV,u=rand.uniform(-0.1,0.1))
            if str(cm.getAttr('defaultRenderGlobals.ren'))=='vray':
                addVrayOpenSubdivAttr()
            pm.displaySmoothness(po=3)
            if bool(pm.ls(mat,type=pm.nodetypes.ShadingEngine)):
                pm.sets(pm.ls(mat)[0],forceElement=HairMesh[0])
        #pm.hide(profileCurve)
        if curveDel:
            pm.delete(pathTransform,hi=1)

def dupHairMesh(mirror=False):
    hairMeshes = pm.selected()
    if not hairMeshes:
        return
    Cgroups=[]
    for hair in hairMeshes:
        try:
            loftMesh=[l for l in hair.listConnections()[0].listConnections() if type(l)==pm.nodetypes.Loft][0]
            Ctrls=[c for c in loftMesh.listConnections() if type(c)==pm.nodetypes.Transform]
            ControlGroup = Ctrls[1].getParent()
        except:
            continue
        if ControlGroup:
            pm.select(hair,ControlGroup)
            pm.duplicate(ic=1,un=1)
            if mirror:
                pm.scale(ControlGroup,-1,smn=1,p=(0,0,0),ws=1)
                pm.polyNormal(hair,nm=3)
                for c in Ctrls:
                    c.centerPivots()
                    if c.getParent() != ControlGroup:
                        c.getParent().centerPivots()
            pm.xform(ControlGroup,ws=1,piv=pm.xform(ControlGroup.getChildren()[0],q=1,ws=1,piv=1)[:3])
            Cgroups.append(ControlGroup)
    if Cgroups:
        pm.select(Cgroups)

def selHair(setPivot=False):
    hairMeshes = pm.selected()
    if not hairMeshes:
        return
    Cgroups=[]
    for hair in hairMeshes:
        try:
            loftMesh=[l for l in hair.listConnections()[0].listConnections() if type(l)==pm.nodetypes.Loft][0]
            Ctrls=[c for c in loftMesh.listConnections() if type(c)==pm.nodetypes.Transform]
            ControlGroup = Ctrls[1].getParent()
            if setPivot:
                pm.xform(ControlGroup,ws=1,piv=pm.xform(ControlGroup.getChildren()[0],q=1,ws=1,piv=1)[:3])
            Cgroups.append(ControlGroup)
        except:
            continue
        if ControlGroup:
            Cgroups.append(ControlGroup)
    if Cgroups:
        pm.select(Cgroups)
def delHair(keepHair=False):
    newAttr =['lengthDivisions','widthDivisions']
    hairMeshes = pm.selected()
    if not hairMeshes:
        return
    Cgroups=[]
    for hair in hairMeshes:
        try:
            loftMesh=[l for l in hair.listConnections()[0].listConnections() if type(l)==pm.nodetypes.Loft][0]
            Ctrls=[c for c in loftMesh.listConnections() if type(c)==pm.nodetypes.Transform]
            ControlGroup = Ctrls[1].getParent()
            Cgroups.append(ControlGroup)
        except:
            continue
    if not keepHair:
        pm.delete(hairMeshes)
        pm.delete(Cgroups)
    else:
        for hair in hairMeshes:
            pm.delete(hair,ch=True)
            for a in newAttr:
                if (pm.attributeQuery(a, exists=1, node=hair)):
                    pm.deleteAttr(hair+"."+a)
        pm.delete(Cgroups)

def cleanHairMesh():
    newAttr =['width','baseWidth','lengthDivisions','widthDivisions']
    meshes = pm.ls("HairMesh*")
    if meshes:
        for mesh in meshes:
            print mesh
            pm.delete(mesh,ch=True)
            for a in newAttr:
    #            print a
                if (pm.attributeQuery (a, exists=1, node=mesh)):
                    pm.deleteAttr (mesh+"."+a)
    if pm.objExists("HairCtrlGroup"):
        pm.delete("HairCtrlGroup",hi='below')
    if pm.objExists("HairBaseProfileCurve"):
        pm. delete("HairBaseProfileCurve")

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