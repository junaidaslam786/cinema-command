# cinecommand.pyp
import c4d
from c4d import plugins
import os
import sys

# Add the plugin directory to Python path
__file__ = os.path.realpath(__file__)
plugin_dir = os.path.dirname(__file__)
if plugin_dir not in sys.path:
    sys.path.append(plugin_dir)

# Add vendor directory for third-party packages
vendor_dir = os.path.join(plugin_dir, 'vendor')
if os.path.exists(vendor_dir) and vendor_dir not in sys.path:
    sys.path.append(vendor_dir)

# Now we can import from src
from src.main_dialog import MainDialog
from src.settings_dialog import SettingsDialog
from config import PLUGIN_ID, PLUGIN_NAME, PLUGIN_VERSION

class CineCommand(plugins.CommandData):
    """Main CineCommand plugin class"""
    dlg = None

    def Execute(self, doc):
        """Execute the plugin - open the dialog"""
        if self.dlg is None:
            self.dlg = MainDialog()
        # Opens non-modal so users can dock/panels
        return self.dlg.Open(c4d.DLG_TYPE_ASYNC, PLUGIN_ID, -2, -2, 400, 200)

    # allow the Settings command to show prefs
    def RestoreLayout(self, secret): 
        return True

# Create a separate CommandData class for settings
class CineCommandSettings(plugins.CommandData):
    """Settings dialog for CineCommand"""
    
    def Execute(self, doc):
        """Execute the plugin - open settings dialog"""
        dlg = SettingsDialog()
        return dlg.Open(c4d.DLG_TYPE_MODAL, PLUGIN_ID+1)
    
    def RestoreLayout(self, secret):
        return True

if __name__ == "__main__":
    # Register the main command
    plugins.RegisterCommandPlugin(
        PLUGIN_ID,
        PLUGIN_NAME,
        0,
        None,
        "AI-powered prompt execution",
        CineCommand()
    )
    
    # Also register the Settings command
    plugins.RegisterCommandPlugin(
        PLUGIN_ID+1,
        f"{PLUGIN_NAME} Settings",
        0,
        None,
        f"Open {PLUGIN_NAME} Preferences",
        CineCommandSettings()  # Use the class instance instead of lambda
    )