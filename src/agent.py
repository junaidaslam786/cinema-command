import os
import json
import re
from typing import List, Dict, Optional
from .logging import log_line

class Agent:
    """
    Agent that processes prompts and extracts commands
    """
    def __init__(self):
        self.rules = []
        self.load_rules()
    
    def load_rules(self):
        """Load rules from the rules file"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, "prefs", "agent_rules.txt")
            
            if not os.path.exists(rules_path):
                log_line("warning", f"Rules file not found: {rules_path}")
                return
            
            with open(rules_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            rules = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                try:
                    rule = json.loads(line)
                    rules.append(rule)
                except json.JSONDecodeError:
                    log_line("error", f"Invalid rule format: {line}")
            
            self.rules = rules
            log_line("info", f"Loaded {len(rules)} rules")
        
        except Exception as e:
            log_line("error", f"Error loading rules: {str(e)}")
    
    def match_prompt(self, prompt: str) -> Optional[List[Dict]]:
        """Check if any rules match the prompt"""
        if not prompt or not self.rules:
            return None
        
        prompt_lower = prompt.lower()
        
        for rule in self.rules:
            pattern = rule.get("prompt_contains", "").lower()
            if pattern and pattern in prompt_lower:
                log_line("info", f"Rule matched: {pattern}")
                return rule.get("commands", [])
        
        return None
    
    def process_prompt(self, prompt: str):
        """Process a prompt and return commands"""
        # First check for rule matches
        commands = self.match_prompt(prompt)
        if commands:
            return {
                "source": "rule",
                "completion": f"Executing predefined rule",
                "commands": commands
            }
        
        # Otherwise call AI
        from .api_handler import call_claude
        response = call_claude(prompt)
        
        # Extract commands from response
        commands = self.parse_commands_from_ai(response.get("completion", ""))
        
        return {
            "source": "ai",
            "completion": response.get("completion", ""),
            "commands": commands
        }
    
    def parse_commands_from_ai(self, completion: str) -> List[Dict]:
        """Extract commands from AI response"""
        # Basic command extraction logic
        commands = []
        
        # Look for patterns like "AddCube(size=200, name='Cube')"
        command_pattern = r'(\w+)\s*\(([^)]+)\)'
        matches = re.findall(command_pattern, completion)
        
        for action, args_str in matches:
            args = self.parse_command_args(action, args_str)
            commands.append({
                "action": action,
                "args": args
            })
        
        # Fallback to more basic pattern matching if no commands found
        if not commands:
            commands = self.extract_commands(completion)
        
        return commands
    
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