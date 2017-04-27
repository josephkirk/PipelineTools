import os
from os import listdir
from os.path import join, isdir, normpath, isfile, getmtime, abspath, exists
import pymel.core as pm
projectRoot = pm.workspace.path
class Asset(object):
    '''Base Class to find AssetPath'''
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
        RootTexPath = normpath(join(projectRoot, 'sourceimages', self.kind, self.type))
        XgenPath = normpath(join(projectRoot, 'xgen', 'collections'))
        if not isdir(RootPath) and not isdir(RootTexPath):
            print "These directories are not exist, please create them:\n\t%s\n\t%s" % (RootPath,RootTexPath)
            return
        CHList = []
        if XgenPath:
            for d in listdir(XgenPath):
                if self.name in d:
                    self.xgenPath = join(XgenPath, d)
        for d in listdir(RootPath):
            if self.name in d:
                self.path = join(RootPath, d)
                if isdir(join(RootTexPath, d)):
                    self.texPath = join(RootTexPath, d)
                if d.split('_')[0].isdigit():
                    self.ID = int(d.split('_')[0])
                else:
                    self.ID = listdir(RootPath).index(d)
                return
            else:
                if isdir(join(RootPath,d)) and d.split('_')[0].isdigit():
                    CHList.append(d)
        print 'Can\'t find character %s' % self.name
        print 'Current Avalaible Character:'
        for ch in CHList:
            print ch
        raise Exception

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
            try:
                if exists(dirDict['..']):
                    for d in listdir(dirDict['..']):
                        if any([di in d.lower() for di in ['hair','clothes', 'pattern', 'zbr', 'uv']]):
                            fullPath = join(dirDict['..'], d)
                            if isdir(fullPath):
                                dirDict[d.lower()] = fullPath
                                if 'cloth' in d.lower():
                                    if isdir(join(fullPath,'rend')):
                                        dirDict['clothRender'] = join(fullPath,'rend')
                                if 'hair' in d.lower():
                                    if isdir(join(fullPath,'rend')):
                                        dirDict['hairRender'] = join(fullPath,'rend')
            except (IOError,OSError) as why:
                print why
        if version in self.version:
            self.version = version
            self.name = '_'.join([self.name, self.version])
            RootPath = join(self.path, self.name)
            self.path = {}
            if exists(RootPath):
                self.path['..'] = RootPath
                collectdir(self.path)
            RootTexPath = join(self.texPath, self.name)
            self.texPath = {}
            if exists(RootTexPath):
                self.texPath['..'] = RootTexPath
                collectdir(self.texPath)
