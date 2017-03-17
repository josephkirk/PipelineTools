import pymel.core as pm
def set_command():
    """Create RuntimeCommand for Hair Ops """
    for ca in pm.windows.runTimeCommand(uca=1, q=1):
        if ca.find('HairOps') == -1:
            pm.windows.runTimeCommand(ca, edit=1, delete=1)
    importCommand = " import PipelineTools.utilities as ul\nreload(ul) "
    commandsDict = {}
    hairCommands_dict = {}
    hairCommands_dict["MakeHair"] = (
        "\n".join([importCommand, "ul.makeHairMesh()"]),
        "")
    hairCommands_dict['MakeHairUI'] = (
        "\n".join(["from PipelineTools import main", "main.makeHairUI()"]),
        "")
    hairCommands_dict['DuplicateHair'] = (
        "\n".join([importCommand, "ul.dupHairMesh()"]),
        "#")
    hairCommands_dict['MirrorHair'] = (
        "\n".join([importCommand, "ul.dupHairMesh(mirror = True)"]),
        "%")
    hairCommands_dict['SelectHair'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'up')"]),
        "Alt+3")
    hairCommands_dict['SelectAllControls'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'right',r = 1)"]),
        "Alt+4")
    hairCommands_dict['SetHairPivot'] = (
        "\n".join([importCommand, "ul.selHair(setPivot = True)"]),
        "Alt+5")
    hairCommands_dict['SplitHairControlUp'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'up')"]),
        "Ctrl+Alt+2")
    hairCommands_dict['SplitHairControlDown'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'down')"]),
        "Ctrl+Alt+1")
    hairCommands_dict['DeleteHairAll'] = (
        "\n".join([importCommand, "ul.delHair()"]),
        "$")
    hairCommands_dict['DeleteHairControl'] = (
        "\n".join([importCommand, "ul.delHair(keepHair = True)"]),
        "")
    hairCommands_dict['DeleteControlsUp'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'up',delete= True)"]),
        "Ctrl+Alt+4")
    hairCommands_dict['DeleteSelectControl'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'self',delete= True)"]),
        "Ctrl+Alt+3")
    hairCommands_dict['DeleteControlsDown'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'down',delete= True)"]),
        "Ctrl+Alt+5")
    hairCommands_dict['PickWalkHideRight'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'right')"]),
        "Alt+2")
    hairCommands_dict['PickWalkAddRight'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'right',add= True)"]),
        "Alt+@")
    hairCommands_dict['PickWalkHideLeft'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'left')"]),
        "Alt+1")
    hairCommands_dict['PickWalkAddLeft'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'left',add= True)"]),
        "Alt+!")
    hairCommands_dict['HideAllHairCtrls'] = (
        "\n".join([importCommand, "ul.ToggleHairCtrlVis(state= 'hide')"]),
        "Shift+T")
    hairCommands_dict['ShowAllHairCtrls'] = (
        "\n".join([importCommand, "ul.ToggleHairCtrlVis(state= 'show')"]),
        "Alt+Shift+T")
    commandsDict['HairOps'] = hairCommands_dict
    for category in commandsDict:
        for command in commandsDict[category]:
            if pm.windows.runTimeCommand(command, q=1, exists=1):
                pm.windows.runTimeCommand(command, edit=1, delete=1)
            pm.windows.runTimeCommand(command, category=category,
                                      command=commandsDict[category][command][0],
                                      hc=commandsDict[category][command][1],
                                      she=1)
