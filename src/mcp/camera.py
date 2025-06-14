import c4d
import math
from ..logging import log_line

def add_camera(doc, focal_length=36, position=None, target=None, name=None, **kwargs):
    """Add a camera to the scene"""
    camera = c4d.BaseObject(c4d.Ocamera)
    
    # Set focal length
    camera[c4d.CAMERA_FOCUS] = focal_length
    
    # Set position
    if position is not None:
        if isinstance(position, list) and len(position) == 3:
            camera.SetAbsPos(c4d.Vector(*position))
    
    # Set name
    if name is not None:
        camera.SetName(name)
    
    # Add to document
    doc.InsertObject(camera)
    
    # Point at target if specified
    if target is not None:
        if isinstance(target, list) and len(target) == 3:
            point_camera_at(camera, c4d.Vector(*target))
        elif isinstance(target, c4d.BaseObject):
            point_camera_at_object(camera, target)
        elif isinstance(target, str):
            # Try to find object by name
            obj = find_object_by_name(doc.GetFirstObject(), target)
            if obj:
                point_camera_at_object(camera, obj)
    
    log_line("info", f"Added camera: {name if name else 'Camera'}, focal length: {focal_length}mm")
    
    return camera

def point_camera_at(camera, target_pos):
    """Point camera at a position"""
    if not isinstance(camera, c4d.BaseObject) or not camera.CheckType(c4d.Ocamera):
        log_line("error", "Not a valid camera object")
        return False
    
    # Calculate direction vector
    cam_pos = camera.GetAbsPos()
    direction = target_pos - cam_pos
    
    # Convert to HPB (Heading, Pitch, Bank)
    hpb = direction.GetHPB()
    
    # Set camera rotation
    camera.SetRotation(hpb)
    
    return True

def point_camera_at_object(camera, target_obj):
    """Point camera at an object"""
    if not isinstance(target_obj, c4d.BaseObject):
        log_line("error", "Not a valid target object")
        return False
    
    # Get target position (center of object)
    target_pos = target_obj.GetAbsPos()
    
    return point_camera_at(camera, target_pos)

def frame_all(doc, camera=None, padding=1.1, **kwargs):
    """Frame all objects in the view"""
    if camera is None:
        # Use active camera or create a new one
        camera = doc.GetActiveObject()
        if not camera or not camera.CheckType(c4d.Ocamera):
            camera = add_camera(doc, name="Frame Camera")
    
    # Get all visible objects
    all_objects = []
    obj = doc.GetFirstObject()
    while obj:
        if obj != camera:  # Don't include the camera itself
            all_objects.append(obj)
        obj = obj.GetNext()
    
    if not all_objects:
        log_line("warning", "No objects to frame")
        return False
    
    # Calculate bounding box of all objects
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    
    for obj in all_objects:
        # This is simplified - in a real implementation, you'd calculate proper bounds
        pos = obj.GetAbsPos()
        min_x = min(min_x, pos.x - 100)
        min_y = min(min_y, pos.y - 100)
        min_z = min(min_z, pos.z - 100)
        max_x = max(max_x, pos.x + 100)
        max_y = max(max_y, pos.y + 100)
        max_z = max(max_z, pos.z + 100)
    
    # Calculate center point and dimensions
    center = c4d.Vector((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2)
    width = max_x - min_x
    height = max_y - min_y
    depth = max_z - min_z
    
    # Position camera
    # Simplified - in real implementation, consider FOV and aspect ratio
    distance = max(width, height, depth) * padding
    camera_pos = c4d.Vector(center.x, center.y, center.z + distance)
    camera.SetAbsPos(camera_pos)
    
    # Point at center
    point_camera_at(camera, center)
    
    log_line("info", "Framed all objects in camera view")
    return True

def enable_overlay(doc, camera=None, type="GoldenSpiral", **kwargs):
    """Enable camera overlay"""
    if camera is None:
        camera = doc.GetActiveObject()
        if not camera or not camera.CheckType(c4d.Ocamera):
            camera = None
            
            # Look for the last added camera
            obj = doc.GetFirstObject()
            while obj:
                if obj.CheckType(c4d.Ocamera):
                    camera = obj
                obj = obj.GetNext()
    
    if camera is None:
        log_line("error", "No camera found to enable overlay")
        return False
    
    if type.lower() in ["goldenspiral", "golden", "spiral"]:
        camera[c4d.CAMERA_SHOW_COMPOSITION_THIRDS] = True  # Rule of thirds as approximation
        log_line("info", f"Enabled {type} overlay for camera '{camera.GetName()}'")
    elif type.lower() in ["thirds", "ruleofthirds"]:
        camera[c4d.CAMERA_SHOW_COMPOSITION_THIRDS] = True
        log_line("info", f"Enabled Rule of Thirds overlay for camera '{camera.GetName()}'")
    elif type.lower() in ["crosshair", "center"]:
        camera[c4d.CAMERA_SHOW_CROSSHAIR] = True
        log_line("info", f"Enabled crosshair overlay for camera '{camera.GetName()}'")
    
    return True

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