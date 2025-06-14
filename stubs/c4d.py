# Stub file for Cinema 4D API
STATUS_OK = 0
STATUS_NOTOK = 1

# UI flags
BFH_SCALEFIT = 0
BFV_SCALEFIT = 0
BFH_LEFT = 0
BFH_RIGHT = 0
BFH_CENTER = 0
BFV_MASK = 0
BFM_INPUT_KEYBOARD = 0

# Dialog types
DLG_TYPE_ASYNC = 0
DLG_TYPE_MODAL = 0

# Plugin flags
PLUGINFLAG_COMMAND = 0

# Script constants
PLUGIN_SCRIPT = 0

# Object types
Ocube = 5159
Osphere = 5160
Ocamera = 5103
Onull = 5140
Ospline = 5101
Osplinecircle = 5181

# Material related
Mmaterial = 5703
MATERIAL_COLOR_COLOR = 0
MATERIAL_SPECULAR_WIDTH = 0
MATERIAL_SPECULAR_HEIGHT = 0
MATERIAL_REFLECTION_LEVEL = 0

# Primitive settings
PRIM_CUBE_LEN = 0
PRIM_CUBE_WID = 0
PRIM_CUBE_HGT = 0
PRIM_SPHERE_RAD = 0
PRIM_CIRCLE_RADIUS = 0

# MoGraph constants
ID_MG_MOTIONGENERATOR_MODE = 0
MG_OBJECT_LINK = 0
MG_SPLINE_MODE = 0
MG_SPLINE_COUNT = 0
ID_MG_BASEEFFECTOR_POSITION_ACTIVE = 0
ID_MG_BASEEFFECTOR_POSITION = 0
VECTOR_X = 0
VECTOR_Y = 0
VECTOR_Z = 0

# Camera constants
CAMERA_FOCUS = 0
CAMERA_SHOW_COMPOSITION_THIRDS = 0

# Render settings
RDATA_XRES = 0
RDATA_YRES = 0
RDATA_FRAMERATE = 0
RDATA_GI_ENABLE = 0
RDATA_ANTIALIASING = 0
RDATA_FRAMEFROM = 0
RDATA_FRAMETO = 0

# Selection flags
GETACTIVEOBJECTFLAGS_CHILDREN = 0

class BaseObject:
    def __init__(self, type):
        pass
    
    def GetName(self):
        return ""
    
    def SetName(self, name):
        pass
    
    def GetUp(self):
        return None
    
    def GetDown(self):
        return None
    
    def GetNext(self):
        return None
    
    def GetClone(self):
        return BaseObject(0)
    
    def SetAbsPos(self, pos):
        pass
    
    def GetAbsPos(self):
        return Vector(0, 0, 0)
    
    def InsertUnder(self, parent):
        pass
    
    def Remove(self):
        pass
    
    def InsertMaterial(self, mat):
        pass
    
    def SetMl(self, mat):
        pass
    
    def SetRotation(self, rot):
        pass
    
    def IsInstanceOf(self, type):
        return False
    
    def CheckType(self, type):
        return False
    
    def __setitem__(self, key, value):
        pass
    
    def __getitem__(self, key):
        return 0

class BaseMaterial:
    def __init__(self, type):
        pass
    
    def GetName(self):
        return ""
    
    def SetName(self, name):
        pass
    
    def __setitem__(self, key, value):
        pass
    
    def __getitem__(self, key):
        return 0

class Vector:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

class BaseContainer:
    def SetString(self, id, value):
        pass
    
    def SetInt32(self, id, value):
        pass
    
    def SetBool(self, id, value):
        pass

def StatusSetText(text, type=0):
    pass

def CallCommand(id, bc=None):
    pass

def EventAdd():
    pass

def gui():
    class GUI:
        def MessageDialog(self, text):
            pass
        
        def QuestionDialog(self, text):
            return True
        
        def SetInputEnabled(self, enabled, flags=0):
            pass
    
    return GUI()

gui = gui()

def documents():
    class Documents:
        def GetActiveDocument(self):
            return BaseDocument()
    
    return Documents()

documents = documents()

def storage():
    class Storage:
        def ExecuteProgram(self, cmd):
            pass
    
    return Storage()

storage = storage()

def plugins():
    class Plugins:
        def RegisterCommandPlugin(self, id, name, flags, icon=None, description="", data=None):
            pass
        
        def SetWorldPluginData(self, pluginid, key, value):
            pass
        
        def GetWorldPluginData(self, pluginid, key, default=None):
            return default
    
    return Plugins()

plugins = plugins()

def utils():
    class Utils:
        def DegToRad(self, deg):
            return deg * 0.0174532925
    
    return Utils()

utils = utils()

class BaseDocument:
    def GetFirstObject(self):
        return None
    
    def InsertObject(self, obj):
        pass
    
    def InsertMaterial(self, mat):
        pass
    
    def InsertRenderData(self, rdata):
        pass
    
    def SetActiveObject(self, obj):
        pass
    
    def GetActiveObject(self):
        return None
    
    def GetActiveObjects(self, flags):
        return []
    
    def GetMaterials(self):
        return []
    
    def GetActiveRenderData(self):
        return BaseContainer()
    
    def SetActiveRenderData(self, rdata):
        pass
    
    def StartUndo(self):
        pass
    
    def EndUndo(self):
        pass