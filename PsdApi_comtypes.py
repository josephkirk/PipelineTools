from comtypes.client import CreateObject
import os
currentPath = os.getcwd()
psApp = CreatePSDApp()
def CreatePSDApp():
    dispatchCom = CreateObject("Photoshop.Application.11")
    return dispatchCom
def runJSX (aFilePath ):
    '''run javascript'''
    id60 = psApp.stringIDToTypeID ( "AdobeScriptAutomation Scripts" )
    desc12 = CreateObject('Photoshop.ActionDescriptor')
    id61 = psApp.charIDToTypeID( "jsCt" )
    desc12.putPath( id61, aFilePath )
    id62 = psApp.charIDToTypeID( "jsMs" )
    desc12.putString( id62, "null" )
    psApp.executeAction( id60, desc12, 2 )

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

fillSolidColour(255,0,0)
#jsxFile = r'%s\\%s' % (currentPath,'PsdjsxHelper.jsx')
#print jsxFile
#runJSX(jsxFile)