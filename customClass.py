import pymel.core as pm
from os import listdir
from os.path import join, isdir, normpath, isfile, getmtime
class Asset:
    def __init__(self, name, type, kind):
        self.kind = kind
        self.type = type
        self.name = name
        self.ID = 0
        self.scenePath = ""
        self.render = ""
        self.files = {}
        self.texPath = ""
        self.PsdPath = ""
        self.texFiles = []
        self.psdFiles = []
        self.version = {}
        #self.getPath()
        #self.getFiles()
    def getName(self):
        CHPath = normpath(join(pm.workspace.path, 'scenes', kind, type))
        CHTexPath = normpath(join(pm.workspace.path,'sourceimages', self.pathExtension))
        if not isdir(CHPath) and not isdir(CHTexPath):
            print "These directories are not exist, please create them:\n\t%s\n\t%s" % (CHPath,CHTexPath)
            return
        for dir in listdir(CHPath):
