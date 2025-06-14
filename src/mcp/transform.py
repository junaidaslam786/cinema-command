import c4d
from math import radians
from ..logging import log_line

def set_position(doc, object=None, object_name=None, position=None, **kwargs):
    """
    Set object position
    
    Args:
        object: Object to modify
        object_name: Name of object to find
        position: [x, y, z] position coordinates
    """
    # Find object
    obj = None
    if object is not None and isinstance(object, c4d.BaseObject):
        obj = object
    elif object_name is not None:
        obj = find_object_by_name(doc.GetFirstObject(), object_name)
    else:
        # Use active object
        obj = doc.GetActiveObject()
    
    if obj is None:
        log_line("error", "No object found for position change")
        return False
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            obj.SetAbsPos(c4d.Vector(*position))
            log_line("info", f"Set position of '{obj.GetName()}' to {position}")
            return True
    
    log_line("error", "Invalid position format")
    return False

def set_rotation(doc, object=None, object_name=None, rotation=None, degrees=True, **kwargs):
    """
    Set object rotation
    
    Args:
        object: Object to modify
        object_name: Name of object to find
        rotation: [h, p, b] rotation angles
        degrees: True if angles are in degrees, False for radians
    """
    # Find object
    obj = None
    if object is not None and isinstance(object, c4d.BaseObject):
        obj = object
    elif object_name is not None:
        obj = find_object_by_name(doc.GetFirstObject(), object_name)
    else:
        # Use active object
        obj = doc.GetActiveObject()
    
    if obj is None:
        log_line("error", "No object found for rotation change")
        return False
    
    # Set rotation
    if rotation is not None:
        if isinstance(rotation, list) and len(rotation) == 3:
            if degrees:
                # Convert degrees to radians
                rot = c4d.Vector(radians(rotation[0]), radians(rotation[1]), radians(rotation[2]))
            else:
                rot = c4d.Vector(*rotation)
            
            obj.SetRotation(rot)
            log_line("info", f"Set rotation of '{obj.GetName()}' to {rotation}{'° (degrees)' if degrees else ' (radians)'}")
            return True
    
    log_line("error", "Invalid rotation format")
    return False

def set_scale(doc, object=None, object_name=None, scale=None, uniform=None, **kwargs):
    """
    Set object scale
    
    Args:
        object: Object to modify
        object_name: Name of object to find
        scale: Scale factor or [x, y, z] scale factors
        uniform: If True and scale is a single number, apply uniform scaling
    """
    # Find object
    obj = None
    if object is not None and isinstance(object, c4d.BaseObject):
        obj = object
    elif object_name is not None:
        obj = find_object_by_name(doc.GetFirstObject(), object_name)
    else:
        # Use active object
        obj = doc.GetActiveObject()
    
    if obj is None:
        log_line("error", "No object found for scale change")
        return False
    
    # Set scale
    if scale is not None:
        if isinstance(scale, (int, float)) or (isinstance(uniform, bool) and uniform):
            # Uniform scaling
            s = float(scale)
            obj.SetScale(c4d.Vector(s, s, s))
            log_line("info", f"Set uniform scale of '{obj.GetName()}' to {s}")
            return True
        elif isinstance(scale, list) and len(scale) == 3:
            # Non-uniform scaling
            obj.SetScale(c4d.Vector(*scale))
            log_line("info", f"Set scale of '{obj.GetName()}' to {scale}")
            return True
    
    log_line("error", "Invalid scale format")
    return False

def duplicate(doc, object=None, object_name=None, count=1, axis="X", distance=100, **kwargs):
    """
    Duplicate an object multiple times
    
    Args:
        object: Object to duplicate
        object_name: Name of object to find
        count: Number of duplicates
        axis: Axis to distribute along (X, Y, Z)
        distance: Distance between duplicates
    """
    # Find object
    obj = None
    if object is not None and isinstance(object, c4d.BaseObject):
        obj = object
    elif object_name is not None:
        obj = find_object_by_name(doc.GetFirstObject(), object_name)
    else:
        # Use active object
        obj = doc.GetActiveObject()
    
    if obj is None:
        log_line("error", "No object found to duplicate")
        return False
    
    # Determine the direction vector
    direction = c4d.Vector(0, 0, 0)
    if axis.upper() == "X":
        direction.x = distance
    elif axis.upper() == "Y":
        direction.y = distance
    elif axis.upper() == "Z":
        direction.z = distance
    
    # Create duplicates
    results = [obj]
    pos = obj.GetAbsPos()
    
    for i in range(count):
        # Create a clone
        clone = obj.GetClone()
        clone.SetName(f"{obj.GetName()}_{i+1}")
        
        # Set position for this clone
        pos += direction
        clone.SetAbsPos(pos)
        
        # Insert into document
        doc.InsertObject(clone)
        results.append(clone)
    
    log_line("info", f"Duplicated '{obj.GetName()}' {count} times along {axis}-axis, {distance} units apart")
    return results

def group_selected(doc, objects=None, name=None, **kwargs):
    """
    Group objects under a new null object
    
    Args:
        objects: List of objects to group
        name: Name for the null object
    """
    # Create null object
    null = c4d.BaseObject(c4d.Onull)
    
    # Set name
    if name is not None:
        null.SetName(name)
    
    # Add to document
    doc.InsertObject(null)
    
    # Get objects to group
    if objects is None or not objects:
        # Use selected objects
        selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
        if not selected:
            # If nothing selected, try active object
            active = doc.GetActiveObject()
            if active:
                selected = [active]
    else:
        # Use provided objects
        selected = []
        for obj in objects:
            if isinstance(obj, c4d.BaseObject):
                selected.append(obj)
            elif isinstance(obj, str):
                found = find_object_by_name(doc.GetFirstObject(), obj)
                if found:
                    selected.append(found)
    
    if not selected:
        log_line("error", "No objects selected to group")
        return False
    
    # Move selected objects under null
    for obj in selected:
        original_parent = obj.GetUp()
        if original_parent:
            obj.Remove()
        
        obj.InsertUnder(null)
    
    log_line("info", f"Grouped {len(selected)} objects under '{null.GetName()}'")
    return null

def randomize(doc, object=None, object_name=None, axis="Y", amount=50, seed=None, **kwargs):
    """
    Add randomization to objects
    
    Args:
        object: Object to randomize
        object_name: Name of object to find
        axis: Axis to randomize (X, Y, Z or combination)
        amount: Random amount
        seed: Random seed
    """
    # Find object
    obj = None
    if object is not None and isinstance(object, c4d.BaseObject):
        obj = object
    elif object_name is not None:
        obj = find_object_by_name(doc.GetFirstObject(), object_name)
    else:
        # Use active object
        obj = doc.GetActiveObject()
    
    if obj is None:
        log_line("error", "No object found to randomize")
        return False
    
    # Create random effector
    effector = c4d.BaseObject(1018643)  # MoGraph Random Effector
    effector.SetName("RandomEffector")
    
    # Set random seed if provided
    if seed is not None:
        effector[c4d.ID_MG_BASEEFFECTOR_SEED] = seed
    
    # Set randomization parameters
    if "X" in axis.upper():
        effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = True
        effector[c4d.ID_MG_BASEEFFECTOR_POSITION, c4d.VECTOR_X] = amount
    
    if "Y" in axis.upper():
        effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = True
        effector[c4d.ID_MG_BASEEFFECTOR_POSITION, c4d.VECTOR_Y] = amount
    
    if "Z" in axis.upper():
        effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = True
        effector[c4d.ID_MG_BASEEFFECTOR_POSITION, c4d.VECTOR_Z] = amount
    
    # Add effector to document
    doc.InsertObject(effector)
    
    # If the target is a cloner, add the effector to it
    if obj.CheckType(1018544):  # MoGraph Cloner
        effector.InsertUnder(obj)
    
    log_line("info", f"Added randomization to '{obj.GetName()}' on {axis}-axis with amount {amount}")
    return effector

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