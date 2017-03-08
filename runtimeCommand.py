import pymel.core as pm
import PipelineTools.utilities as ul
def setCommand():
    importCommand="import PipelineTools.utilities as ul\nreload(ul)"
    commandsDict={}
    hairCommandsDict={}
    hairCommandsDict['MakeHair']="\n".join([importCommand,"ul.makeHairMesh()"])
    hairCommandsDict['DuplicateHair']="\n".join([importCommand,"ul.dupHairMesh()"])
    hairCommandsDict['MirrorHair']="\n".join([importCommand,"ul.dupHairMesh(mirror=True)"])
    hairCommandsDict['SelectHairRoot']="\n".join([importCommand,"ul.selHair(selectRoot=True)"])
    hairCommandsDict['SelectHairInner']="\n".join([importCommand,"ul.selHair(selectInner=True)"])
    hairCommandsDict['SelectHair']="\n".join([importCommand,"ul.selHair()"])
    hairCommandsDict['SelectAllControls']="\n".join([importCommand,"ul.selHair(selectAll=True)"])
    hairCommandsDict['SetHairPivot']="\n".join([importCommand,"ul.selHair(setPivot=True)"])
    hairCommandsDict['HideAllHair']="\n".join([importCommand,"ul.hideHairCtrl(allHide=True)"])
    hairCommandsDict['DeleteHairAll']="\n".join([importCommand,"ul.delHair()"])
    hairCommandsDict['DeleteHairControl']="\n".join([importCommand,"ul.delHair(keepHair=True)"])
    commandsDict['HairOps']=hairCommandsDict
    for category in commandsDict:
        for command in commandsDict[category]:
            if pm.windows.runTimeCommand(command,q=1,exists=1):
                pm.windows.runTimeCommand(command,edit=1,delete=1)
            pm.windows.runTimeCommand(command,category=category,command=commandsDict[category][command],she=1)