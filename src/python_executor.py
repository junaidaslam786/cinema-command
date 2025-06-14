import c4d
import re
from .preferences import load_pref
from .logging import log_line

def run_python_snippet(code: str):
    """
    Safely run a Python snippet inside Cinema 4D
    
    Args:
        code: Python code to execute
    """
    # Check if Python execution is enabled
    if not load_pref("enable_python", False):
        log_line("error", "Python execution disabled. Enable it in CineCommand Settings > Advanced.")
        return False
    
    # Basic safety check
    if not is_safe_code(code):
        log_line("error", "Unsafe Python code detected. Execution blocked.")
        return False
    
    # Add undo support
    code = f"""
import c4d
doc = c4d.documents.GetActiveDocument()
doc.StartUndo()
try:
{indent_code(code)}
    c4d.EventAdd()
except Exception as e:
    print("Error:", str(e))
doc.EndUndo()
"""
    
    # Log the execution
    log_line("python", code)
    
    # Execute the code
    bc = c4d.BaseContainer()
    bc.SetString(c4d.PLUGIN_SCRIPT, code)
    return c4d.CallCommand(1395743516, bc)  # Execute Python command in C4D

def indent_code(code: str, spaces: int = 4):
    """Add indentation to code block"""
    indent = " " * spaces
    return indent + code.replace("\n", f"\n{indent}")

def is_safe_code(code: str) -> bool:
    """
    Basic safety check for Python code
    
    Returns:
        True if code passes safety checks
    """
    # List of potentially dangerous operations
    dangerous_patterns = [
        r"import\s+(os|subprocess|sys|shutil)",
        r"__import__\(\s*['\"]os['\"]",
        r"eval\s*\(",
        r"exec\s*\(",
        r"open\s*\(",
        r"\.system\s*\(",
        r"\.popen\s*\(",
        r"\.unlink\s*\("
    ]
    
    # Check for dangerous patterns
    for pattern in dangerous_patterns:
        if re.search(pattern, code):
            return False
    
    return True