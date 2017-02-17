import pymel.core as pm
import itertools
sel = pm.selected()
if len(sel)>3:
    posList = [o.translate.get() for o in sel]
    pm.curve(p=posList)