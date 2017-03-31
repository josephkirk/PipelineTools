import pymel.core as pm
import os
from os import listdir
from os.path import join, isdir, normpath, isfile, getmtime
projectRoot = pm.workspace.path
class Asset:
    def __init__(self, name, type, kind):
        self.kind = kind
        self.type = type
        self.name = name
        self.ID = 0
        self.path = ""
        self.texPath = ""
        self.get()
        #self.getFiles()
    def get(self):
        RootPath = normpath(join(projectRoot, 'scenes', self.kind, self.type))
        RootTexPath = normpath(join(projectRoot,'sourceimages', self.kind, self.type))
        if not isdir(RootPath) and not isdir(RootTexPath):
            print "These directories are not exist, please create them:\n\t%s\n\t%s" % (CHPath,CHTexPath)
            return
        for dir in listdir(RootPath):
            if self.name in dir:
                self.path = join(RootPath,dir)
                if isdir(join(RootTexPath,dir)):
                    self.texPath = join(RootTexPath,dir)
                if dir.split('_')[0].isdigit():
                    self.ID = int(dir.split('_')[0])
                else:
                    self.ID = listdir(CHPath).index(dir)

class Character(Asset):
    def __init__(self, name):
        self.kind = 'Model'
        self.type = 'CH'
        Asset.__init__(self, name, self.type, self.kind)
        self.get()
    def rename(self, newName):
        self.name = newName
        self.get()
    def get(self):
        Asset.get(self)
        self.texCommon = [d for d in listdir(self.texPath) if 'common' in d.lower()]
        if self.texCommon:
            self.texCommon = join(self.texPath,self.texCommon[0])
        self.version = ([d.split('_')[1] for d in listdir(self.path)
                         if self.name.lower() in d.lower()])
        self.version.sort()
    def __getitem__(self,*args):
        version = []
        if not self.version:
            return version
        for v in self.version:
            version.append(subCharacter(self.name,v))
        if not args:
            return version
        else:
            if len(args)<2:
                return version[args[0]]
            else:
                result = []
                for arg in args:
                    result.append(version[arg])
                return result
    def getChild(self):
        return self.__getitem__()

class subCharacter(Character):
    def __init__(self, name, version):
        Character.__init__(self, name)
        self.getversion(version)
    def getversion(self, version):
        def collectdir(dirDict):
            for d in listdir(dirDict['..']):
                fullPath = join(dirDict['..'],d) 
                if isdir(fullPath):
                    dirDict[d.lower()] = fullPath
        if version in self.version:
            self.version = version
            self.name = '_'.join([self.name, self.version])
            RootPath = join(self.path,self.name)
            self.path = {}
            self.path['..'] = RootPath
            collectdir(self.path)
            RootTexPath = join(self.texPath,self.name)
            self.texPath = {}
            self.texPath['..'] = RootTexPath
            #for d in lisdir(self.texPath['..']):
            #    for k in ['psd','pattern','uv']
            collectdir(self.texPath)
    #         self.files = []
    # def getScene(self, **kwargs):
    #     #pass
    #     def getfiles(k):
    #         self.files = []
    #         if self.path.has_key(k):
    #             for f in listdir(self.path[k]):
    #                 fullPath = join(self.path[k],f)
    #                 if (f.endswith('mb') and isfile(fullPath)):
    #                     self.files.append(fullPath)
    #         else:
    #             print "no %s directory in %s" % (k, self.path['..'])
    #         self.files.sort(key=getmtime)
    #     for key, value in kwargs.iteritems():
    #         print key,value
    #         if key == 'a' or key == 'all' and value == True:
    #             for d in self.path:
    #                 getfiles(d)
    #             #return self.files
    #         if key == 'h' or key == 'hair' and value == True:
    #             getfiles('..')
    #             #return self.files
    #         if key == 'cl' or key == 'cloth' and value == True:
    #             getfiles('clothes')
    #             #return self.files
    #         if key == 'q':
    #             return self.files
    #         if key == 'opn' or key == 'openNewest' and value == True:
    #             if self.files:
    #                 #self.files.sort(key=getmtime)
    #                 pm.openFile(self.files[-1],f=1)
    #             # else:
    #             #     getfiles('..')
    #                 #self.files.sort(key=getmtime)
    #                 # pm.openFile(self.files[-1],f=1)
    #         if key == 'gn' or key == 'getNewest' and value == True:
    #             if self.files:
    #                 #self.files.sort(key=getmtime)
    #                 return self.files[-1]
    #             # else:
    #             #     getfiles('..')
    #             #     #self.files.sort(key=getmtime)
    #             #     return self.files[-1]
                    