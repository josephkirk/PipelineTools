import pymel.core as pm
from PipelineTools import utilities as ul
"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
def setHotkeys():
    if pm.hotkeySet('Custom', q=1, exists=1):
        pm.hotkeySet('Custom', edit=1, current=1)
    else:
        pm.hotkeySet('Custom', source="Maya_Default", current=1)
    if pm.windows.runTimeCommand(uca=1, q=1):
        for ca in pm.windows.runTimeCommand(uca=1, q=1):
            if ca.find('Custom') == -1:
                pm.windows.runTimeCommand(ca, edit=1, delete=1, s=1)
    import_command = "import PipelineTools.utilities as ul\nreload(ul)"
    commands_dict = {}
    skin_utilities_dict = {}
    skin_utilities_dict['BindPose'] =(
        "GoToBindPose", #Command
        "BindPose", #Command Name
        ['2', True, True, False] # Key, Ctrl, Alt, Shift
    )
    skin_utilities_dict['PaintWeight'] =(
        "artAttrSkinToolScript 3", #Command
        "PaintWeight", #CommandName
        ['1', True, True, False] # Key, Ctrl, Alt, Shift
    )
    weight_tick = 5
    weight_value = 1.0/(weight_tick-1)
    for i in range(weight_tick):
        format_value = '%04.2f'%(weight_value*i)
        format_value = "".join(format_value.split('.'))
        skin_utilities_dict['SetWeight%s'%(format_value)] = (
            "\n".join([import_command,
                       "ul.skin_weight_setter(skin_value=%s, normalized=False)"%(weight_value*i)]),
            "SetWeightTo%s"%(format_value),
            ["%d"%(i+1), False, True, False])
    commands_dict['skin_tool'] = skin_utilities_dict
    nameCommandList = []
    for category in commands_dict:
        for command in commands_dict[category]:
            if pm.runTimeCommand(command, q=1, exists=1):
                pm.runTimeCommand(command, edit=1, delete=1, s=1)
            pm.runTimeCommand(command,
                              category=category,
                              command=commands_dict[category][command][0])
            nameCommand = pm.nameCommand(
                command+"NameCommand",
                ann=commands_dict[category][command][1],
                c=command)
            nameCommandList.append((nameCommand,
                                    commands_dict[category][command][2]))
    for nc in nameCommandList:

        if nc[1][0]:

            pm.hotkey(keyShortcut=nc[1][0], ctl=nc[1][1], alt=nc[1][2], sht=nc[1][3], n=nc[0])