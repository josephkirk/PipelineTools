import win32com.client
psApp = win32com.client.Dispatch("Photoshop.Application")
psApp.Application.Documents.add(1024,1024)
doc = psApp.Application.ActiveDocument
doc.ArtLayers.art()