import c4d
import os
import sys
import importlib
from typing import Dict, Any, List, Callable
import json

from .logging import log_line

class MCPExecutor:
    """
    Model Command Processor Executor
    Handles the execution of commands from the agent
    """
    def __init__(self):
        self.commands = {
            "AddCube": self.add_cube,
            "AddSphere": self.add_sphere,
            "CreateMaterial": self.create_material,
            "ApplyMaterial": self.apply_material,
            "SelectObject": self.select_object,
            "Duplicate": self.duplicate,
            "GroupSelected": self.group_selected,
            "AddSpline": self.add_spline,
            "CloneAlongSpline": self.clone_along_spline,
            "Randomize": self.randomize,
            "AddCamera": self.add_camera,
            "FrameAll": self.frame_all,
            "EnableOverlay": self.enable_overlay,
            "AddRenderSetting": self.add_render_setting,
            "SetRenderResolution": self.set_render_resolution,
            "ToggleGI": self.toggle_gi,
            "ToggleViewportAA": self.toggle_viewport_aa,
            "SetFrameRange": self.set_frame_range,
            "RunTool": self.run_tool  # Generic tool runner
            
        }
        self.register_default_commands()
    
    def register_default_commands(self):
        """Register all default commands"""
        # Register primitives
        self.register_command("AddCube", self.add_cube)
        self.register_command("AddSphere", self.add_sphere)
        
        # Register materials
        self.register_command("CreateMaterial", self.create_material)
        self.register_command("ApplyMaterial", self.apply_material)
        
        # Register selection and grouping
        self.register_command("SelectObject", self.select_object)
        self.register_command("Duplicate", self.duplicate)
        self.register_command("GroupSelected", self.group_selected)
        
        # Register splines
        self.register_command("AddSpline", self.add_spline)
        self.register_command("CloneAlongSpline", self.clone_along_spline)
        
        # Register modifiers
        self.register_command("Randomize", self.randomize)
        
        # Register camera
        self.register_command("AddCamera", self.add_camera)
        self.register_command("FrameAll", self.frame_all)
        self.register_command("EnableOverlay", self.enable_overlay)
        
        # Register render settings
        self.register_command("AddRenderSetting", self.add_render_setting)
        self.register_command("SetRenderResolution", self.set_render_resolution)
        self.register_command("ToggleGI", self.toggle_gi)
        self.register_command("ToggleViewportAA", self.toggle_viewport_aa)
        self.register_command("SetFrameRange", self.set_frame_range)
    
    def register_command(self, name: str, func: Callable):
        """Register a command with the executor"""
        self.commands[name] = func
    
    # Modify the run_tool method to properly handle all command types

    def run_tool(self, action: str, **kwargs):
        """
        Generic method to run any tool
        
        Args:
            action: The action to perform
            **kwargs: Arguments for the action
        """
        # Extract doc from kwargs for logging to avoid JSON serialization issues
        doc = kwargs.pop('doc', None) or c4d.documents.GetActiveDocument()
        
        # Now we can safely log the remaining arguments
        log_line("execute", f"{action}({json.dumps(kwargs)})")
        
        # Check if the command is in the commands dictionary
        if action in self.commands:
            # Call the registered method directly
            return self.commands[action](doc, **kwargs)
        
        # If not found directly, try case-insensitive lookup in commands dict
        action_lower = action.lower()
        for cmd_name, cmd_func in self.commands.items():
            if cmd_name.lower() == action_lower:
                return cmd_func(doc, **kwargs)
        
        # If still not found, log a warning and return False
        log_line("warning", f"Unknown command: {action}")
        return False
    # Primitive commands
    def add_cube(self, doc, size=100, position=None, name=None, **kwargs):
        """Add a cube to the scene with automatic parameter discovery"""
        cube = c4d.BaseObject(c4d.Ocube)
        
        # Set name
        if name is not None:
            cube.SetName(name)
        
        # Set cube size - try multiple approaches
        try:
            # Method 1: Try standard C4D parameter names
            param_attempts = [
                # Standard parameter names
                ('PRIM_CUBE_LEN', 'PRIM_CUBE_WID', 'PRIM_CUBE_HGT'),
                # Alternative names
                ('PRIM_CUBE_SUBX', 'PRIM_CUBE_SUBY', 'PRIM_CUBE_SUBZ'),
                # Numeric IDs (common across versions)
                (1100, 1101, 1102),
                (1000, 1001, 1002),
                (100, 101, 102),
            ]
            
            success = False
            for x_param, y_param, z_param in param_attempts:
                try:
                    # Try to get the parameter ID if it's a string
                    if isinstance(x_param, str):
                        x_id = getattr(c4d, x_param, None)
                        y_id = getattr(c4d, y_param, None)
                        z_id = getattr(c4d, z_param, None)
                        
                        if x_id is not None and y_id is not None and z_id is not None:
                            cube[x_id] = float(size)
                            cube[y_id] = float(size)
                            cube[z_id] = float(size)
                            success = True
                            log_line("info", f"Set cube size using parameter names: {x_param}, {y_param}, {z_param}")
                            break
                    else:
                        # Try numeric IDs directly
                        cube[x_param] = float(size)
                        cube[y_param] = float(size)
                        cube[z_param] = float(size)
                        success = True
                        log_line("info", f"Set cube size using parameter IDs: {x_param}, {y_param}, {z_param}")
                        break
                        
                except Exception as e:
                    continue
            
            if not success:
                log_line("warning", f"Could not set cube size - using default size")
            else:
                log_line("info", f"Successfully created cube with size {size}")
                
        except Exception as e:
            log_line("error", f"Error setting cube dimensions: {str(e)}")
        
        # Set position
        if position is not None:
            if isinstance(position, list) and len(position) == 3:
                pos = c4d.Vector(float(position[0]), float(position[1]), float(position[2]))
                cube.SetAbsPos(pos)
        
        # Add to document
        doc.InsertObject(cube)
        
        # Force update to refresh UI
        c4d.EventAdd()
        c4d.DrawViews()
        
        return cube
    
    def add_sphere(self, doc, diameter=100, position=None, name=None, **kwargs):
        """Add a sphere to the scene"""
        sphere = c4d.BaseObject(c4d.Osphere)
        
        # Set name
        if name is not None:
            sphere.SetName(name)
        
        # Get data instance for parameter access
        data = sphere.GetDataInstance()
        
        try:
            # Common parameter ID for sphere radius (might vary by C4D version)
            radius_param = 1001  # Common ID for radius
            data.SetFloat(radius_param, float(diameter) / 2)
            
            log_line("info", f"Created sphere with diameter {diameter}")
        except Exception as e:
            log_line("error", f"Error setting sphere dimensions: {str(e)}")
        
        # Set position
        if position is not None:
            if isinstance(position, list) and len(position) == 3:
                pos = c4d.Vector(float(position[0]), float(position[1]), float(position[2]))
                sphere.SetAbsPos(pos)
        
        # Add to document
        doc.InsertObject(sphere)
        
        return sphere
    
    # Material commands
    def create_material(self, doc, name=None, type=None, color=None, **kwargs):
        """Create a new material"""
        mat = c4d.BaseMaterial(c4d.Mmaterial)
        
        # Set name
        if name is not None:
            mat.SetName(name)
        
        # Get the material's data instance for safer parameter setting
        data = mat.GetDataInstance()
        
        # Define common material parameter IDs that are more stable across C4D versions
        mat_params = {
            'COLOR': 3000,          # Base color (common ID)
            'SPECULAR_WIDTH': 1500, # Specular width parameter ID
            'SPECULAR_HEIGHT': 1501, # Specular height parameter ID
            'REFLECTION': 2000,     # Reflection parameter ID
        }
        
        # Set color
        if color is not None:
            if isinstance(color, list) and len(color) == 3:
                col = c4d.Vector(*color)
                # Set using data instance for increased compatibility
                data.SetVector(mat_params['COLOR'], col)
                log_line("info", f"Set material color to {color}")
        
        # Set material type based on parameters
        if type is not None:
            if type.lower() == "glossy":
                # Set high specular and reflection using safe parameter IDs
                try:
                    data.SetFloat(mat_params['SPECULAR_WIDTH'], 0.1)
                    data.SetFloat(mat_params['SPECULAR_HEIGHT'], 0.8)
                    data.SetFloat(mat_params['REFLECTION'], 0.5)
                    log_line("info", f"Created glossy material: {name}")
                except Exception as e:
                    log_line("error", f"Error setting glossy material parameters: {str(e)}")
                    
            elif type.lower() == "matte":
                # Set low specular and reflection
                try:
                    data.SetFloat(mat_params['SPECULAR_WIDTH'], 0.8)
                    data.SetFloat(mat_params['SPECULAR_HEIGHT'], 0.1)
                    data.SetFloat(mat_params['REFLECTION'], 0.0)
                    log_line("info", f"Created matte material: {name}")
                except Exception as e:
                    log_line("error", f"Error setting matte material parameters: {str(e)}")
        
        # Add to document
        doc.InsertMaterial(mat)
        
        return mat
    
    # Improve the apply_material method

    def apply_material(self, doc, name=None, to=None, **kwargs):
        """Apply a material to an object"""
        if name is None or to is None:
            log_line("error", "Material name or target object not specified")
            return False
        
        # Find material by name
        material = None
        materials = doc.GetMaterials()
        for mat in materials:
            if mat.GetName() == name:
                material = mat
                break
        
        if material is None:
            log_line("error", f"Material not found: {name}")
            return False
        
        # Find object by name
        obj = None
        if isinstance(to, str):
            obj = self._find_object_by_name(doc.GetFirstObject(), to)
        
        if obj is None:
            log_line("error", f"Object not found: {to}")
            return False
        
        try:
            # Apply material tag
            tag = c4d.TextureTag()
            tag.SetMaterial(material)
            obj.InsertTag(tag)
            
            log_line("info", f"Applied material '{name}' to object '{to}'")
            return True
        except Exception as e:
            log_line("error", f"Error applying material: {str(e)}")
            return False
    
    # Selection and grouping commands
    def select_object(self, doc, name=None, **kwargs):
        """Select an object by name"""
        if name is None:
            return False
        
        obj = self._find_object_by_name(doc.GetFirstObject(), name)
        if obj is None:
            log_line("error", f"Object not found: {name}")
            return False
        
        doc.SetActiveObject(obj)
        return True
    
    def duplicate(self, doc, count=1, axis="X", distance=100, **kwargs):
        """Duplicate the selected object multiple times"""
        obj = doc.GetActiveObject()
        if obj is None:
            log_line("error", "No active object to duplicate")
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
            
            # Set position for this clone
            pos += direction
            clone.SetAbsPos(pos)
            
            # Insert into document
            doc.InsertObject(clone)
            results.append(clone)
        
        return results
    
    def group_selected(self, doc, name=None, **kwargs):
        """Group selected objects under a new null object"""
        # Create null object
        null = c4d.BaseObject(c4d.Onull)
        
        # Set name
        if name is not None:
            null.SetName(name)
        
        # Insert null into document
        doc.InsertObject(null)
        
        # Get selected objects
        selected = doc.GetActiveObjects(c4d.GETACTIVEOBJECTFLAGS_CHILDREN)
        if not selected:
            selected = []
            obj = doc.GetActiveObject()
            if obj:
                selected.append(obj)
        
        if not selected:
            log_line("error", "No objects selected to group")
            return False
        
        # Move selected objects under null
        for obj in selected:
            original_parent = obj.GetUp()
            if original_parent:
                obj.Remove()
            
            obj.InsertUnder(null)
        
        return null
    
    # Spline commands
    def add_spline(self, doc, type="Circle", radius=100, plane="XZ", **kwargs):
        """Add a spline object to the scene"""
        # Determine which spline type to create
        spline_type = c4d.Osplinecircle  # Default to circle
        if type.lower() == "circle":
            spline_type = c4d.Osplinecircle
        elif type.lower() == "rectangle":
            spline_type = c4d.Osplinerectangle
        elif type.lower() == "bezier":
            spline_type = c4d.Ospline
        
        # Create the spline object
        spline = c4d.BaseObject(spline_type)
        
        # Set name if provided
        if "name" in kwargs:
            spline.SetName(kwargs["name"])
        
        # For circle spline, set radius
        if spline_type == c4d.Osplinecircle:
            spline[c4d.PRIM_CIRCLE_RADIUS] = radius
        
        # Handle plane orientation with proper rotation
        if plane:
            # Instead of using SetRotation, use SetRotationOrder and SetAbsRot
            if plane.upper() == "XY":
                # XY plane is default, no rotation needed
                pass
            elif plane.upper() == "XZ":
                # Rotate 90 degrees around X axis
                rot = c4d.Vector(c4d.utils.DegToRad(90), 0, 0)
                spline.SetAbsRot(rot)
            elif plane.upper() == "YZ":
                # Rotate 90 degrees around Y axis
                rot = c4d.Vector(0, c4d.utils.DegToRad(90), 0)
                spline.SetAbsRot(rot)
        
        # Insert into document
        doc.InsertObject(spline)
        
        # Update Cinema 4D
        c4d.EventAdd()
        
        return spline
        
    # Improve the clone_along_spline method for better error handling

    def clone_along_spline(self, doc, source=None, spline_index=0, count=10, **kwargs):
        """Clone an object along a spline"""
        # Find source object
        src_obj = None
        if isinstance(source, str):
            src_obj = self._find_object_by_name(doc.GetFirstObject(), source)
        
        if src_obj is None:
            log_line("error", f"Source object not found: {source}")
            return False
        
        # Find spline (try to find a spline in the scene)
        splines = []
        obj = doc.GetFirstObject()
        while obj:
            # Check if object is a spline - FIXED: Removed non-existent Osplineellipse
            spline_types = [c4d.Ospline, c4d.Osplinecircle, c4d.Osplinerectangle]
            if obj.GetType() in spline_types:
                splines.append(obj)
            obj = obj.GetNext()
        
        if not splines:
            # Create a default circle spline if none exists
            log_line("info", "No spline found, creating a circle spline")
            spline = c4d.BaseObject(c4d.Osplinecircle)
            spline.SetName("DefaultSpline")
            spline[c4d.PRIM_CIRCLE_RADIUS] = 500
            doc.InsertObject(spline)
            splines.append(spline)
        
        # Use the specified spline or the first one
        spline_idx = min(spline_index, len(splines) - 1) if splines else 0
        spline = splines[spline_idx] if splines else None
        
        if spline is None:
            log_line("error", "No spline available for cloning")
            return False
        
        # Create a MoGraph Cloner object
        # First check if MoGraph is available
        try:
            # MoGraph Cloner ID
            MOGRAPH_CLONER_ID = 1018544
            
            cloner = c4d.BaseObject(MOGRAPH_CLONER_ID)  # MoGraph Cloner
            if cloner is None:
                log_line("error", "Could not create MoGraph Cloner - MoGraph module may not be available")
                return False
                
            cloner.SetName("Clones")
            
            # Set cloner properties - these IDs may vary by Cinema 4D version
            # Common MoGraph parameter IDs
            MG_OBJECT_LINK = 1001
            MG_SPLINE_MODE = 1057
            MG_SPLINE_COUNT = 1073
            MG_DISTRIBUTION = 1010
            MG_CLONE_MODE = 1000
            
            # Set to "Object" mode (2)
            cloner[MG_CLONE_MODE] = 2
            cloner[MG_OBJECT_LINK] = spline
            
            # Set distribution to "Count" mode and set count
            cloner[MG_DISTRIBUTION] = 0  # 0 = Count, 1 = Step
            cloner[MG_SPLINE_COUNT] = count
            
            # Add source as child of cloner
            src_copy = src_obj.GetClone()
            src_copy.InsertUnder(cloner)
            
            # Add cloner to document
            doc.InsertObject(cloner)
            
            return cloner
        except Exception as e:
            log_line("error", f"Error creating cloner: {str(e)}")
            return False
        
    # Modifier commands
    def randomize(self, doc, target=None, axis="Y", amount=50, **kwargs):
        """Add randomization to objects"""
        # Find target
        obj = None
        if isinstance(target, str):
            obj = self._find_object_by_name(doc.GetFirstObject(), target)
        
        if obj is None and target is not None:
            log_line("error", f"Target not found: {target}")
            return False
        
        # If no specific target, use selected object
        if obj is None:
            obj = doc.GetActiveObject()
        
        if obj is None:
            log_line("error", "No target object specified or selected")
            return False
        
        # Create random effector
        effector = c4d.BaseObject(1018643)  # MoGraph Random Effector
        effector.SetName("RandomEffector")
        
        # Set effector properties
        if axis.upper() == "X":
            effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = True
            effector[c4d.ID_MG_BASEEFFECTOR_POSITION, c4d.VECTOR_X] = amount
        elif axis.upper() == "Y":
            effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = True
            effector[c4d.ID_MG_BASEEFFECTOR_POSITION, c4d.VECTOR_Y] = amount
        elif axis.upper() == "Z":
            effector[c4d.ID_MG_BASEEFFECTOR_POSITION_ACTIVE] = True
            effector[c4d.ID_MG_BASEEFFECTOR_POSITION, c4d.VECTOR_Z] = amount
        
        # Add effector to document
        doc.InsertObject(effector)
        
        # If the target is a cloner, add the effector to it
        if obj.CheckType(1018544):  # MoGraph Cloner
            effector.InsertUnder(obj)
        
        return effector
    
    # Camera commands
    def add_camera(self, doc, focal_length=36, name=None, **kwargs):
        """Add a camera to the scene"""
        camera = c4d.BaseObject(c4d.Ocamera)
        
        # Set focal length
        camera[c4d.CAMERA_FOCUS] = focal_length
        
        # Set name
        if name is not None:
            camera.SetName(name)
        
        # Add to document
        doc.InsertObject(camera)
        
        return camera
    
    def frame_all(self, doc, **kwargs):
        """Frame all objects in the view"""
        c4d.CallCommand(12151)  # Frame All command
        return True
    
    def enable_overlay(self, doc, type="Thirds", **kwargs):
        """Enable camera overlay like rule of thirds, etc."""
        try:
            # Get active viewport
            bd = doc.GetActiveBaseDraw()
            if not bd:
                log_line("error", "No active viewport")
                return False
            
            # Get active camera
            camera = bd.GetSceneCamera(doc)
            if not camera:
                log_line("error", "No active camera")
                return False
            
            # Try parameter-based approach first
            try:
                # Set camera parameters directly (most compatible method)
                if type.lower() == "thirds" or type.lower() == "ruleofthirds":
                    # Common parameter IDs for composition guides
                    camera[1057] = True  # Enable guides - parameter ID may vary by C4D version
                    camera[1058] = 0     # Rule of Thirds mode
                elif type.lower() == "goldenspiral" or type.lower() == "golden":
                    camera[1057] = True  # Enable guides
                    camera[1058] = 1     # Golden Spiral mode
                    
                log_line("info", f"Enabled {type} overlay on camera {camera.GetName()}")
            except:
                # Fallback to command-based approach
                # Use Cinema 4D command IDs to enable guides
                c4d.CallCommand(440000088)  # Show Composition Guides toggle
                
                log_line("info", f"Enabled camera guides via command")
                
            # Update the view
            c4d.DrawViews()
            c4d.EventAdd()
            return True
            
        except Exception as e:
            log_line("error", f"Error enabling camera overlay: {str(e)}")
            return False
    
    # Render settings commands
    def add_render_setting(self, doc, name="QuickPreview", **kwargs):
        """Add a new render setting preset"""
        try:
            # Create new render data
            rd = c4d.documents.RenderData()
            
            # Set name
            if name:
                rd.SetName(name)
            
            # Apply provided settings if any
            for key, value in kwargs.items():
                # Try to find parameter ID for the key
                # This is a simplified approach
                if key.lower() == "width":
                    rd[c4d.RDATA_XRES] = value
                elif key.lower() == "height":
                    rd[c4d.RDATA_YRES] = value
                elif key.lower() == "fps":
                    rd[c4d.RDATA_FRAMERATE] = value
                    
            # Insert the render data into document
            doc.InsertRenderData(rd)
            
            # Activate the new render settings
            doc.SetActiveRenderData(rd)
            
            c4d.EventAdd()
            log_line("info", f"Created render preset: {name}")
            return rd
            
        except Exception as e:
            log_line("error", f"Error creating render preset: {str(e)}")
            return False
    
    def set_render_resolution(self, doc, width=1920, height=1080, fps=30, **kwargs):
        """Set render resolution and frame rate"""
        try:
            # Get active render data
            rd = doc.GetActiveRenderData()
            if not rd:
                log_line("error", "No render settings available")
                return False
            
            # Set resolution
            if width:
                rd[c4d.RDATA_XRES] = width
            if height:
                rd[c4d.RDATA_YRES] = height
                
            # Set frame rate
            if fps:
                # Try both common frame rate parameters
                try:
                    rd[c4d.RDATA_FRAMERATE] = fps
                except:
                    # Alternative ID for frame rate in some C4D versions
                    try:
                        rd[c4d.RDATA_FRAMESCALE] = fps
                    except:
                        log_line("warning", "Could not set frame rate")
            
            c4d.EventAdd()
            log_line("info", f"Set render resolution to {width}x{height} at {fps}fps")
            return True
            
        except Exception as e:
            log_line("error", f"Error setting render resolution: {str(e)}")
            return False
    
    def toggle_gi(self, doc, enabled=True, **kwargs):
        """Toggle Global Illumination in render settings"""
        # Get current render data
        rd = doc.GetActiveRenderData()
        if not rd:
            log_line("error", "No render settings available")
            return False
        
        try:
            # Approach 1: Try different common parameter IDs
            # These are the most common IDs for GI across C4D versions:
            gi_enable_ids = [
                7000,  # Common ID for GI
                7001,  # Another common ID
                'RDATA_GI_ENABLE', # Symbolic name (may not work)
                'GI_ENABLE_FLAG', # Another symbolic name
                'RDATA_OPTION_GI', # Another possible ID
            ]
            
            success = False
            for id_val in gi_enable_ids:
                try:
                    # Try to convert string to integer if it's a numeric string
                    if isinstance(id_val, str) and id_val.isdigit():
                        id_val = int(id_val)
                    
                    # Try to set the parameter
                    if isinstance(id_val, int):
                        rd[id_val] = enabled
                        log_line("info", f"Set GI enabled={enabled} using ID {id_val}")
                        success = True
                        break
                except:
                    continue
            
            # If we couldn't set it directly, try the alternative approach
            if not success:
                # Approach 2: Use VideoPost for GI if available
                vp_list = rd.GetVideoPostList()
                for vp in vp_list:
                    if "global illumination" in vp.GetName().lower():
                        # Found the GI post effect, enable/disable it
                        vp.SetAllBits(c4d.BIT_ACTIVE, enabled)
                        log_line("info", f"Set GI VideoPost to enabled={enabled}")
                        success = True
                        break
                        
            if success:
                c4d.EventAdd()
                return True
            else:
                log_line("warning", f"Could not find GI setting to set enabled={enabled}")
                return False
                
        except Exception as e:
            log_line("error", f"Error toggling GI: {str(e)}")
            return False
    
    def toggle_viewport_aa(self, doc, enabled=True, **kwargs):
        """Toggle viewport anti-aliasing"""
        try:
            # Method 1: Try command-based approach (most reliable)
            if enabled:
                c4d.CallCommand(12156)  # Anti-Aliasing ON command ID
            else:
                c4d.CallCommand(12157)  # Anti-Aliasing OFF command ID
            
            # Method 2: Try some common parameter IDs as backup
            bd = doc.GetActiveBaseDraw()
            if bd:
                try:
                    # Try common parameter IDs (these vary by C4D version)
                    aa_param_ids = [
                        c4d.BASEDRAW_ANTIALIASING,         # Common ID name
                        c4d.BASEDRAW_DISPLAYFILTER_ANTIALIASING,  # Alternative ID name
                        1001,  # Numerical ID often used for AA
                        1023,  # Alternative numerical ID
                    ]
                    
                    for param_id in aa_param_ids:
                        try:
                            bd[param_id] = enabled
                            break  # Stop if successful
                        except:
                            continue
                except:
                    # Already handled by command approach
                    pass
                    
            log_line("info", f"Set viewport anti-aliasing to enabled={enabled}")
            return True
            
        except Exception as e:
            log_line("error", f"Error toggling viewport AA: {str(e)}")
            return False
    
    def set_frame_range(self, doc, start=0, end=100, **kwargs):
        """Set document frame range"""
        try:
            # Set document min/max time
            doc.SetMinTime(c4d.BaseTime(start, doc.GetFps()))
            doc.SetMaxTime(c4d.BaseTime(end, doc.GetFps()))
            
            # Update timeline
            c4d.EventAdd()
            
            log_line("info", f"Set frame range to {start}-{end}")
            return True
            
        except Exception as e:
            log_line("error", f"Error setting frame range: {str(e)}")
            return False
    
    # Helper methods
    # Improve the _find_object_by_name method

    def _find_object_by_name(self, start_obj, name):
        """Find an object by name in the hierarchy"""
        if not start_obj:
            return None
        
        # Name can be None in some cases
        if name is None:
            return None
            
        # First perform a document-wide search
        doc = c4d.documents.GetActiveDocument()
        objects = doc.GetObjects()
        
        # Direct matching first (faster)
        for obj in objects:
            if obj.GetName() == name:
                return obj
        
        # Then try case-insensitive (more flexible)
        name_lower = name.lower()
        for obj in objects:
            if obj.GetName().lower() == name_lower:
                return obj
        
        # Recursive search as a fallback (for deep hierarchies)
        def search_recursive(obj, target_name):
            if not obj:
                return None
            
            if obj.GetName() == target_name:
                return obj
            
            # Try children
            child = obj.GetDown()
            if child:
                result = search_recursive(child, target_name)
                if result:
                    return result
            
            # Try next
            sibling = obj.GetNext()
            if sibling:
                return search_recursive(sibling, target_name)
            
            return None
        
        return search_recursive(start_obj, name)

def add_light(self, doc, type="point", position=None, name=None, intensity=100, color=None, **kwargs):
    """Add a light to the scene"""
    try:
        # Map light types to Cinema 4D light objects
        light_types = {
            "point": c4d.Olight,
            "spot": c4d.Olight,
            "area": c4d.Olight,
            "infinite": c4d.Olight,
            "sun": c4d.Olight
        }
        
        # Create the light object
        light_obj_type = light_types.get(type, c4d.Olight)
        light = c4d.BaseObject(light_obj_type)
        
        if not light:
            log_line("error", f"Failed to create light object")
            return None
        
        # Set name
        if name:
            light.SetName(name)
        else:
            light.SetName(f"{type.title()}Light")
        
        # Set light type using parameters
        try:
            if type == "point":
                light[c4d.LIGHT_TYPE] = c4d.LIGHT_TYPE_OMNI
            elif type == "spot":
                light[c4d.LIGHT_TYPE] = c4d.LIGHT_TYPE_SPOT
            elif type == "area":
                light[c4d.LIGHT_TYPE] = c4d.LIGHT_TYPE_AREA
            elif type == "infinite":
                light[c4d.LIGHT_TYPE] = c4d.LIGHT_TYPE_INFINITE
            elif type == "sun":
                light[c4d.LIGHT_TYPE] = c4d.LIGHT_TYPE_SUN
            
            log_line("info", f"Set light type to {type}")
        except Exception as e:
            log_line("warning", f"Could not set light type: {str(e)}")
        
        # Set intensity
        try:
            light[c4d.LIGHT_BRIGHTNESS] = float(intensity)
            log_line("info", f"Set light intensity to {intensity}")
        except Exception as e:
            log_line("warning", f"Could not set light intensity: {str(e)}")
        
        # Set color if provided
        if color and isinstance(color, list) and len(color) == 3:
            try:
                color_vector = c4d.Vector(float(color[0]), float(color[1]), float(color[2]))
                light[c4d.LIGHT_COLOR] = color_vector
                log_line("info", f"Set light color to {color}")
            except Exception as e:
                log_line("warning", f"Could not set light color: {str(e)}")
        
        # Set position
        if position and isinstance(position, list) and len(position) == 3:
            try:
                pos = c4d.Vector(float(position[0]), float(position[1]), float(position[2]))
                light.SetAbsPos(pos)
                log_line("info", f"Set light position to {position}")
            except Exception as e:
                log_line("warning", f"Could not set light position: {str(e)}")
        
        # Add to document
        doc.InsertObject(light)
        
        # Update document
        c4d.EventAdd()
        
        log_line("info", f"Successfully created {type} light: {light.GetName()}")
        return light
        
    except Exception as e:
        log_line("error", f"Error creating light: {str(e)}")
        return None

# Create a single instance to be used by the execute_commands function
_mcp = MCPExecutor()

# Update the execute_commands function to handle commands more reliably

def execute_commands(cmd_list):
    """
    Execute a list of commands
    
    Args:
        cmd_list: List of command dictionaries
    """
    # Get active document
    doc = c4d.documents.GetActiveDocument()
    
    # Make sure we have commands
    if not cmd_list:
        log_line("warning", "No commands to execute")
        return
    
    # Start undo
    doc.StartUndo()
    
    try:
        # Execute each command
        for cmd in cmd_list:
            action = cmd.get("action", "")
            args = cmd.get("args", {})
            
            log_line("execute", f"Executing {action} with args: {args}")
            
            # Always use run_tool for consistent behavior
            _mcp.run_tool(action, doc=doc, **args)
        
        # Update the document
        doc.EndUndo()
        c4d.EventAdd()
        
    except Exception as e:
        doc.EndUndo()
        log_line("error", f"Error executing commands: {str(e)}")
        raise