from typing import Dict, Any, List, Optional, Union

class Command:
    """
    Represents a command to be executed by the MCP system
    """
    def __init__(self, action: str, args: Optional[Dict[str, Any]] = None):
        self.action = action
        self.args = args or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "action": self.action,
            "args": self.args
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Command':
        """Create a Command from dictionary"""
        return cls(
            action=data.get("action", ""),
            args=data.get("args", {})
        )
    
    def __str__(self) -> str:
        """String representation of command"""
        args_str = ", ".join(f"{k}={v}" for k, v in self.args.items())
        return f"{self.action}({args_str})"

class CommandGroup:
    """
    Represents a group of commands to be executed together
    """
    def __init__(self, name: str = "", commands: Optional[List[Command]] = None):
        self.name = name
        self.commands = commands or []
    
    def add_command(self, command: Command) -> None:
        """Add a command to the group"""
        self.commands.append(command)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "commands": [cmd.to_dict() for cmd in self.commands]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandGroup':
        """Create a CommandGroup from dictionary"""
        commands = []
        for cmd_data in data.get("commands", []):
            commands.append(Command.from_dict(cmd_data))
        
        return cls(
            name=data.get("name", ""),
            commands=commands
        )
    
    def __str__(self) -> str:
        """String representation of command group"""
        cmds = "\n  ".join(str(cmd) for cmd in self.commands)
        return f"CommandGroup '{self.name}':\n  {cmds}"

class Rule:
    """
    Represents a rule that maps prompts to commands
    """
    def __init__(self, prompt_contains: str = "", 
                 commands: Optional[List[Dict[str, Any]]] = None,
                 description: str = ""):
        self.prompt_contains = prompt_contains
        self.commands = commands or []
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "prompt_contains": self.prompt_contains,
            "commands": self.commands,
            "description": self.description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Rule':
        """Create a Rule from dictionary"""
        return cls(
            prompt_contains=data.get("prompt_contains", ""),
            commands=data.get("commands", []),
            description=data.get("description", "")
        )
    
    def __str__(self) -> str:
        """String representation of rule"""
        return f"Rule '{self.prompt_contains}': {len(self.commands)} commands"