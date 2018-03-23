import ui
import SkinSetterUI
import RebuildBSUI
import RenamerUI
import ControlsMakerUI
def _reload():
    for mod in [
        ui,
        SkinSetterUI,
        RebuildBSUI,
        RenamerUI,
        ControlsMakerUI]:
        reload(mod)