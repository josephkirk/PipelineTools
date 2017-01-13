import pymel.core as pm
import maya.cmds as cm
import maya.mel as mm
import pymel.core as pm
#### For running in mayapy
try: 			
    import maya.standalone 			
    maya.standalone.initialize() 		
except: 			
    pass
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
        