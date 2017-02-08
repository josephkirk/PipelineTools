import pymel.core as pm
import maya.cmds as cmds
#setAttr "tubeMeshes|TubeMesh4|TubeMesh4|TubeMesh4Shape.vrayOsdPreserveMapBorders" 2;
def addVrayOpenSubdivAttr():
    sel = pm.selected()
    if not sel:
        return
    for o in sel:
        if str(cmds.getAttr('defaultRenderGlobals.ren'))=='vray':
                    obShape = pm.listRelatives(o,shapes=True)[0]
                    cmds.vray('addAttributesFromGroup', obShape, "vray_opensubdiv", 1)
                    pm.setAttr(obShape+".vrayOsdPreserveMapBorders",2)