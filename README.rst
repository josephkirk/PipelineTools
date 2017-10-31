PipelineTools Module Repository
========================

Pipeline Tools is a collection of maya script and tool to help with Production of Jetstudio

+to run facial rig
import PipelineTools.main.rigging as rig
import PipelineTools.etc.facialTemp as ft
import pymel.core as pm
for mod in [ul,ui,rig,ft]:
    reload(mod)
curfile = pm.sceneName()
pm.openFile(curfile,f=True)
rig.create_facial_rig()