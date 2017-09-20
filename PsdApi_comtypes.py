from comtypes.client import CreateObject
import os
currentPath = os.getcwd()
"""
written by Nguyen Phi Hung 2017
email: josephkirk.art@gmail.com
All code written by me unless specify
"""
#### init 
def CreatePSDApp():
    dispatchCom = CreateObject("Photoshop.Application.11")
    return dispatchCom
psApp = CreatePSDApp()

### Function
def runJSX (aFilePath ):
    '''run javascript'''
    id60 = psApp.stringIDToTypeID ( "AdobeScriptAutomation Scripts" )
    desc12 = CreateObject('Photoshop.ActionDescriptor')
    id61 = psApp.charIDToTypeID( "jsCt" )
    desc12.putPath( id61, aFilePath )
    id62 = psApp.charIDToTypeID( "jsMs" )
    desc12.putString( id62, "null" )
    psApp.executeAction( id60, desc12, 2 )

def createEmptyLayer(name):
    newLayer = psApp.activeDocument.artLayers.add()
    newLayer.name = name
    return newLayer

def createTextLayer(name):
    newLayer = psApp.activeDocument.artLayers.add()
    newLayer.name = name
    newLayer.kind = 2
    return newLayer

def createSolidFillLayer(R, G, B):
    '''create Solid Color Layer'''
    id117 = psApp.charIDToTypeID( "Mk  " )
    desc25 = CreateObject('Photoshop.ActionDescriptor')
    id118 = psApp.charIDToTypeID( "null" )
    ref13 = CreateObject('Photoshop.ActionReference')
    id119 = psApp.stringIDToTypeID( "contentLayer" )
    ref13.putClass( id119 )
    desc25.putReference( id118, ref13 )
    id120 = psApp.charIDToTypeID( "Usng" )
    desc26 = CreateObject('Photoshop.ActionDescriptor')
    id121 = psApp.charIDToTypeID( "Type" )
    desc27 = CreateObject('Photoshop.ActionDescriptor')
    id122 = psApp.charIDToTypeID( "Clr " )
    desc28 = CreateObject('Photoshop.ActionDescriptor')
    id123 = psApp.charIDToTypeID( "Rd  " )
    desc28.putDouble( id123, R )
    id124 = psApp.charIDToTypeID( "Grn " )
    desc28.putDouble( id124, G )
    id125 = psApp.charIDToTypeID( "Bl  " )
    desc28.putDouble( id125, B )
    id126 = psApp.charIDToTypeID( "RGBC" )
    desc27.putObject( id122, id126, desc28 )
    id127 = psApp.stringIDToTypeID( "solidColorLayer" )
    desc26.putObject( id121, id127, desc27 )
    id128 = psApp.stringIDToTypeID( "contentLayer" )
    desc25.putObject( id120, id128, desc26 )
    psApp.executeAction( id117, desc25, 2 )
    newLayer = psApp.activeDocument.activeLayer
    newLayer.name = name
    return newLayer

def createLevelLayer(name):
    idMk = psApp.CharIDToTypeID( "Mk  " )
    desc4 = CreateObject( "Photoshop.ActionDescriptor" )
    idnull = psApp.CharIDToTypeID( "null" )
    ref1 = CreateObject( "Photoshop.ActionReference" )
    idAdjL = psApp.CharIDToTypeID( "AdjL" )
    ref1.PutClass( idAdjL )
    desc4.PutReference( idnull, ref1)
    idUsng = psApp.CharIDToTypeID( "Usng" )
    desc5 = CreateObject( "Photoshop.ActionDescriptor" )
    idType = psApp.CharIDToTypeID( "Type" )
    desc6 = CreateObject( "Photoshop.ActionDescriptor" )
    idpresetKind = psApp.StringIDToTypeID( "presetKind" )
    idpresetKindType = psApp.StringIDToTypeID( "presetKindType" )
    idpresetKindDefault = psApp.StringIDToTypeID( "presetKindDefault" )
    desc6.PutEnumerated( idpresetKind, idpresetKindType, idpresetKindDefault )
    idLvls = psApp.CharIDToTypeID( "Lvls" )
    desc5.PutObject( idType, idLvls, desc6 )
    idAdjL = psApp.CharIDToTypeID( "AdjL" )
    desc4.PutObject( idUsng, idAdjL, desc5 )
    psApp.ExecuteAction( idMk, desc4, 2 )
    newLayer = psApp.activeDocument.activeLayer
    newLayer.name = name
    return newLayer

def createColorCorrectLayer(name):
    idMk = psApp.CharIDToTypeID( "Mk  " )
    desc8 = CreateObject( "Photoshop.ActionDescriptor" )
    idnull = psApp.CharIDToTypeID( "null" )
    ref3 = CreateObject( "Photoshop.ActionReference" )
    idAdjL = psApp.CharIDToTypeID( "AdjL" )
    ref3.PutClass( idAdjL )
    desc8.PutReference( idnull, ref3 )
    idUsng = psApp.CharIDToTypeID( "Usng" )
    desc9 = CreateObject( "Photoshop.ActionDescriptor" )
    idType = psApp.CharIDToTypeID( "Type" )
    desc10 = CreateObject( "Photoshop.ActionDescriptor" )
    idpresetKind = psApp.StringIDToTypeID( "presetKind" )
    idpresetKindType = psApp.StringIDToTypeID( "presetKindType" )
    idpresetKindDefault = psApp.StringIDToTypeID( "presetKindDefault" )
    desc10.PutEnumerated( idpresetKind, idpresetKindType, idpresetKindDefault )
    idClrz = psApp.CharIDToTypeID( "Clrz" )
    desc10.PutBoolean( idClrz, False )
    idHStr = psApp.CharIDToTypeID( "HStr" )
    desc9.PutObject( idType, idHStr, desc10 )
    idAdjL = psApp.CharIDToTypeID( "AdjL" )
    desc8.PutObject( idUsng, idAdjL, desc9 )
    psApp.ExecuteAction( idMk, desc8, dialogMode )
    newLayer = psApp.activeDocument.activeLayer
    newLayer.name = name
    return newLayer

def createLayer(name, type, blendMode, opacity):
    typeDict = {
        "empty": createEmptyLayer(name),
        "text": createTextLayer(name),
        "fill": createSolidFillLayer(name),
        "level": createLevelLayer(name)
    }
    if typeDict.has_key(type):
        newLayer = typeDict[type]
        newLayer.blendMode = blendMode
        newLayer.opacity = opacity
        return newLayer

################### Main Class
class Document(object):
    def __init__(self)
        self = psApp.documents
class Layer(object):
    """Photoshop Layer Class"""
    def __init__(self, name, layerType, blendMode=2, opacity=100):
        self.name = name
        self.type = layerType
        self.blendMode = blendMode
        self.opacity = opacity
        createLayer(name, layerType, blendMode, opacity)

#jsxFile = r'%s\\%s' % (currentPath,'PsdjsxHelper.jsx')
#print jsxFile
#runJSX(jsxFile)