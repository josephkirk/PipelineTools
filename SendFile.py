import os
import shutil
import time
from datetime import date
import maya.cmds as cmds
#path declaration
fullPath = cmds.file(q=1,sn=1).split("/")
srcDrive = fullPath[0]
desDrive = "N:"
projectPath = "/".join(fullPath[1:fullPath.index("scenes")])
filePath= fullPath[fullPath.index("Model"):len(fullPath)-1]
scenePath = "/".join([projectPath,u"scenes"]+filePath)
texPath = "/".join([projectPath,u"sourceimages"]+filePath)
sceneName= fullPath[len(fullPath)-1]
today = date.today()
todayFolder = "%s%02d%02d" % (str(today.year)[2:],today.month,today.day)
sceneSrc = "/".join([srcDrive,scenePath])
texSrc= "/".join([srcDrive,texPath])
sceneDest = "/".join([srcDrive,"to",todayFolder,scenePath])
texDest = "/".join([srcDrive,"to",todayFolder,texPath]

###Execution
cmds.sysFile(sceneDest,makeDir=True)
print "scene folder Created"
os.shutil.copy(sceneSrc+sceneName,sceneDest)
print "file copied"
if 
    if f=="rend":
        try:
            shutil.copytree("/".join([srcDrive,scenePath,"rend"]),"/".join([srcDrive,"to",todayFolder,scenePath,"rend"]))
            print "Render Copied"
        except:
            print "copy render error"
cmds.sysFile("/".join([srcDrive,"to",todayFolder,texPath]),makeDir=True)
print "sourceimages created"
for d in os.listdir("/".join([srcDrive,texPath])):
    if d=="_Common":
        try:
            shutil.copytree("/".join([srcDrive,texPath,"_Common"]),"/".join([srcDrive,"to",todayFolder,texPath,"_Common"]))
            print "Texture Copied"
        except:
            print "error"