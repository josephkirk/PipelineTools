#VBSCript
import win32com.client
psApp = win32com.client.Dispatch("Photoshop.Application")
newPsd = "NewPsdFile"
docRef= psApp.Application.Documents.Add(1024,1024)
docRefLayers = docRef.artLayers
newLayer = docRefLayers.Add()
newLayer.name = "NewLayer%s" % 1
docRef.ActiveLayer = newLayer
newLayer.Kind = 16
#layerKind = 
# for i in range(1,100):
#     newLayer = docRefLayers.Add()
#     newLayer.name = "NewLayer%s" % i
#     docRef.ActiveLayer = newLayer
#     try:
#         docRef.ActiveLayer.kind = i
#     except:
#         continue
# activeLayer = docRef.ActiveLayer
#layerKind = win32com.client.Dispatch("Photoshop.LayerKind")

# docRef.Selection.SelectAll()
# solidColorRef = win32com.client.Dispatch("Photoshop.SolidColor")
# solidColorRef.RGB.Red = 255
# solidColorRef.RGB.Green = 0
# solidColorRef.RGB.Blue = 0
# docRef.Selection.Fill(solidColorRef)
# docRefLayerGroups = docRef.LayerSets
# docRefLayerGroups.Add()
# layerRef = docRefLayerGroups(1).Duplicate(docRefLayers, 2)
# # Save Psd
# psdSaveOptions = win32com.client.Dispatch("Photoshop.PhotoshopSaveOptions")
# psApp.Application.ActiveDocument.SaveAs("F:\\psd\%s.psd" % newPsd, psdSaveOptions, False, 2)
# psApp.Application.ActiveDocument.Selection.Fill(255,5,5)
