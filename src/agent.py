

import os
import json
import re
from typing import List, Dict, Optional
from .logging import log_line
from .api_handler import call_claude, extract_commands_from_text, extract_text_from_claude_response
from .preferences import load_pref, save_pref


# Add this to the top of your agent.py file for testing
def test_command_extraction():
    """Test function to verify command extraction works"""
    from .api_handler import extract_commands_from_text
    
    test_text = '''{\n  "action": "AddCube",\n  "args": {\n    "size": 100,\n    "position": [0, 0, 0],\n    "name": "RedCube"\n  }\n}\n\n{\n  "action": "CreateMaterial",\n  "args": {\n    "name": "Red",\n    "type": "standard",\n    "color": [1, 0, 0]\n  }\n}'''
    
    log_line("debug", "=== TESTING COMMAND EXTRACTION ===")
    commands = extract_commands_from_text(test_text)
    log_line("debug", f"Test result: {len(commands)} commands")
    
    return commands

# Call this test when the plugin loads
test_result = test_command_extraction()
log_line("info", f"Command extraction test: {len(test_result)} commands extracted")

# System prompt optimized for command generation
SYSTEM_PROMPT = """
You are an AI assistant for Cinema 4D. When asked to create or modify 3D content, respond with specific commands.
Always format your commands as JSON objects with 'action' and 'args' fields.

Example command format:
{
  "action": "AddCube", 
  "args": {"size": 100, "position": [0,0,0]}
}

Available commands:
- AddCube: Creates a cube primitive (args: size, position, name)
- AddSphere: Creates a sphere primitive (args: diameter, position, name)
- CreateMaterial: Creates a new material (args: name, type, color)
- ApplyMaterial: Applies material to object (args: name, to)
- SelectObject: Selects an object by name (args: name)
- Duplicate: Duplicates selected objects (args: count, axis, distance)
- GroupSelected: Groups selected objects (args: name)
- AddSpline: Creates a spline (args: type, radius, plane)
- AddCamera: Creates a camera (args: focal_length, name)
- FrameAll: Frames all objects in view
- SetRenderResolution: Sets render resolution (args: width, height, fps)

Respond ONLY with commands to fulfill the user's request. Do not include explanations.
"""

class Agent:
    def __init__(self):
        """Initialize the agent"""
        self.rules = []
        self.reload_rules()
    
    def reload_rules(self):
        """Load rules from file with proper comment handling"""
        try:
            import os
            import json
            
            # Get plugin directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            # Load rules from prefs directory
            rules_path = os.path.join(base_dir, "prefs", "agent_rules.txt")
            
            rules = []
            if os.path.exists(rules_path):
                with open(rules_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f:
                        line = line.strip()
                        # Skip empty lines and lines starting with '#' (comments)
                        if not line or line.startswith('#'):
                            continue
                        try:
                            rule = json.loads(line)
                            rules.append(rule)
                        except json.JSONDecodeError:
                            log_line("warning", f"Invalid rule: {line}")
            
            self.rules = rules
            log_line("info", f"Loaded {len(rules)} rules")
            
            return True
        except Exception as e:
            log_line("error", f"Error loading rules: {str(e)}")
            return False
    
    
    def match_prompt(self, prompt: str) -> List[Dict]:
        """Check if prompt matches any rule and return commands if it does"""
        # Check if rules are disabled in settings
        use_rules = load_pref("use_rules", True)
        if not use_rules:
            log_line("info", "Rules disabled in settings, skipping rule matching")
            return []
            
        for rule in self.rules:
            if "prompt_contains" in rule and rule["prompt_contains"].lower() in prompt.lower():
                log_line("info", f"Rule matched: {rule['prompt_contains']}")
                return rule.get("commands", [])
        
        return []
    
    def process_prompt(self, prompt: str):
        """Process a prompt and return commands with forced function calls"""
        log_line("debug", f"=== process_prompt called with: {prompt} ===")
        
        try:
            # Check for rule matches first
            commands = self.match_prompt(prompt)
            
            if commands:
                log_line("info", f"Rule matched, executing {len(commands)} commands")
                return {
                    "source": "rule",
                    "completion": "Executing predefined rule",
                    "commands": commands
                }
            
            # If no rule matched, call Claude API
            log_line("info", "No rules matched, calling API")
            
            # Import and force use of our corrected functions
            from .api_handler import call_claude, extract_text_from_claude_response, extract_commands_from_text, get_command_system_prompt
            log_line("debug", "Successfully imported API handler functions")
            
            # Get system prompt
            system_prompt = get_command_system_prompt()
            
            # Call the API
            response = call_claude(prompt, system_prompt=system_prompt)
            log_line("debug", "=== API call completed ===")
            
            # FORCE our text extraction function
            log_line("debug", "=== Starting FORCED text extraction ===")
            text = extract_text_from_claude_response(response)
            log_line("debug", f"=== FORCED text extraction result: {len(text) if text else 0} chars ===")
            
            # FORCE our command extraction function
            log_line("debug", "=== Starting FORCED command extraction ===")
            commands = extract_commands_from_text(text)
            log_line("debug", f"=== FORCED command extraction result: {len(commands)} commands ===")
            
            # Override any other parsing that might happen
            if commands:
                log_line("info", f"SUCCESSFULLY extracted {len(commands)} commands using corrected functions")
            else:
                log_line("error", "FAILED to extract commands even with corrected functions")
            
            return {
                "source": "ai",
                "completion": text,
                "commands": commands
            }
            
        except Exception as e:
            log_line("error", f"Error in process_prompt: {str(e)}")
            import traceback
            log_line("error", f"Full traceback: {traceback.format_exc()}")
            return {
                "source": "error",
                "completion": f"Error: {str(e)}",
                "commands": []
            }
    
    def parse_commands_from_ai(self, completion: str) -> List[Dict]:
        """Parse commands from AI completion text - Fixed version"""
        try:
            log_line("debug", f"=== parse_commands_from_ai called with completion length: {len(completion)} ===")
            log_line("debug", f"Completion text: {repr(completion)}")
            
            import re
            import json
            
            commands = []
            
            # Method 1: Split by double newlines (how Claude formats multiple commands)
            blocks = completion.split('\n\n')
            log_line("debug", f"Split completion into {len(blocks)} blocks")
            
            for i, block in enumerate(blocks):
                block = block.strip()
                if not block:
                    continue
                    
                log_line("debug", f"Processing block {i+1}: {repr(block[:100])}")
                
                # Try to parse this block as JSON
                try:
                    cmd = json.loads(block)
                    if isinstance(cmd, dict) and "action" in cmd:
                        commands.append(cmd)
                        log_line("debug", f"✓ Block {i+1} parsed as command: {cmd['action']}")
                    else:
                        log_line("debug", f"✗ Block {i+1} is JSON but missing 'action': {cmd}")
                except json.JSONDecodeError as e:
                    log_line("debug", f"✗ Block {i+1} is not valid JSON: {str(e)}")
            
            # Method 2: Look for commands inside code blocks (```json ... ```) - your original logic
            if not commands:
                log_line("debug", "No commands found in blocks, trying code block extraction")
                code_blocks = re.findall(r'```(?:json)?\s*\n(.*?)\n```', completion, re.DOTALL)
                log_line("debug", f"Found {len(code_blocks)} code blocks")
                
                for block in code_blocks:
                    try:
                        # Try to parse as JSON array
                        if block.strip().startswith('['):
                            cmd_list = json.loads(block)
                            for cmd in cmd_list:
                                if isinstance(cmd, dict) and 'action' in cmd:
                                    commands.append(cmd)
                                    log_line("debug", f"✓ Code block array command: {cmd['action']}")
                        
                        # Try to parse as JSON object
                        elif block.strip().startswith('{'):
                            cmd = json.loads(block)
                            if 'action' in cmd:
                                commands.append(cmd)
                                log_line("debug", f"✓ Code block object command: {cmd['action']}")
                    except Exception as e:
                        log_line("debug", f"✗ Code block parse failed: {str(e)}")
                        continue
            
            # Method 3: Regex extraction as fallback
            if not commands:
                log_line("debug", "No commands found in code blocks, trying regex extraction")
                # Find JSON objects that contain "action"
                pattern = r'\{[^{}]*"action"[^{}]*\}'
                matches = re.findall(pattern, completion, re.DOTALL)
                log_line("debug", f"Regex found {len(matches)} potential JSON objects")
                
                for match in matches:
                    try:
                        cmd = json.loads(match)
                        if isinstance(cmd, dict) and "action" in cmd:
                            commands.append(cmd)
                            log_line("debug", f"✓ Regex extracted command: {cmd['action']}")
                    except:
                        continue
            
            # Method 4: Natural language fallback (your original logic)
            if not commands:
                log_line("debug", "No JSON commands found, trying natural language parsing")
                actions = {
                    r'(?:create|add|make)\s+a\s+(?:red\s+)?cube': {'action': 'AddCube', 'args': {'size': 100, 'name': 'Cube'}},
                    r'(?:create|add|make)\s+a\s+sphere': {'action': 'AddSphere', 'args': {'diameter': 100}},
                    r'(?:create|add|make)\s+a\s+camera': {'action': 'AddCamera', 'args': {}},
                    r'(?:create|add|make)\s+a\s+light': {'action': 'AddLight', 'args': {'type': 'point'}},
                    r'(?:create|add|make)\s+a\s+material': {'action': 'CreateMaterial', 'args': {'name': 'NewMaterial'}}
                }
                
                for pattern, cmd in actions.items():
                    if re.search(pattern, completion, re.IGNORECASE):
                        commands.append(cmd)
                        log_line("debug", f"✓ Natural language command: {cmd['action']}")
            
            # Final results
            if commands:
                log_line("info", f"Successfully parsed {len(commands)} commands from AI text")
                for i, cmd in enumerate(commands, 1):
                    log_line("debug", f"Final command {i}: {json.dumps(cmd)}")
            else:
                log_line("error", "FAILED to parse any commands from AI text")
                log_line("debug", f"Full completion text: {repr(completion)}")
            
            return commands
            
        except Exception as e:
            log_line("error", f"Error parsing commands from AI: {str(e)}")
            import traceback
            log_line("error", f"Traceback: {traceback.format_exc()}")
            return []
    
    def parse_command_args(self, action: str, args_str: str) -> Dict:
        """Parse command arguments from string"""
        # Choose the appropriate parser based on action
        if action in ["AddCube", "AddSphere"]:
            return self.parse_primitive_args(action, args_str)
        elif action in ["CreateMaterial"]:
            return self.parse_material_args(args_str)
        elif action in ["Duplicate"]:
            return self.parse_duplicate_args(args_str)
        else:
            # Generic argument parser
            args = {}
            pairs = args_str.split(",")
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to parse values to appropriate types
                    try:
                        if value.startswith("'") or value.startswith('"'):
                            # String
                            args[key] = value.strip("'\"")
                        elif value.lower() == "true":
                            args[key] = True
                        elif value.lower() == "false":
                            args[key] = False
                        else:
                            # Try number
                            args[key] = float(value) if "." in value else int(value)
                    except:
                        args[key] = value
                        
            return args
    
    def parse_primitive_args(self, action: str, args_str: str) -> Dict:
        """Parse arguments for primitive objects"""
        args = self.parse_command_args("", args_str)
        
        # Add defaults for primitives if needed
        if "size" not in args and "radius" not in args:
            if action == "AddCube":
                args["size"] = 200
            elif action == "AddSphere":
                args["radius"] = 100
                
        return args
    
    def parse_material_args(self, args_str: str) -> Dict:
        """Parse arguments for materials"""
        args = self.parse_command_args("", args_str)
        
        # Parse color if specified
        if "color" in args and isinstance(args["color"], str):
            # Try to parse color string like [1,0,0]
            match = re.search(r'\[([\d\.,\s]+)\]', args["color"])
            if match:
                try:
                    color_str = match.group(1)
                    args["color"] = [float(x) for x in color_str.split(",")]
                except:
                    pass
        
        # Add defaults
        if "name" not in args:
            args["name"] = "NewMaterial"
            
        if "color" not in args:
            args["color"] = [1, 1, 1]  # White
            
        return args
    
    def parse_duplicate_args(self, args_str: str) -> Dict:
        """Parse arguments for duplication"""
        args = self.parse_command_args("", args_str)
        
        # Add defaults
        if "count" not in args:
            args["count"] = 1
            
        if "axis" not in args:
            args["axis"] = "X"
            
        if "distance" not in args:
            args["distance"] = 100
            
        return args
    
    def extract_commands(self, completion: str) -> List[Dict]:
        """
        Extract commands from text using pattern matching
        Used as a fallback when parse_commands_from_ai doesn't find explicit commands
        """
        commands = []
        
        # Patterns to look for in the text
        patterns = [
            (r"add(?:ing|ed)?\s+(?:a|the)?\s+cube", "AddCube", {"size": 200}),
            (r"add(?:ing|ed)?\s+(?:a|the)?\s+sphere", "AddSphere", {"radius": 100}),
            (r"creat(?:e|ing|ed)\s+(?:a|the)?\s+material", "CreateMaterial", {"name": "NewMaterial"}),
            (r"apply(?:ing|ed)?\s+(?:a|the)?\s+material", "ApplyMaterial", {}),
            (r"add(?:ing|ed)?\s+(?:a|the)?\s+camera", "AddCamera", {}),
            (r"duplicate", "Duplicate", {"count": 1}),
            (r"group(?:ing|ed)?", "GroupSelected", {"name": "Group"})
        ]
        
        for pattern, command, default_args in patterns:
            if re.search(pattern, completion, re.IGNORECASE):
                # Simple command extraction
                commands.append({
                    "action": command,
                    "args": default_args.copy()
                })
        
        log_line("info", f"Extracted {len(commands)} commands from text")
        return commands