import c4d
from ..logging import log_line

def create_material(doc, name=None, type=None, color=None, reflectance=None, roughness=None, **kwargs):
    """Create a new material"""
    mat = c4d.BaseMaterial(c4d.Mmaterial)
    
    # Set name
    if name is not None:
        mat.SetName(name)
    
    # Set color
    if color is not None:
        if isinstance(color, list) and len(color) == 3:
            col = c4d.Vector(*color)
            mat[c4d.MATERIAL_COLOR_COLOR] = col
    
    # Set material type based on parameters
    if type is not None:
        if type.lower() == "glossy":
            # Set high specular and reflection
            mat[c4d.MATERIAL_SPECULAR_WIDTH] = 0.1
            mat[c4d.MATERIAL_SPECULAR_HEIGHT] = 0.8
            mat[c4d.MATERIAL_REFLECTION_LEVEL] = 0.5 if reflectance is None else reflectance
        elif type.lower() == "matte":
            # Set low specular and reflection
            mat[c4d.MATERIAL_SPECULAR_WIDTH] = 0.8
            mat[c4d.MATERIAL_SPECULAR_HEIGHT] = 0.1
            mat[c4d.MATERIAL_REFLECTION_LEVEL] = 0.0
        elif type.lower() == "metal":
            # Set metallic properties
            mat[c4d.MATERIAL_SPECULAR_WIDTH] = 0.05
            mat[c4d.MATERIAL_SPECULAR_HEIGHT] = 1.0
            mat[c4d.MATERIAL_REFLECTION_LEVEL] = 0.8 if reflectance is None else reflectance
    
    # Set roughness if specified
    if roughness is not None:
        mat[c4d.MATERIAL_REFLECTION_ROUGHNESS] = roughness
    
    # Add to document
    doc.InsertMaterial(mat)
    log_line("info", f"Created material: {name if name else 'Unnamed'}, type: {type if type else 'standard'}")
    
    return mat

def apply_material(doc, material=None, material_name=None, object=None, object_name=None, **kwargs):
    """Apply a material to an object"""
    # Find material by name or use provided material
    mat = None
    if material is not None and isinstance(material, c4d.BaseMaterial):
        mat = material
    elif material_name is not None:
        materials = doc.GetMaterials()
        for m in materials:
            if m.GetName() == material_name:
                mat = m
                break
    
    if mat is None:
        log_line("error", f"Material not found: {material_name}")
        return False
    
    # Find object by name or use provided object
    obj = None
    if object is not None and isinstance(object, c4d.BaseObject):
        obj = object
    elif object_name is not None:
        obj = find_object_by_name(doc.GetFirstObject(), object_name)
    
    if obj is None:
        log_line("error", f"Object not found: {object_name}")
        return False
    
    # Apply material
    obj.InsertMaterial(mat)
    obj.SetMl(mat)
    log_line("info", f"Applied material '{mat.GetName()}' to object '{obj.GetName()}'")
    
    return True

def create_texture(doc, material=None, material_name=None, channel="color", texture_path=None, **kwargs):
    """Add a texture to a material channel"""
    # Find material by name or use provided material
    mat = None
    if material is not None and isinstance(material, c4d.BaseMaterial):
        mat = material
    elif material_name is not None:
        materials = doc.GetMaterials()
        for m in materials:
            if m.GetName() == material_name:
                mat = m
                break
    
    if mat is None:
        log_line("error", f"Material not found: {material_name}")
        return False
    
    # Determine channel ID
    channel_id = c4d.MATERIAL_COLOR_SHADER
    if channel.lower() == "bump":
        channel_id = c4d.MATERIAL_BUMP_SHADER
    elif channel.lower() == "alpha":
        channel_id = c4d.MATERIAL_ALPHA_SHADER
    elif channel.lower() == "specular":
        channel_id = c4d.MATERIAL_SPECULAR_SHADER
    elif channel.lower() == "reflection":
        channel_id = c4d.MATERIAL_REFLECTION_SHADER
    
    # Create bitmap shader
    if texture_path:
        shader = c4d.BaseShader(c4d.Xbitmap)
        shader[c4d.BITMAPSHADER_FILENAME] = texture_path
        mat[channel_id] = shader
        log_line("info", f"Added texture to material '{mat.GetName()}', channel: {channel}")
        return True
    
    return False

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