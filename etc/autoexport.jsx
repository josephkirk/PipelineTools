// var originalUnit = preferences.rulerUnits
// preferences.rulerUnits = Units.PIXELS

var docRef = app.activeDocument
var layerSetsRef = docRef.layerSets

var newFileRef
jpgSaveOptions = new JPEGSaveOptions()
jpgSaveOptions.embedColorProfile = true
jpgSaveOptions.formatOptions = FormatOptions.STANDARDBASELINE
jpgSaveOptions.matte = MatteType.NONE
jpgSaveOptions.quality = 10
try {
    docRef.artLayers.getByName("UV").visible = false
} 
catch(err) {}
for(i=0; i < layerSetsRef.length; i++) {
    if (layerSetsRef[i].name != "dif") {
        layerSetsRef[i].visible = false
    } else {
        layerSetsRef[i].visible = true
    }
}

for(i=0; i < layerSetsRef.length; i++) {
    if (layerSetsRef[i].layerSets.length!=0 || layerSetsRef[i].artLayers.length!=0) {
        layerSetsRef[i].visible = true
        newFileRef = docRef.path.toString().replace("psd","") +
                    docRef.name.replace(".psd","") +
                    "_".concat(layerSetsRef[i].name) +
                    ".jpeg"
        jpgFile = new File(newFileRef)
        docRef.saveAs(jpgFile, jpgSaveOptions, true,
        Extension.LOWERCASE)
        if (layerSetsRef[i].name != "dif") {
            layerSetsRef[i].visible = false
        } else {
            layerSetsRef[i].visible = true
        }
    }
}
try {
    docRef.artLayers.getByName("UV").visible = true
} 
catch(err) {}
// artLayerRef.kind = LayerKind.TEXT
// var textItemRef = artLayerRef.textItem
// textItemRef.contents = docRef.path.toString()


newFileRef = null
docRef = null
layerSetsRef = null
// artLayerRef = null
// textItemRef = null

// app.preferences.rulerUnits = originalUnit