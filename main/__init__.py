import ui
import SkinSetterUI
import RebuildBSUI
import RenamerUI
def _reload():
    for mod in [
        ui,
        SkinSetterUI,
        RebuildBSUI,
        RenamerUI]:
        reload(mod)