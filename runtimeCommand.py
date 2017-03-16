import pymel.core as pm
import PipelineTools.utilities as ul
def setCommand():
    importCommand="import PipelineTools.utilities as ul\nreload(ul)"
    commandsDict={}
    hairCommandsDict={}
    hairCommandsDict['MakeHair']="\n".join([importCommand,"ul.makeHairMesh()"])
    hairCommandsDict['MakeHairUI']="\n".join([importCommand,"from PipelineTools import main; main.makeHairUI()"])
    hairCommandsDict['DuplicateHair']="\n".join([importCommand,"ul.dupHairMesh()"])
    hairCommandsDict['MirrorHair']="\n".join([importCommand,"ul.dupHairMesh(mirror=True)"])
    hairCommandsDict['SelectHairRoot']="\n".join([importCommand,"ul.selHair(selectRoot=True)"])
    hairCommandsDict['SelectHairInner']="\n".join([importCommand,"ul.selHair(selectTip=True)"])
    hairCommandsDict['SelectHair']="\n".join([importCommand,"ul.pickWalkHairCtrl(d='up')"])
    hairCommandsDict['SelectAllControls']="\n".join([importCommand,"ul.pickWalkHairCtrl(d='right',r=1)"])
    hairCommandsDict['SetHairPivot']="\n".join([importCommand,"ul.selHair(setPivot=True)"])
    hairCommandsDict['SplitHairControlUp']="\n".join([importCommand,"ul.splitHairCtrl(d='up')"])
    hairCommandsDict['SplitHairControlDown']="\n".join([importCommand,"ul.splitHairCtrl(d='down')"])
    hairCommandsDict['DeleteHairAll']="\n".join([importCommand,"ul.delHair()"])
    hairCommandsDict['DeleteHairControl']="\n".join([importCommand,"ul.delHair(keepHair=True)"])
    hairCommandsDict['DeleteControlsUp']="\n".join([importCommand,"ul.splitHairCtrl(d='up',delete=True)"])
    hairCommandsDict['DeleteSelectControl']="\n".join([importCommand,"ul.splitHairCtrl(d='self',delete=True)"])
    hairCommandsDict['DeleteControlsDown']="\n".join([importCommand,"ul.splitHairCtrl(d='down',delete=True)"])
    hairCommandsDict['PickWalkHideRight']="\n".join([importCommand,"ul.pickWalkHairCtrl(d='right')"])
    hairCommandsDict['PickWalkAddRight']="\n".join([importCommand,"ul.pickWalkHairCtrl(d='right',add=True)"])
    hairCommandsDict['PickWalkHideLeft']="\n".join([importCommand,"ul.pickWalkHairCtrl(d='left')"])
    hairCommandsDict['PickWalkAddLeft']="\n".join([importCommand,"ul.pickWalkHairCtrl(d='left',add=True)"])
    hairCommandsDict['ToggleHairCtrlVisibility']="\n".join([importCommand,"ul.ToggleHairCtrlVis()"])
    commandsDict['HairOps']=hairCommandsDict
    for category in commandsDict:
        for command in commandsDict[category]:
            if pm.windows.runTimeCommand(command,q=1,exists=1):
                pm.windows.runTimeCommand(command,edit=1,delete=1)
            pm.windows.runTimeCommand(command,category=category,command=commandsDict[category][command],she=1)