import pymel.core as pm
import maya.cmds as cmds
def makeCurveTube():
    pathTransform = pm.selected()
    if not pathTransform:
        print "Select some Curves"
        return
    pathShape = pm.listRelatives(shapes=True)
    if pm.nodeType(pathShape[0])=='nurbsCurve':
        pathCurve=[(i,pathShape[pathTransform.index(i)]) for i in pathTransform]
        profileCurve = pm.circle(c=(0,0,0), nr=(0,1,0), sw=360, r=1, d=3, ut=0, tol=5.77201e-008, s=8, ch=1, name='extrudeprofileCurve#')
        for crv in pathCurve:
            #profileInstance = instance(profileCurve,n="pCrv_instance"+string(pathCurve.index(crv)))
            mPath=pm.pathAnimation(profileCurve,crv[0],fa='y',ua='x')
            HairProfile =[]
            for u in range(4):
                pm.setAttr(mPath+".uValue",float(u))
                profileInstance = pm.instance(profileCurve,n="proFileCrv_"+str(u))
                if u!= 2:
                    profileInstance[0].setAttr('scale',(0.01,0.01,0.01))
                if u==0:
                    pm.delete(profileInstance)
                else:
                    HairProfile.append(profileInstance)
            pm.select(HairProfile)
            pm.nurbsToPolygonsPref(pt=1,un=4,vn=7)
            HairMesh=pm.loft(n="HairMesh",po=1,ch=1,u=1,c=0,ar=1,d=3,ss=1,rn=0,rsn=True)
            #print HairMesh
            if str(cmds.getAttr('defaultRenderGlobals.ren'))=='vray':
                HairShape = pm.listRelatives(HairMesh[0],shapes=True)
                cmds.vray('addAttributesFromGroup', HairShape[0], "vray_opensubdiv", 1)
            HairMesh[0].addAttr('width',min=0.1,at='double',dv=1)
            HairMesh[0].addAttr('orientation',min=-360,max=360,at='long',dv=1)
            HairMesh[0].addAttr('lengthDivisions',min=1,at='long',dv=7)
            HairMesh[0].addAttr('widthDivisions',min=4,at='long',dv=4)
            HairMesh[0].setAttr('width',e=1,k=1)
            HairMesh[0].setAttr('orientation',e=1,k=1)
            HairMesh[0].setAttr('lengthDivisions',e=1,k=1)
            HairMesh[0].setAttr('widthDivisions',e=1,k=1)
            HairTess= pm.listConnections(HairMesh)[3]
            HairWidth=pm.listConnections(pm.listRelatives(HairProfile[0]))[0]
            for hp in HairProfile:
                #print hp
                HairMesh[0].connectAttr('orientation',hp[0]+".rotateY")
            HairMesh[0].connectAttr('width',HairWidth+".radius")
            HairMesh[0].connectAttr('widthDivisions',HairTess+".uNumber")
            HairMesh[0].connectAttr('lengthDivisions',HairTess+".vNumber")
            pm.delete(mPath)
        pm.delete(profileCurve)

