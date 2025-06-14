import c4d
from math import sin, cos, pi
from ..logging import log_line

def add_spline(doc, type="circle", radius=100, width=200, height=200, 
               points=None, position=None, plane="XZ", name=None, **kwargs):
    """
    Add a spline to the scene
    
    Args:
        type: Type of spline (circle, rectangle, line, custom)
        radius: Radius for circle splines
        width/height: Dimensions for rectangle splines
        points: List of points for custom splines
        position: Position of the spline
        plane: Orientation plane (XY, XZ, YZ)
        name: Name of the spline object
    """
    spline = None
    
    # Create different spline types
    if type.lower() in ["circle", "circular"]:
        spline = c4d.BaseObject(c4d.Osplinecircle)
        spline[c4d.PRIM_CIRCLE_RADIUS] = radius
        log_line("info", f"Created circle spline with radius {radius}")
        
    elif type.lower() in ["rectangle", "rect", "square"]:
        spline = c4d.BaseObject(c4d.Osplineprimitiveobject)
        spline[c4d.PRIM_PLANE_SUBTYPE] = 0  # Rectangle
        spline[c4d.PRIM_PLANE_WIDTH] = width
        spline[c4d.PRIM_PLANE_HEIGHT] = height
        log_line("info", f"Created rectangle spline with width {width} and height {height}")
        
    elif type.lower() in ["line", "linear"]:
        if points and len(points) >= 2:
            spline = create_linear_spline(points)
            log_line("info", f"Created line spline with {len(points)} points")
        else:
            # Default line if no points provided
            spline = c4d.BaseObject(c4d.Osplineprimitiveobject)
            spline[c4d.PRIM_PLANE_SUBTYPE] = 2  # Line
            spline[c4d.PRIM_PLANE_WIDTH] = width
            log_line("info", f"Created line spline with width {width}")
            
    elif type.lower() in ["custom", "freeform"]:
        if points and len(points) >= 2:
            spline = create_linear_spline(points)
            log_line("info", f"Created custom spline with {len(points)} points")
        else:
            log_line("error", "Cannot create custom spline without points")
            return None
    
    if spline is None:
        log_line("error", f"Unsupported spline type: {type}")
        return None
    
    # Set plane orientation
    if plane.upper() == "XY":
        # Default orientation
        pass
    elif plane.upper() == "XZ":
        spline.SetRotation(c4d.Vector(c4d.utils.DegToRad(90), 0, 0))
    elif plane.upper() == "YZ":
        spline.SetRotation(c4d.Vector(0, c4d.utils.DegToRad(90), 0))
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            spline.SetAbsPos(c4d.Vector(*position))
    
    # Set name
    if name is not None:
        spline.SetName(name)
    
    # Add to document
    doc.InsertObject(spline)
    
    return spline

def create_linear_spline(points):
    """Create a linear spline from a list of points"""
    spline = c4d.SplineObject(len(points), c4d.SPLINETYPE_LINEAR)
    
    for i, point in enumerate(points):
        if isinstance(point, list) and len(point) >= 2:
            # Use z=0 if only x,y provided
            z = point[2] if len(point) > 2 else 0
            spline.SetPoint(i, c4d.Vector(point[0], point[1], z))
        elif isinstance(point, c4d.Vector):
            spline.SetPoint(i, point)
    
    # Update spline
    spline.Message(c4d.MSG_UPDATE)
    return spline

def create_bezier_spline(points, handles_in=None, handles_out=None):
    """Create a bezier spline with control points"""
    if not points or len(points) < 2:
        return None
    
    spline = c4d.SplineObject(len(points), c4d.SPLINETYPE_BEZIER)
    
    for i, point in enumerate(points):
        if isinstance(point, list) and len(point) >= 2:
            z = point[2] if len(point) > 2 else 0
            spline.SetPoint(i, c4d.Vector(point[0], point[1], z))
        elif isinstance(point, c4d.Vector):
            spline.SetPoint(i, point)
        
        # Set control handles if provided
        if handles_in and i < len(handles_in):
            if isinstance(handles_in[i], list) and len(handles_in[i]) >= 2:
                z = handles_in[i][2] if len(handles_in[i]) > 2 else 0
                spline.SetTangent(i, c4d.Vector(handles_in[i][0], handles_in[i][1], z), True)
            elif isinstance(handles_in[i], c4d.Vector):
                spline.SetTangent(i, handles_in[i], True)
                
        if handles_out and i < len(handles_out):
            if isinstance(handles_out[i], list) and len(handles_out[i]) >= 2:
                z = handles_out[i][2] if len(handles_out[i]) > 2 else 0
                spline.SetTangent(i, c4d.Vector(handles_out[i][0], handles_out[i][1], z), False)
            elif isinstance(handles_out[i], c4d.Vector):
                spline.SetTangent(i, handles_out[i], False)
    
    # Update spline
    spline.Message(c4d.MSG_UPDATE)
    return spline

def clone_along_spline(doc, source=None, source_name=None, spline=None, spline_name=None, 
                       count=10, mode="equal", name=None, **kwargs):
    """
    Clone objects along a spline
    
    Args:
        source: Source object to clone
        source_name: Name of source object (alternative to source)
        spline: Spline to clone along
        spline_name: Name of spline (alternative to spline)
        count: Number of clones
        mode: Distribution mode (equal, step)
        name: Name for the cloner object
    """
    # Find source object
    src_obj = None
    if source is not None and isinstance(source, c4d.BaseObject):
        src_obj = source
    elif source_name is not None:
        src_obj = find_object_by_name(doc.GetFirstObject(), source_name)
    
    if src_obj is None:
        log_line("error", f"Source object not found: {source_name}")
        return False
    
    # Find spline
    spline_obj = None
    if spline is not None and isinstance(spline, c4d.BaseObject):
        spline_obj = spline
    elif spline_name is not None:
        spline_obj = find_object_by_name(doc.GetFirstObject(), spline_name)
    else:
        # Look for latest spline if none specified
        all_objects = []
        obj = doc.GetFirstObject()
        while obj:
            all_objects.append(obj)
            obj = obj.GetNext()
        
        # Look for splines in reverse order (most recently added first)
        for obj in reversed(all_objects):
            if obj.IsInstanceOf(c4d.Ospline):
                spline_obj = obj
                break
    
    if spline_obj is None:
        log_line("error", "No spline found for cloning")
        return False
    
    # Create cloner object
    cloner = c4d.BaseObject(1018544)  # MoGraph Cloner ID
    
    # Set name
    if name is not None:
        cloner.SetName(name)
    else:
        cloner.SetName(f"Cloner_{src_obj.GetName()}")
    
    # Set cloner properties
    cloner[c4d.ID_MG_MOTIONGENERATOR_MODE] = 2  # Object mode
    cloner[c4d.MG_OBJECT_LINK] = spline_obj
    
    # Set distribution mode
    if mode.lower() == "equal":
        cloner[c4d.MG_SPLINE_MODE] = 0  # Equal
    elif mode.lower() == "step":
        cloner[c4d.MG_SPLINE_MODE] = 1  # Fixed Step
    
    # Set count
    cloner[c4d.MG_SPLINE_COUNT] = count
    
    # Add source as child of cloner
    src_copy = src_obj.GetClone()
    src_copy.InsertUnder(cloner)
    
    # Add cloner to document
    doc.InsertObject(cloner)
    log_line("info", f"Created cloner with {count} instances of '{src_obj.GetName()}' along '{spline_obj.GetName()}'")
    
    return cloner

def find_object_by_name(start_obj, name):
    """Find an object by name in the hierarchy"""
    if start_obj is None:
        return None
    
    if start_obj.GetName() == name:
        return start_obj
    
    # Check children
    child = start_obj.GetDown()
    if child:
        found = find_object_by_name(child, name)
        if found:
            return found
    
    # Check next
    next_obj = start_obj.GetNext()
    if next_obj:
        return find_object_by_name(next_obj, name)
    
    return None