from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from .command import Command, CommandGroup

class AIResponse:
    """
    Represents a response from an AI model
    """
    def __init__(self, prompt: str = "", 
                 completion: str = "",
                 model: str = "",
                 timestamp: Optional[datetime] = None,
                 commands: Optional[List[Dict[str, Any]]] = None):
        self.prompt = prompt
        self.completion = completion
        self.model = model
        self.timestamp = timestamp or datetime.now()
        self.commands = commands or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "prompt": self.prompt,
            "completion": self.completion,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "commands": self.commands
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIResponse':
        """Create an AIResponse from dictionary"""
        timestamp = None
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except ValueError:
                pass
        
        return cls(
            prompt=data.get("prompt", ""),
            completion=data.get("completion", ""),
            model=data.get("model", ""),
            timestamp=timestamp,
            commands=data.get("commands", [])
        )
    
    def __str__(self) -> str:
        """String representation of AI response"""
        return f"AIResponse: {self.model} ({self.timestamp.strftime('%Y-%m-%d %H:%M:%S')})"

class RuleResponse:
    """
    Represents a response from a rule match
    """
    def __init__(self, rule: str = "",
                 prompt: str = "",
                 commands: Optional[List[Dict[str, Any]]] = None):
        self.rule = rule
        self.prompt = prompt
        self.commands = commands or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "rule": self.rule,
            "prompt": self.prompt,
            "commands": self.commands
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RuleResponse':
        """Create a RuleResponse from dictionary"""
        return cls(
            rule=data.get("rule", ""),
            prompt=data.get("prompt", ""),
            commands=data.get("commands", [])
        )
    
    def __str__(self) -> str:
        """String representation of rule response"""
        return f"RuleResponse: {self.rule} ({len(self.commands)} commands)"

class ProcessResult:
    """
    Represents the result of processing a prompt
    """
    def __init__(self, source: str = "ai",
                 completion: str = "",
                 commands: Optional[List[Dict[str, Any]]] = None):
        self.source = source  # 'ai' or 'rule'
        self.completion = completion
        self.commands = commands or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "source": self.source,
            "completion": self.completion,
            "commands": self.commands
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessResult':
        """Create a ProcessResult from dictionary"""
        return cls(
            source=data.get("source", "ai"),
            completion=data.get("completion", ""),
            commands=data.get("commands", [])
        )
    
    def __str__(self) -> str:
        """String representation of process result"""
        return f"ProcessResult: {self.source} ({len(self.commands)} commands)"

class SessionLog:
    """
    Represents a log of a session with user prompts and AI responses
    """
    def __init__(self):
        self.entries = []
        self.start_time = datetime.now()
        self.end_time = None
    
    def add_user_prompt(self, prompt: str) -> None:
        """Log a user prompt"""
        self.entries.append({
            "type": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_ai_response(self, response: AIResponse) -> None:
        """Log an AI response"""
        self.entries.append({
            "type": "ai",
            "content": response.completion,
            "commands": response.commands,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_action(self, commands: List[Dict[str, Any]]) -> None:
        """Log executed commands"""
        self.entries.append({
            "type": "action",
            "commands": commands,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_error(self, error: str) -> None:
        """Log an error"""
        self.entries.append({
            "type": "error",
            "content": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def end_session(self) -> None:
        """End the session and record end time"""
        self.end_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "entries": self.entries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionLog':
        """Create a SessionLog from dictionary"""
        session = cls()
        
        if "start_time" in data:
            try:
                session.start_time = datetime.fromisoformat(data["start_time"])
            except ValueError:
                pass
        
        if "end_time" in data and data["end_time"]:
            try:
                session.end_time = datetime.fromisoformat(data["end_time"])
            except ValueError:
                pass
        
        session.entries = data.get("entries", [])
        return session
    
    def __str__(self) -> str:
        """String representation of session log"""
        duration = ""
        if self.end_time:
            duration = f", duration: {(self.end_time - self.start_time).total_seconds():.1f}s"
        
        return f"SessionLog: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}{duration}, {len(self.entries)} entries"