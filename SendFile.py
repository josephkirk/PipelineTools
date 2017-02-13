import os
import shutil
import time
from datetime import date
import maya.cmds as cmds
#os.mkdir(r"F:/TestFolder")
fullPath = cmds.file(q=1,sn=1).split("/")
print fullPath
srcDrive = fullPath[0]
desDrive = "F:"
projectPath = "/".join(fullPath[1:fullPath.index("scenes")])
filePath= fullPath[fullPath.index("Model"):len(fullPath)-1]
scenePath = "/".join([projectPath,u"scenes"]+filePath)
texPath = "/".join([projectPath,u"sourceimages"]+filePath)
sceneName= fullPath[len(fullPath)-1]
#textPath= scenePath[0:]
#textPath[textPath.index("scenes")]=u"sourceimages"
print drive,projectPath
print scenePath,texPath,sceneName
#print os.listdir("/".join([srcDrive,texPath]))
today = date.today()
todayFolder = "%s%02d%02d" % (str(today.year)[2:],today.month,today.day)
print "/".join([srcDrive,texPath])
print cmds.getFileList(folder="/".join([srcDrive,texPath]))
#cmds.sysFile("/".join([drive,"to",todayFolder,scenePath]),makeDir=True)
#cmds.sysFile(fullSceneName,copy="/".join([drive,"to",todayFolder,scenePath,sceneName]))
#cmds.sysFile("/".join([drive,"to",todayFolder,texPath]),makeDir=True)
