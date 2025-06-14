import c4d
import os
import json
import sys

# Get the plugin directory
plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if plugin_dir not in sys.path:
    sys.path.append(plugin_dir)

# Now import from config
from config import PLUGIN_ID

# Create a simpler way to create IDs from strings that won't overflow
def generate_id(key):
    """Generate a smaller int ID from a string key"""
    # Just use a simple sum of character codes modulo 10000
    # This limits the range but prevents overflow
    id_num = 0
    for char in key:
        id_num += ord(char)
    return (id_num % 10000) + 1000  # Keep between 1000-11000 range

def save_pref(key, value):
    """Save a preference value using the plugin storage mechanism"""
    # C4D API may have changed - we need to use a different approach
    # First check if the storage container already exists
    bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)
    
    if bc is None:
        # Create a new container if none exists
        bc = c4d.BaseContainer()
    
    # Use our simplified ID generation
    key_id = generate_id(key)
    
    # Store our value in the container
    if isinstance(value, str):
        bc.SetString(key_id, value)
    elif isinstance(value, bool):
        bc.SetBool(key_id, value)
    elif isinstance(value, int):
        bc.SetInt32(key_id, value)
    elif isinstance(value, float):
        bc.SetFloat(key_id, value)
    else:
        # Convert complex types to JSON
        try:
            bc.SetString(key_id, json.dumps(value))
        except:
            return False
    
    # Save the container back to the plugin data
    return c4d.plugins.SetWorldPluginData(PLUGIN_ID, bc)

def load_pref(key, default=None):
    """Load a preference value from the plugin storage mechanism"""
    # Get the container
    bc = c4d.plugins.GetWorldPluginData(PLUGIN_ID)
    
    if bc is None:
        return default
    
    # Use our simplified ID generation
    key_id = generate_id(key)
    
    # Try to retrieve the value based on its expected type
    if default is None:
        # Try string first
        value = bc.GetString(key_id)
        if value:
            return value
        return default
    
    if isinstance(default, str):
        return bc.GetString(key_id, default)
    elif isinstance(default, bool):
        return bc.GetBool(key_id, default)
    elif isinstance(default, int):
        return bc.GetInt32(key_id, default)
    elif isinstance(default, float):
        return bc.GetFloat(key_id, default)
    else:
        # Try to parse complex types from JSON
        try:
            value = bc.GetString(key_id)
            if value:
                return json.loads(value)
        except:
            pass
    
    return default