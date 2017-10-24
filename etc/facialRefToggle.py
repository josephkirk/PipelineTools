import pymel.core as pm
jobs = pm.scriptJob( listJobs=True )
for job in jobs:
    if 'CH_Ctrl_Reference.Facial_Ref' in job:
        pm.scriptJob(kill=int(job.split(':')[0]))
def toggleSecondaryRef():
    curscene = pm.workspace.path
    facialRig_file = curscene.__div__('scenes/Model/CH/01_KG/_temp/facialRig/NS57_KG_facialRig.mb') # path to character facialRig file
    rootCtrl = pm.PyNode('CH_Ctrl_Reference') # name of Root
    rootFacialAtr = rootCtrl.attr('Facial_Ref') # name of customAttribute
    if rootCtrl.Secondary_Ref.get() is True:
        pm.FileReference(facialRig_file).load()
    elif rootCtrl.Secondary_Ref.get() is False:
        pm.FileReference(facialRig_file).unload()
    pm.select(rootCtrl)
pm.scriptJob(attributeChange=['CH_Ctrl_Reference.Secondary_Ref', toggleFacialRef] )