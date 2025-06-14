import os
import sys
import json

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__)))

# Mock c4d module
class MockC4D:
    class BaseObject:
        def __init__(self, type_id):
            self.type_id = type_id
            self.name = ""
            self.children = []
            self.params = {}  # Add this to store parameters
            
        def SetName(self, name):
            self.name = name
            return self
            
        def GetName(self):
            return self.name
        
        # Add these methods to support item assignment
        def __setitem__(self, key, value):
            self.params[key] = value
            print(f"SET: {self.name} parameter {key} = {value}")
            
        def __getitem__(self, key):
            return self.params.get(key)
            
    class Vector:
        def __init__(self, x=0, y=0, z=0):
            self.x = x
            self.y = y
            self.z = z
            
    class BaseMaterial:
        def __init__(self, type_id):
            self.type_id = type_id
            self.name = ""
            self.props = {}
            
        def SetName(self, name):
            self.name = name
            print(f"SET MATERIAL: Name = {name}")
            return self
            
        # Add these methods to support material properties
        def __setitem__(self, key, value):
            self.props[key] = value
            print(f"SET MATERIAL: {self.name} property {key} = {value}")
            
        def __getitem__(self, key):
            return self.props.get(key)
            
        # Add a method to set a shader
        def SetShader(self, channel, shader):
            print(f"SET MATERIAL: {self.name} channel {channel} shader = {shader.__class__.__name__}")
            self.props[channel] = shader
            return True
            
    class BaseContainer:
        def __init__(self):
            self.data = {}
            
        def SetString(self, id, value):
            self.data[id] = value
            
        def SetInt32(self, id, value):
            self.data[id] = value
            
        def SetBool(self, id, value):
            self.data[id] = value
            
        def GetString(self, id, default=None):
            return self.data.get(id, default)
            
        def GetInt32(self, id, default=0):
            return self.data.get(id, default)
            
        def GetBool(self, id, default=False):
            return self.data.get(id, default)
            
    class plugins:
        @staticmethod
        def GetWorldPluginData(plugin_id):
            return MockC4D.BaseContainer()
            
        @staticmethod
        def SetWorldPluginData(plugin_id, container):
            return True
            
    class gui:
        @staticmethod
        def MessageDialog(message):
            print(f"MESSAGE: {message}")
            
    class documents:
        @staticmethod
        def GetActiveDocument():
            return MockDocument()
            
    @staticmethod
    def StatusSetText(text):
        print(f"STATUS: {text}")
        
    @staticmethod
    def EventAdd():
        print("EVENT: Document updated")
        
    # Define some constants to match Cinema 4D's
    Ocube = 1001
    Osphere = 1002
    Ocamera = 1003
    Onull = 1005
    Ospline = 1006
    Osplinecircle = 1008
    
    # Material types
    Mmaterial = 5000  # Add this standard material type
    
    PRIM_CUBE_LEN = 2000
    PRIM_CUBE_WID = 2001
    PRIM_CUBE_HGT = 2002
    
    PRIM_SPHERE_RAD = 2100
    
    MATERIAL_COLOR_COLOR = 3000
    # Add appropriate color channel constants
    MATERIAL_COLOR_SHADER = 3001
    MATERIAL_LUMINANCE_COLOR = 3002
    MATERIAL_TRANSPARENCY_COLOR = 3003
    MATERIAL_REFLECTION_COLOR = 3004

class MockDocument:
    def __init__(self):
        self.objects = []
        self.materials = []
        
    def InsertObject(self, obj):
        self.objects.append(obj)
        return True
        
    def InsertMaterial(self, mat):
        self.materials.append(mat)
        return True
        
    def GetFirstObject(self):
        return self.objects[0] if self.objects else None
        
    def GetMaterials(self):
        return self.materials
        
    def StartUndo(self):
        print("UNDO: Starting undo block")
        
    def EndUndo(self):
        print("UNDO: Ending undo block")
        
    def SetActiveObject(self, obj):
        print(f"SELECT: {obj.GetName()}")
        return True
        
    def GetActiveObject(self):
        return self.objects[0] if self.objects else None

# Replace the real c4d module with our mock
sys.modules['c4d'] = MockC4D()

# Now we can import our modules
from src.agent import Agent
from src.mcp_executor import execute_commands, MCPExecutor

# Test function
def test_agent_rules():
    print("=== Testing Agent Rules Processing ===")
    agent = Agent()
    agent.load_rules()
    
    # Test rule matching
    test_prompts = [
        "Add a cube that is 200cm on each side",
        "I want to duplicate it four more times",
        "Create a red glossy material named RedMaterial",
        "This shouldn't match any rules"
    ]
    
    for prompt in test_prompts:
        print(f"\nTesting prompt: '{prompt}'")
        commands = agent.match_prompt(prompt)
        if commands:
            print(f"  ✓ Matched rule with {len(commands)} commands")
            print(f"  Commands: {json.dumps(commands, indent=2)}")
        else:
            print(f"  ✗ No match found")
            
    return agent

def test_command_execution():
    print("\n=== Testing Command Execution ===")
    # Create an MCPExecutor instance
    mcp = MCPExecutor()
    
    # Test executing some basic commands
    commands = [
        {"action": "AddCube", "args": {"size": 200, "name": "TestCube"}},
        {"action": "CreateMaterial", "args": {"name": "RedMaterial", "color": [1, 0, 0]}}
    ]
    
    # Execute the commands
    print(f"Executing {len(commands)} test commands:")
    for cmd in commands:
        print(f"  - {cmd['action']}: {cmd['args']}")
        
    execute_commands(commands)
    
    return mcp

if __name__ == "__main__":
    agent = test_agent_rules()
    mcp = test_command_execution()
    
    print("\nAll tests complete!")