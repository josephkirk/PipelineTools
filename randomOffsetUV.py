import pymel.core as pm
import random as rand
offset=0.1
sel=pm.selected()
for o in sel:
    uvCount=pm.polyEvaluate(o,uv=True)
    pm.select(o+".map[0:%s]" % uvCount,r=1)
    pm.polyEditUV(u=rand.uniform(-offset,offset))
pm.select(sel)