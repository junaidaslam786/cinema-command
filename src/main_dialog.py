import c4d
from c4d.gui import GeDialog
import threading
import time
from .api_handler import call_claude
from .agent import Agent
from .logging import log_line
from .mcp_executor import execute_commands
from .models.response import AIResponse, ProcessResult

class MainDialog(GeDialog):
    # UI element IDs
    PROMPT_TEXT = 1000
    RUN_BUTTON = 1001
    RESULT_TEXT = 1002
    
    def __init__(self):
        super(MainDialog, self).__init__()
        self.agent = Agent()
        self.processing = False
    
    def CreateLayout(self):
        # Instead of SetSize (which doesn't exist), use dialog dimensions
        # self.SetSize(600, 400)  # Remove this line
        
        self.SetTitle("CineCommand")
        
        # Create main layout
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 0, ""):
            return False
        
        # Prompt input (multiline)
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 1, 0, "Prompt"):
            return False
            
        self.AddMultiLineEditText(self.PROMPT_TEXT, c4d.BFH_SCALEFIT | c4d.BFV_TOP, 600, 100)
        
        self.GroupEnd()  # End prompt group
        
        # Result output (multiline)
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 0, "Result"):
            return False
            
        self.AddMultiLineEditText(self.RESULT_TEXT, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 600, 200)
        
        self.GroupEnd()  # End result group
        
        # Button row
        if not self.GroupBegin(0, c4d.BFH_RIGHT, 1, 0, ""):
            return False
            
        self.AddButton(self.RUN_BUTTON, c4d.BFH_RIGHT, name="Run")
        
        self.GroupEnd()  # End button group
        
        self.GroupEnd()  # End main group
        
        return True
        
    def InitValues(self):
        """Initialize dialog values"""
        # Set initial values
        self.SetString(self.RESULT_TEXT, "Enter a prompt and click Run to generate and execute commands.")
        self.SetString(self.PROMPT_TEXT, "")
        return True
    
    def set_busy(self, state):
        """Set the busy state of the dialog"""
        self.processing = state
        
        # Enable/disable the run button based on busy state
        self.Enable(self.RUN_BUTTON, not state)
        
        # Update status text if busy
        if state:
            self.SetString(self.RESULT_TEXT, "Processing...")
        
        # Update the UI immediately
        self.LayoutChanged(self.RESULT_TEXT)
        self.LayoutChanged(self.RUN_BUTTON)
        
    # Modify the process_prompt method to handle completion better

    def process_prompt(self, prompt):
        """Process prompt in a separate thread"""
        try:
            # First check for rule matches
            commands = self.agent.match_prompt(prompt)
            
            if commands:
                result = {
                    "source": "rule",
                    "completion": "Using predefined rule",
                    "commands": commands
                }
            else:
                # No rules matched, call AI
                log_line("info", "No rules matched, calling API")
                api_result = call_claude(prompt)
                
                # Create AI response object
                completion = api_result.get("completion", "")
                
                # Process response for commands
                commands = self.agent.parse_commands_from_ai(completion)
                
                result = {
                    "source": "ai",
                    "completion": completion,
                    "commands": commands
                }
            
            # Execute commands if any
            if result.get("commands"):
                log_line("info", f"Executing {len(result.get('commands'))} commands")
                execute_commands(result.get("commands"))
            
            # Store result for UI update
            self.processing_finished = True
            self.processing_success = True
            self.result = result
            
            # Force a redraw
            c4d.DrawViews() if hasattr(c4d, "DrawViews") else None
                
        except Exception as e:
            log_line("error", f"Error processing prompt: {str(e)}")
            self.processing_finished = True
            self.processing_success = False
            self.error_message = str(e)
            
            # Force a redraw
            c4d.DrawViews() if hasattr(c4d, "DrawViews") else None

    def update_ui_after_processing(self):
        """Update the UI after processing completes - called from main thread"""
        if hasattr(self, 'SetString') and hasattr(self, 'result'):
            # Update result text
            self.SetString(self.RESULT_TEXT, self.result.get("completion", ""))
            # Show processing complete message
            c4d.gui.MessageDialog("Processing complete")
            # Reset UI state
            self.set_busy(False)

    def show_error_ui(self):
        """Show error in UI - called from main thread"""
        if hasattr(self, 'SetString') and hasattr(self, 'error_message'):
            self.SetString(self.RESULT_TEXT, f"Error: {self.error_message}")
            # Reset UI state
            self.set_busy(False)
    
    # Replace the Command method with this synchronous approach:

    def Command(self, id, msg):
        """Handle UI commands"""
        if id == self.RUN_BUTTON:
            # Get the prompt text
            prompt = self.GetString(self.PROMPT_TEXT)
            
            if not prompt:
                c4d.gui.MessageDialog("Please enter a prompt.")
                return True
            
            try:
                # Set busy state for UI
                self.set_busy(True)
                
                # Use Cinema 4D's status bar for progress indication
                c4d.StatusSetText("Processing prompt...")
                c4d.StatusSetBar(10)  # Set to 10%
                
                # First check for rule matches
                commands = self.agent.match_prompt(prompt)
                
                c4d.StatusSetBar(30)  # Update to 30%
                
                if commands:
                    result = {
                        "source": "rule",
                        "completion": "Using predefined rule",
                        "commands": commands
                    }
                else:
                    # No rules matched, call AI
                    c4d.StatusSetText("Calling AI...")
                    log_line("info", "No rules matched, calling API")
                    api_result = call_claude(prompt)
                    
                    # Create AI response object
                    completion = api_result.get("completion", "")
                    
                    c4d.StatusSetBar(60)  # Update to 60%
                    c4d.StatusSetText("Processing AI response...")
                    
                    # Process response for commands
                    commands = self.agent.parse_commands_from_ai(completion)
                    
                    result = {
                        "source": "ai",
                        "completion": completion,
                        "commands": commands
                    }
                
                # Execute commands if any
                if result.get("commands"):
                    c4d.StatusSetBar(80)  # Update to 80%
                    c4d.StatusSetText(f"Executing {len(result.get('commands'))} commands...")
                    log_line("info", f"Executing {len(result.get('commands'))} commands")
                    execute_commands(result.get("commands"))
                
                # Update UI with result
                self.SetString(self.RESULT_TEXT, result.get("completion", ""))
                
                c4d.StatusSetBar(100)  # Complete
                c4d.StatusSetText("Done")
                
            except Exception as e:
                log_line("error", f"Error processing prompt: {str(e)}")
                self.SetString(self.RESULT_TEXT, f"Error: {str(e)}")
            finally:
                # Always reset UI state
                self.set_busy(False)
                c4d.StatusClear()  # Clear the status bar
            
            return True
        
        return False
    # Replace the poll_processing_status method with this alternative approach:

    def poll_processing_status(self):
        """Poll for processing completion and update UI accordingly"""
        # Check if processing is finished
        if hasattr(self, 'processing_finished') and self.processing_finished:
            if self.processing_success:
                # Update result text with completion
                if hasattr(self, 'result'):
                    self.SetString(self.RESULT_TEXT, self.result.get("completion", ""))
                    # Reset UI state
                    self.set_busy(False)
            else:
                # Show error message
                if hasattr(self, 'error_message'):
                    self.SetString(self.RESULT_TEXT, f"Error: {self.error_message}")
                    # Reset UI state
                    self.set_busy(False)
                    
            # Clear flags
            self.processing_finished = False
            return
        
        # Use Cinema 4D's timer mechanism instead
        # (Set a timer and check when it triggers)
        if not hasattr(self, 'timer_id'):
            # Create a timer ID for our polling (12345 is just an example ID)
            self.timer_id = 12345
            c4d.SetTimer(500, self.timer_id)  # Check every 500ms
        
        # Redraw views to refresh the UI
        if hasattr(c4d, "DrawViews"):
            c4d.DrawViews()
            
    def Timer(self, msg):
        """Handle timer messages"""
        # This is automatically called by Cinema 4D when timers trigger
        if hasattr(self, 'processing_finished') and self.processing_finished:
            # Processing is finished, update UI
            if hasattr(self, 'timer_id'):
                c4d.RemoveTimer(self.timer_id)
                del self.timer_id
            
            if self.processing_success:
                # Update result text with completion
                if hasattr(self, 'result'):
                    self.SetString(self.RESULT_TEXT, self.result.get("completion", ""))
            else:
                # Show error message
                if hasattr(self, 'error_message'):
                    self.SetString(self.RESULT_TEXT, f"Error: {self.error_message}")
            
            # Reset UI state
            self.set_busy(False)
            return
        
        return