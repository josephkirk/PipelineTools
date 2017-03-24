import pymel.core as pm
#HairOpsMarkingMenu_Press
#HairOpsMarkingMenu_Release
def setCommand():
    """Create RuntimeCommand for Hair Ops """
    if pm.hotkeySet('HairOps', q=1, exists=1):
        pm.hotkeySet('HairOps', edit=1, current=1)
    else:
        pm.hotkeySet('HairOps', source="Maya_Default", current=1)
    for ca in pm.windows.runTimeCommand(uca=1, q=1):
        if ca.find('HairOps') == -1:
            pm.windows.runTimeCommand(ca, edit=1, delete=1, s=1)
    #pm.nameCommand('HairOpsMarkingMenu_PressNameCommand',ann='HairMk',c=command)
    #pm.hotkey(
    #   k = '`',
    #   alt = True,
    #   n = 'HairOpsMarkingMenu_Press',
    #   rn = 'HairOpsMarkingMenu_Release')
    importCommand = "import PipelineTools.utilities as ul\nreload(ul)"
    commandsDict = {}
    hairCommands_dict = {}
    hairCommands_dict["MakeHair"] = (
        "\n".join([importCommand, "ul.makeHairMesh()"]),
        "Make Hair",
        ["", False, False, False])
    hairCommands_dict['MakeHairUI'] = (
        "\n".join(["from PipelineTools import main", "reload(main)", "main.makeHairUI()"]),
        "Make Hair UI",
        ["", False, False, False])
    hairCommands_dict['DuplicateHair'] = (
        "\n".join([importCommand, "ul.dupHairMesh()"]),
        "Duplicate Hair along with Controls",
        ["#", False, False, False])
    hairCommands_dict['MirrorHair'] = (
        "\n".join([importCommand, "ul.dupHairMesh(mirror=True)"]),
        "Mirror Hair along with Controls",
        ["%", False, False, False])
    hairCommands_dict['SelectHair'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d='up')"]),
        "Select Hair Control Root",
        ["3", False, True, False])
    hairCommands_dict['SelectAllControls'] = (
        "\n".join([importCommand, "ul.selHair(selectAll=True)"]),
        "Select All Controls of Hair",
        ["4", False, True, False])
    hairCommands_dict['SetHairPivot'] = (
        "\n".join([importCommand, "ul.selHair(setPivot=True)"]),
        "set Hair Control Root Pivot to Root",
        ["5", False, True, False])
    hairCommands_dict['SplitHairControlUp'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d='up')"]),
        "Add a Hair Control Toward Tip",
        ["2", True, True, False])
    hairCommands_dict['SplitHairControlDown'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d='down')"]),
        "Add a Hair Control Toward Root",
        ["1", True, True, False])
    hairCommands_dict['DeleteHairAll'] = (
        "\n".join([importCommand, "ul.delHair()"]),
        "Delete Hair with its controls",
        ["$", False, False, False])
    hairCommands_dict['DeleteHairControl'] = (
        "\n".join([importCommand, "ul.delHair(keepHair=True)"]),
        "Delete Hair controls but keep Hair Mesh",
        ["", False, False, False])
    hairCommands_dict['DeleteControlsUp'] = (
        "\n".join([importCommand, "ul.delHair(dType='above', keepHair=True)"]),
        "Delete All Controls From Select to Tip",
        ["4", True, True, False])
    hairCommands_dict['DeleteSelectControl'] = (
        "\n".join([importCommand, "ul.delHair(dType='self', keepHair=True)"]),
        "Delete Select Control",
        ["3", True, True, False])
    hairCommands_dict['DeleteControlsDown'] = (
        "\n".join([importCommand, "ul.delHair(dType='below', keepHair=True)"]),
        "Delete All Controls From Select to Root",
        ["5", True, True, False])
    hairCommands_dict['RebuildControlsUp'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'up', rebuild= True)"]),
        "rebuild All Controls From Select to Tip",
        ["", False, False, False])
    hairCommands_dict['RebuildSelectControl'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'self', rebuild= True)"]),
        "rebuild Select Control",
        ["", False, False, False])
    hairCommands_dict['RebuildControlsDown'] = (
        "\n".join([importCommand, "ul.splitHairCtrl(d = 'down', rebuild= True)"]),
        "rebuild All Controls From Select to Root",
        ["", False, False, False])
    hairCommands_dict['PickWalkHideRight'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'right')"]),
        "Pick Walk Right and hide last Select Control",
        ["2", False, True, False])
    hairCommands_dict['PickWalkAddRight'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'right',add= True)"]),
        "Pick Walk Right and add to last Select Control",
        ["@", False, True, False])
    hairCommands_dict['PickWalkHideLeft'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'left')"]),
        "Pick Walk Left and hide last Select Control",
        ["1", False, True, False])
    hairCommands_dict['PickWalkAddLeft'] = (
        "\n".join([importCommand, "ul.pickWalkHairCtrl(d = 'left',add= True)"]),
        "Pick Walk Left and add to last Select Control",
        ["!", False, True, False])
    hairCommands_dict['HideAllHairCtrls'] = (
        "\n".join([importCommand, "ul.ToggleHairCtrlVis(state= 'hide')"]),
        "Hide All Hair Controls",
        ["t", False, False, True])
    hairCommands_dict['ShowAllHairCtrls'] = (
        "\n".join([importCommand, "ul.ToggleHairCtrlVis(state= 'show')"]),
        "Show All Hair Controls",
        ["t", False, True, True])
    commandsDict['HairOps'] = hairCommands_dict
    nameCommandList = []
    for category in commandsDict:
        for command in commandsDict[category]:
            if pm.runTimeCommand(command, q=1, exists=1):
                pm.runTimeCommand(command, edit=1, delete=1, s=1)
            pm.runTimeCommand(command,
                              category=category,
                              command=commandsDict[category][command][0])
            nameCommand = pm.nameCommand(
                command+"NameCommand",
                ann=commandsDict[category][command][1],
                c=command)
            nameCommandList.append((nameCommand,
                                    commandsDict[category][command][2]))
    for nc in nameCommandList:
        print nc
        if nc[1][0]:
            print "hotKey is %s" % nc[1][0]
            pm.hotkey(keyShortcut=nc[1][0], ctl=nc[1][1], alt=nc[1][2], sht=nc[1][3], n=nc[0])

