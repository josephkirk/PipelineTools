import pymel.core as pm
try:
    pm.delete('facialRigScript')
except:
    pass
connectBSCommand='''
import pymel.core as pm
try:
    if not pm.ls('RootBS') and not pm.ls('EyeDeformBS'):
        pm.select('facial',r=True)
        pm.select("*_face_grp_skinDeform",add=True)
        pm.blendShape(name='RootBS',w=[(0,1),], automatic=True)
        pm.select('eyeDeform',r=True)
        pm.select("*_eye_grp_skinDeform",add=True)
        pm.blendShape(name='EyeDeformBS',w=[(0,1),], ar=True)
except:
    print 'Cant connect BS'
'''
unConnectBSCommand='''
try:
    pm.delete('RootBS')
    pm.delete('EyeDeformBS')
except:
    'cant delete RootBS and EyeDeformBS'
'''
initNode = pm.scriptNode(name='facialRigScript', st=2, bs=connectBSCommand, n='script', stp='python')
pm.scriptNode(initNode, e=True, afterScript=unConnectBSCommand, stp='python' )
