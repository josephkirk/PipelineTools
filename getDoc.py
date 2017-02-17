import pymel.core as pm
sel= pm.selected()[0]
#for i in dir(sel):
#    print i
for i in dir(sel.getMatrix()):
    try:
        print i+"\n\n",eval("sel.getMatrix().%s.__doc__" % i)
    except:
        continue