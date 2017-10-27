from PipelineTools.packages import metadata
import maya.cmds as cmds
import os
#print os.getpid()
import pymel.core as pm
class FacialRig(metadata.MetaRig):
    '''
    Example custom mRig class inheriting from MetaRig
    '''
    def __init__(self,*args,**kws):
        super(FacialRig, self).__init__(*args,**kws) 
        self.lockState=False
        
    def __bindData__(self):
        '''
        bind our default attrs to this node
        '''
        self.addAttr('RigType','FacialRig', l=True)
        self.addAttr('CharacterName','')
        self.addAttr('BuildBy','{} {}'.format(os.environ.get('COMPUTERNAME'), os.environ.get('USERNAME')), l=True)
        self.addAttr('Branch',os.environ.get('USERDOMAIN'), l=True)
        self.addAttr('BuildDate',pm.date(), l=True)
        #self.addAttr('Models','-'*50, l=True)
        self.addAttr('FaceGp','')
        self.addAttr('EyeGp','')
        self.addAttr('FaceDeformGp','')
        self.addAttr('FacialTargetPath','')
        #self.addAttr('Bones','-'*100, l=True)
        self.addAttr('HeadBone', 'CH_Head')
        self.addAttr('FacialBoneGp','')
        self.addAttr('EyeBoneGp','')
        self.addAttr('BlendshapeCtl','')
        self.addAttr('FacialCtl','')
        self.addAttr('EyeCtl','')
        self.addAttr('TongueCtl','')
        self.addAttr('JawCtl','')
#r9Meta.registerMClassInheritanceMapping()
if __name__ == 'main':
    try:
        networks = pm.ls(type=pm.nt.Network)
        networks.extend(pm.selected())
        for networknode in networks: 
            pm.lockNode(networknode, lock=False)
            pm.delete(networknode)
    except:
        pass
    myRigmetaGp = pm.nt.Transform(name='facialGP')
    myRigmeta = FacialRig(myRigmetaGp.name())
    myRigmeta.CharacterName='KG'
    #myRigmeta.addRigCtrl(pm.selected()[0],'new')
    #pm.select(myRigmeta)
    print myRigmeta
    #pm.delete(myRigmeta)