import c4d
from ..logging import log_line

def add_render_setting(doc, name=None, inherit=True, **kwargs):
    """
    Add a new render setting
    
    Args:
        name: Name for the new render setting
        inherit: Whether to inherit from current settings
    """
    # Get active render data to inherit from
    rdata = None
    if inherit:
        rdata = doc.GetActiveRenderData()
        if rdata:
            rdata = rdata.GetClone()
    
    # Create new render data if needed
    if not rdata:
        rdata = c4d.documents.RenderData()
    
    # Set name
    if name is not None:
        rdata.SetName(name)
    
    # Add to document
    doc.InsertRenderData(rdata)
    
    # Set as active render data
    doc.SetActiveRenderData(rdata)
    
    log_line("info", f"Added render setting: {name if name else 'Unnamed'}")
    return rdata

def set_render_resolution(doc, width=1920, height=1080, fps=30, **kwargs):
    """
    Set render resolution and frame rate
    
    Args:
        width: Render width in pixels
        height: Render height in pixels
        fps: Frames per second
    """
    rdata = doc.GetActiveRenderData()
    if not rdata:
        log_line("error", "No active render data")
        return False
    
    # Set resolution
    rdata[c4d.RDATA_XRES] = width
    rdata[c4d.RDATA_YRES] = height
    
    # Set frame rate
    rdata[c4d.RDATA_FRAMERATE] = fps
    
    log_line("info", f"Set render resolution to {width}x{height} at {fps} FPS")
    return True

def toggle_gi(doc, enabled=True, **kwargs):
    """
    Toggle global illumination
    
    Args:
        enabled: Whether GI should be enabled
    """
    rdata = doc.GetActiveRenderData()
    if not rdata:
        log_line("error", "No active render data")
        return False
    
    # Toggle GI
    rdata[c4d.RDATA_GI_ENABLE] = enabled
    
    log_line("info", f"Global Illumination: {'Enabled' if enabled else 'Disabled'}")
    return True

def toggle_ambient_occlusion(doc, enabled=True, **kwargs):
    """
    Toggle ambient occlusion
    
    Args:
        enabled: Whether AO should be enabled
    """
    rdata = doc.GetActiveRenderData()
    if not rdata:
        log_line("error", "No active render data")
        return False
    
    # Toggle AO
    rdata[c4d.RDATA_OPTION_AO] = enabled
    
    log_line("info", f"Ambient Occlusion: {'Enabled' if enabled else 'Disabled'}")
    return True

def toggle_viewport_aa(doc, enabled=True, level=4, **kwargs):
    """
    Toggle viewport anti-aliasing
    
    Args:
        enabled: Whether AA should be enabled
        level: AA quality level (1-4)
    """
    rdata = doc.GetActiveRenderData()
    if not rdata:
        log_line("error", "No active render data")
        return False
    
    # Toggle AA
    if enabled:
        # Clamp level between 1-4
        level = max(1, min(4, level))
        rdata[c4d.RDATA_ANTIALIASING] = level
    else:
        rdata[c4d.RDATA_ANTIALIASING] = 0
    
    log_line("info", f"Viewport Anti-Aliasing: {'Enabled (Level {level})' if enabled else 'Disabled'}")
    return True

def set_frame_range(doc, start=0, end=100, **kwargs):
    """
    Set animation frame range
    
    Args:
        start: Start frame
        end: End frame
    """
    rdata = doc.GetActiveRenderData()
    if not rdata:
        log_line("error", "No active render data")
        return False
    
    # Set frame range
    rdata[c4d.RDATA_FRAMEFROM] = start
    rdata[c4d.RDATA_FRAMETO] = end
    
    # Set document frame range too
    doc[c4d.DOCUMENT_MINTIME] = c4d.BaseTime(start, doc.GetFps())
    doc[c4d.DOCUMENT_MAXTIME] = c4d.BaseTime(end, doc.GetFps())
    
    log_line("info", f"Set frame range: {start} to {end}")
    return True

def set_renderer(doc, renderer="Standard", **kwargs):
    """
    Set render engine
    
    Args:
        renderer: Name of renderer (Standard, Physical, etc.)
    """
    rdata = doc.GetActiveRenderData()
    if not rdata:
        log_line("error", "No active render data")
        return False
    
    # Set renderer based on name
    if renderer.lower() in ["standard", "default"]:
        rdata[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_STANDARD
        log_line("info", "Set renderer: Standard")
    elif renderer.lower() in ["physical", "physical renderer"]:
        rdata[c4d.RDATA_RENDERENGINE] = c4d.RDATA_RENDERENGINE_PHYSICAL
        log_line("info", "Set renderer: Physical")
    else:
        log_line("error", f"Unknown renderer: {renderer}")
        return False
    
    return True

def set_output_path(doc, path, format="JPEG", **kwargs):
    """
    Set render output path and format
    
    Args:
        path: Output file path
        format: Output format (JPEG, PNG, etc.)
    """
    rdata = doc.GetActiveRenderData()
    if not rdata:
        log_line("error", "No active render data")
        return False
    
    # Set path
    rdata[c4d.RDATA_PATH] = path
    
    # Set format based on name
    if format.upper() in ["JPEG", "JPG"]:
        rdata[c4d.RDATA_FORMAT] = c4d.FILTER_JPG
        log_line("info", f"Set output: JPEG to {path}")
    elif format.upper() == "PNG":
        rdata[c4d.RDATA_FORMAT] = c4d.FILTER_PNG
        log_line("info", f"Set output: PNG to {path}")
    elif format.upper() == "TIF" or format.upper() == "TIFF":
        rdata[c4d.RDATA_FORMAT] = c4d.FILTER_TIF
        log_line("info", f"Set output: TIFF to {path}")
    else:
        log_line("warning", f"Unknown format: {format}, using JPEG")
        rdata[c4d.RDATA_FORMAT] = c4d.FILTER_JPG
    
    return True