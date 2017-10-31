
# Author:		Steven T. L. Roselle
#
# Created:        ( 04/01/15 )

from pymel.core import *
import maya.cmds as cmds


def curveToTube():
        
    select(filterExpand(sm=9),r=1)
    curves = ls(sl=1)    
    
    if (curves.__len__()):

           
        allInstances = []
        allProfiles = []
        allMeshes = []
          
        for crv in curves:

            # Create unique profile curvve
            profileCurve = circle(c=(0,0,0), nr=(0,1,0), sw=360, r=1, d=3, ut=0, tol=5.77201e-008, s=8, ch=1, name='extrudeprofileCurve#')
            scale (0.5, 0.5, 0.5)
            #curve( name=crv+'_profile',p=[(0, -0.25, 0.5), (0, 0.5, 0.5), (0, 0.5, -0.5), (0, -0.25, -0.5)] )
            #profileCurve = ls(sl=1) 
        
            # Move pivot of curve to first CV
            curveOrigin = pointPosition(crv+'.cv[0]', w=1)
            crv.setRotatePivot([curveOrigin])
            crv.setScalePivot([curveOrigin])
            
                                    
            # instance curve and move to origin
            curveInstance = instance(crv, n=crv+'_instance#')
            move(0,0,0, curveInstance, rpr=1)
            curveInstance[0].setAttr("rx",0)
            curveInstance[0].setAttr("ry",0)
            curveInstance[0].setAttr("rz",0)
            curveInstance[0].setAttr("sx",1)
            curveInstance[0].setAttr("sy",1)
            curveInstance[0].setAttr("sz",1)
            allInstances.append(curveInstance[0])
            allProfiles.append(profileCurve[0])
                
            # extrude curve with profiler 
            select(profileCurve[0], curveInstance,r=1)
            extrudeResult = extrude(ch=1, rn=0, po=1, et=2, ucp=2, fpt=1, upn=1, rotation=0, scale=0, rsp=1, name='TubeMesh#')
            extrudedSurface = ls(sl=1);
            extrudedSurfaceShape = listRelatives(extrudedSurface,shapes=1)[0]
            cmds.vray('addAttributesFromGroup', extrudedSurfaceShape, "vray_opensubdiv", 1)
            extrudedSurface[0].addAttr('width',min=0.1,at='double',dv=1)  
            #extrudedSurface[0].addAttr('curvature',min=-1,max=1,at='double',dv=0)  
            extrudedSurface[0].addAttr('orientation',min=-360,max=360,at='long',dv=1)  
            extrudedSurface[0].addAttr('taper',min=0,at='double',dv=0)  
            extrudedSurface[0].addAttr('twist',at='double',dv=1)  
            extrudedSurface[0].addAttr('lengthDivisionSpacing',at='enum',enumName="uniform=1:non-uniform=2", dv=1)  
            extrudedSurface[0].addAttr('lengthDivisions',min=1,at='long',dv=7)  
            extrudedSurface[0].addAttr('widthDivisions',min=4,at='long',dv=4) 
            extrudedSurface[0].setAttr('width',e=1,k=1)
            #extrudedSurface[0].setAttr('curvature',e=1,k=1)
            extrudedSurface[0].setAttr('orientation',e=1,k=1)                    
            extrudedSurface[0].setAttr('taper',e=1,k=1)
            extrudedSurface[0].setAttr('twist',e=1,k=1)
            extrudedSurface[0].setAttr('widthDivisions',e=1,k=1)
            extrudedSurface[0].setAttr('lengthDivisions',e=1,k=1)
            extrudedSurface[0].setAttr('lengthDivisionSpacing',e=1,k=1)
            

            extrudedSurface[0].connectAttr('taper',extrudeResult[1]+'.scale')
            extrudedSurface[0].connectAttr('twist',extrudeResult[1]+'.rotation')
            allMeshes.append(extrudedSurface[0])
                        
            # Setup nurbsTesselate node
            extrudeInput = listConnections(extrudeResult[1])
            extrudeInput[2].setAttr("format",2)
            extrudeInput[2].setAttr("uType",1) # uniform
            #extrudeInput[2].setAttr("vType",1)
            extrudeInput[2].setAttr("polygonType",1)
            extrudedSurface[0].connectAttr('widthDivisions',extrudeInput[2]+'.uNumber')
            extrudedSurface[0].connectAttr('lengthDivisions',extrudeInput[2]+'.vNumber')
            extrudedSurface[0].connectAttr('lengthDivisionSpacing',extrudeInput[2]+'.vType')


            #
            extrudedSurface[0].connectAttr('width',profileCurve[0]+'.sx')
            #extrudedSurface[0].connectAttr('curvature',profileCurve[0]+'.sy')
            extrudedSurface[0].connectAttr('width',profileCurve[0]+'.sz')
            extrudedSurface[0].connectAttr('orientation',profileCurve[0]+'.rx')
            #
                        

            # constrain extrude to target curve position
            select(crv, extrudedSurface[0], r=1)
            pointConstraint (w=1)
            orientConstraint (o=(0, 0, 0), w=1);
            scaleConstraint (mo=0, w=1)
             
        
        if (ls ('tubeCurveHistory')):
            select (allProfiles, allInstances, 'tubeCurveHistory', r=1)
            parent ()
        else:    
            hide (group (allProfiles, allInstances, w=1, name='tubeCurveHistory'))
            

        if (ls ('tubeMeshes')):
            select (allMeshes, 'tubeMeshes', r=1)
            parent ()
        else:    
            group (allMeshes, w=1, name='tubeMeshes')            
            
        
        select (allMeshes, r=1)    
        
                    
    else:
        warning ('No curves selected.\n')
        
                
        
#bt_curveToTubeMesh()
def cleanupCurveTube():
        
    instanceNode = ''
    extrudeNode = ''
    
    select(filterExpand(sm=12),r=1)
    select(listRelatives( parent=True))
    meshes = ls(sl=1)    
    
    if (meshes.__len__()):
        
        for mesh in meshes:        

            if (attributeQuery ('taper', exists=1, node=mesh)):
                extrudeNode = (listConnections (mesh+'.taper'))
                instanceNode = (listConnections (extrudeNode[0]+'.path'))
                        
            #delete remaining history and constraints
            delete (mesh, ch=1)
            delete (mesh, constraints=1)      
            
            if (attributeQuery ('width', exists=1, node=mesh)):
                delete(listConnections (mesh+'.width'))
                deleteAttr (mesh+".width")
            if (attributeQuery ('orientation', exists=1, node=mesh)):
                delete(listConnections (mesh+'.orientation'))
                deleteAttr (mesh+".orientation")
                 
            if (attributeQuery ('curvature', exists=1, node=mesh)):
                deleteAttr (mesh+".curvature")
            if (attributeQuery ('taper', exists=1, node=mesh)):
                deleteAttr (mesh+".taper")
            if (attributeQuery ('twist', exists=1, node=mesh)):
                deleteAttr (mesh+".twist")
            if (attributeQuery ('lengthDivisionSpacing', exists=1, node=mesh)):
                deleteAttr (mesh+'.lengthDivisionSpacing') 
            if (attributeQuery ('lengthDivisions', exists=1, node=mesh)):
                deleteAttr (mesh+".lengthDivisions")                               
            if (attributeQuery ('widthDivisions', exists=1, node=mesh)):
                deleteAttr (mesh+".widthDivisions")  
                
            if (objExists (instanceNode)):
                delete (instanceNode)
                
    else:
        warning ('No meshes selected.\n')
 
        
#bt_cleanupCurveMesh()


        