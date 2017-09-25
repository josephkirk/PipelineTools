# -*- coding: utf-8 -*-
# --------------------------------------
# �I����W���C���g�̈ʒu�Ƀ��P�[�^�ƃR���g���[����쐬
# --------------------------------------

import pymel.core as pm

name = pm.ls(sl=True)
for n in name:
    locname = n.replace('_bon','_loc')
    loc = pm.spaceLocator(p=(0,0,0), n=locname)
    pc = pm.pointConstraint(n, loc, o=(0,0,0), w=1)
    pm.delete(pc[0])
for n in name:
    ctlname = n.replace('_bon','_ctl')
    sph = pm.sphere(p=(0,0,0), ax=(0,1,0), ssw=0, esw=360, r=0.35, d=3, ut=False, tol=0.01, s=8, nsp=4, ch=False, n=ctlname)
    pc = pm.pointConstraint(n, sph, o=(0,0,0), w=1)
    pm.delete(pc[0])