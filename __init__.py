import os
import site
import core
import etc
import main
import project_specific
basePath = os.path.dirname(__file__)
# installPackages = []
# installPackages.append('packages')
# for package in installPackages:
#     installpath = os.path.join(basePath, package)
#     if os.path.isdir(installpath):
#         site.addsitedir(installpath)
#     else:
#         print installpath, 'does not exists'
# print 'third Party packages iniliazize'
def _reload():
    for mod in [core,etc,main,project_specific]:
        reload(mod)
        if hasattr(mod,'_reload'):
            mod._reload()
        # print mod.__name__, 'reload'