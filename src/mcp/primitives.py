import c4d
from ..logging import log_line

def add_cube(doc, size=100, position=None, name=None, **kwargs):
    """Add a cube to the scene"""
    cube = c4d.BaseObject(c4d.Ocube)
    
    # Set size
    cube[c4d.PRIM_CUBE_LEN] = size
    cube[c4d.PRIM_CUBE_WID] = size
    cube[c4d.PRIM_CUBE_HGT] = size
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            cube.SetAbsPos(c4d.Vector(*position))
    
    # Set name
    if name is not None:
        cube.SetName(name)
    
    # Add to document
    doc.InsertObject(cube)
    log_line("info", f"Added cube: {name if name else 'Unnamed'}, size: {size}")
    
    return cube

def add_sphere(doc, diameter=100, position=None, name=None, **kwargs):
    """Add a sphere to the scene"""
    sphere = c4d.BaseObject(c4d.Osphere)
    
    # Set size
    sphere[c4d.PRIM_SPHERE_RAD] = diameter / 2
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            sphere.SetAbsPos(c4d.Vector(*position))
    
    # Set name
    if name is not None:
        sphere.SetName(name)
    
    # Add to document
    doc.InsertObject(sphere)
    log_line("info", f"Added sphere: {name if name else 'Unnamed'}, diameter: {diameter}")
    
    return sphere

def add_cylinder(doc, radius=50, height=100, position=None, name=None, **kwargs):
    """Add a cylinder to the scene"""
    cylinder = c4d.BaseObject(c4d.Ocylinder)
    
    # Set size
    cylinder[c4d.PRIM_CYLINDER_RADIUS] = radius
    cylinder[c4d.PRIM_CYLINDER_HEIGHT] = height
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            cylinder.SetAbsPos(c4d.Vector(*position))
    
    # Set name
    if name is not None:
        cylinder.SetName(name)
    
    # Add to document
    doc.InsertObject(cylinder)
    log_line("info", f"Added cylinder: {name if name else 'Unnamed'}, radius: {radius}, height: {height}")
    
    return cylinder

def add_plane(doc, width=100, height=100, position=None, name=None, **kwargs):
    """Add a plane to the scene"""
    plane = c4d.BaseObject(c4d.Oplane)
    
    # Set size
    plane[c4d.PRIM_PLANE_WIDTH] = width
    plane[c4d.PRIM_PLANE_HEIGHT] = height
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            plane.SetAbsPos(c4d.Vector(*position))
    
    # Set name
    if name is not None:
        plane.SetName(name)
    
    # Add to document
    doc.InsertObject(plane)
    log_line("info", f"Added plane: {name if name else 'Unnamed'}, width: {width}, height: {height}")
    
    return plane

def add_null(doc, position=None, name=None, **kwargs):
    """Add a null object to the scene"""
    null = c4d.BaseObject(c4d.Onull)
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            null.SetAbsPos(c4d.Vector(*position))
    
    # Set name
    if name is not None:
        null.SetName(name)
    
    # Add to document
    doc.InsertObject(null)
    log_line("info", f"Added null: {name if name else 'Unnamed'}")
    
    return null