import PipelineTools.core as ptc
import controlShape as cs
import pymel.core as pm
reload(cs)
ptc._reload()

####
@ptc.gu.do_function_on()
def createFreeJointControl(bone):
    bonepos = bone.getTranslation('world')
    bonGp = pm.nt.Transform(name=bone.name()+'Gp')
    bonGp.setTranslation(bonepos, 'world')
    pm.makeIdentity(bonGp, apply=True)
    bone.setParent(bonGp)
    ctl = cs.createSphereCtl(name=bone.name().replace('bon', 'ctl'))
    ctlGp = pm.nt.Transform(name=ctl.name()+'Gp')
    ctl.setParent(ctlGp)
    ctlGp.setTranslation(bonepos, 'world')
    pm.makeIdentity(ctlGp, apply=True)
    for atr in ['tx','ty','tz','rx','ry','rz','sx','sy','sz']:
        ctl.attr(atr) >> bonGp.attr(atr)
@ptc.gu.do_function_on()
def createParentJointControl(bone, offsetRotate=[0,0,0]):
    bonematrix = bone.getMatrix(worldSpace=True)
    name = bone.name().split('|')[-1].split('_')[0]
    ctl = cs.createPinCtl(name=name+'_ctl')
    ctlGp = pm.nt.Transform(name=name+'_ctlGp')
    ctl.setParent(ctlGp)
    ctlGp.setMatrix(bonematrix,worldSpace=True)
    ctl.rotate.set(offsetRotate)
    pm.makeIdentity(ctl,apply=True)
    for atr in ['translate', 'rotate', 'scale']:
        ctl.attr(atr) >> bone.attr(atr)