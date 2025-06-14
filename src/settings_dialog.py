import c4d
import os
from c4d.gui import GeDialog
from .preferences import save_pref, load_pref
from .api_handler import get_available_models
from .agent import Agent
from .logging import log_line
from .api_handler import call_claude  # Import call_claude function
from .mcp_executor import execute_commands  # Import execute_commands function

class SettingsDialog(GeDialog):
    # IDs for the UI elements
    GROUP_TABS = 1000
    TAB_GENERAL = 1001
    TAB_API = 1002
    TAB_LOGGING = 1003
    TAB_ADVANCED = 1004
    
    # General tab
    MODEL_SELECTOR = 2001
    
    # API tab
    API_KEY = 2100
    BTN_TEST_API = 2101
    
    # Logging tab
    LOG_PATH = 2200
    OPEN_LOG = 2201
    CLEAR_LOGS = 2202
    
    # Advanced tab
    RULES_EDITOR = 2300
    RELOAD_RULES = 2301
    PYTHON_ENABLE = 2302
    
    # Dialog buttons
    BTN_OK = 3001
    BTN_CANCEL = 3002
    
    API_TEST_RESULT = 2102  # For displaying API test results
    BTN_SAVE_RULES = 2303   # Save rules button


    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.agent = Agent()
    
    def CreateLayout(self):
        self.SetTitle("CineCommand Settings")

        # Create tab group with improved styling
        if not self.GroupBegin(self.GROUP_TABS, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, 1, 0, ""):
            return False
        
        # Create a better tab navigation system with proper spacing
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT, 4, 0, ""):
            return False
            
        # Get active tab for initialization
        active_tab = load_pref("settings_active_tab", 0)
        
        # Add tab buttons with improved styling and fixed width
        tab_flags = c4d.BFH_LEFT | c4d.BFV_TOP
        tab_names = ["General", "API Key", "Logging", "Advanced"]
        
        # Create tab buttons with consistent width and height
        for i, name in enumerate(tab_names):
            tab_id = self.TAB_GENERAL + i
            
            # Add the button with fixed width (100 pixels) and height (20 pixels)
            self.AddButton(tab_id, tab_flags, 100, 20, name)
            
            # Set initial appearance - highlight active tab
            if i == active_tab:
                # Try to set background color for the active tab
                if hasattr(self, 'SetBgColor'):
                    try:
                        self.SetBgColor(tab_id, c4d.COLOR_CUSTOMGUI_BACKGROUND_SELECTED)
                    except:
                        pass
                
                # Try to set text color for better contrast
                if hasattr(self, 'SetTextColor'):
                    try:
                        self.SetTextColor(tab_id, c4d.COLOR_TEXT_SELECTED)
                    except:
                        pass
        
        self.GroupEnd()  # End tab buttons group
        
        # Add horizontal separator with a bit of padding
        self.AddSeparatorH(c4d.BFH_SCALEFIT)
        
        # Create all tab content (always create all tabs, show/hide as needed)
        self.CreateGeneralTab()
        self.CreateAPITab()
        self.CreateLoggingTab()
        self.CreateAdvancedTab()
        
        # Add space before dialog buttons
        self.AddSeparatorH(c4d.BFH_SCALEFIT)
        
        # Add dialog buttons at bottom
        if not self.GroupBegin(0, c4d.BFH_RIGHT, 2, 0, "", 0):
            return False
            
        self.AddButton(self.BTN_OK, c4d.BFH_RIGHT, name="OK")
        self.AddButton(self.BTN_CANCEL, c4d.BFH_RIGHT, name="Cancel")
        
        self.GroupEnd()  # End buttons group
        self.GroupEnd()  # End main group
        
        # Show the active tab by default
        self.ShowTab(active_tab)
        
        return True
    
    def ShowTab(self, tab_index):
        """Show only the selected tab content"""
        # Hide all tab content first
        for i in range(4):  # We have 4 tabs
            tab_id = self.TAB_GENERAL + i
            self.HideElement(tab_id, tab_index != i)
        
        # Force UI refresh steps for reliable visual updates
        self.LayoutChanged(self.GROUP_TABS)
        c4d.EventAdd()
        
        # Remove or fix the problematic GetInputState call
        # Option 1: Create a proper BaseContainer (preferred approach)
        bc = c4d.BaseContainer()
        c4d.gui.GetInputState(c4d.BFM_INPUT_MOUSE, c4d.BFM_INPUT_CHANNEL, bc)
        
        # Or Option 2: Just remove this line entirely as it's not essential
        # (remove the GetInputState line if the tabs still work without it)
        
        # Only save preference when explicitly changing tabs, not during init
        if hasattr(self, '_initialized') and self._initialized:
            save_pref("settings_active_tab", tab_index)
        
    def CreateGeneralTab(self):
        """Create the General tab content"""
        if not self.GroupBegin(self.TAB_GENERAL, c4d.BFH_SCALEFIT, 1, 0, "General"):
            return False
            
        # Model selection
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, ""):
            return False
            
        self.AddStaticText(0, c4d.BFH_LEFT, name="AI Model:")
        self.AddComboBox(self.MODEL_SELECTOR, c4d.BFH_SCALEFIT)
        
        # Add models to dropdown
        models = get_available_models()
        for i, model in enumerate(models):
            self.AddChild(self.MODEL_SELECTOR, i, f"{model['name']} - {model['description']}")
            
        self.GroupEnd()  # End model selection group
        
        # Add spacer
        self.AddSeparatorH(c4d.BFH_SCALEFIT)
        
        # Add more general settings here
        
        self.GroupEnd()  # End General tab
        return True
    
    def CreateAPITab(self):
        """Create the API tab content with improved layout"""
        if not self.GroupBegin(self.TAB_API, c4d.BFH_SCALEFIT, 1, 0, "API"):
            return False
            
        # Add explanatory text at the top
        self.AddStaticText(0, c4d.BFH_SCALEFIT, name="Enter your Anthropic Claude API key below:")
        self.AddSeparatorH(c4d.BFH_SCALEFIT)
        
        # API Key field with better spacing
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, ""):
            return False
            
        self.AddStaticText(0, c4d.BFH_LEFT, 0, 0, "Claude API Key:")
        # Add the edit field with password masking (show asterisks)
        self.AddEditText(self.API_KEY, c4d.BFH_SCALEFIT, 300, 20)
        self.SetInt32(self.API_KEY, c4d.EDITTEXT_PASSWORD, c4d.EDITTEXT_PASSWORD)
        self.GroupEnd()  # End API key group
        
        # Add spacing
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 10, "")
    
        # Info text with better styling - FIX HERE
        infoText = "Your API key will be stored securely in Cinema 4D's preferences and used for all requests to Claude AI."
        # Fix: Make sure parameters are in the correct order (id, flags, width, height, text)
        info_field = self.AddMultiLineEditText(0, c4d.BFH_SCALEFIT, 300, 30)
        # Then set the text separately
        self.SetString(info_field, infoText)
        # Set read-only by disabling the field
        self.Enable(info_field, False)
        
        # Add spacing
        self.AddStaticText(0, c4d.BFH_SCALEFIT, 0, 10, "")
        
        # Test button with improved styling
        if not self.GroupBegin(0, c4d.BFH_CENTER, 1, 0, ""):
            return False
        
        self.AddButton(self.BTN_TEST_API, c4d.BFH_CENTER, name="Test API Connection")
        
        self.GroupEnd()  # End button group
        
        # Add a result area for API test results
        self.AddStaticText(self.API_TEST_RESULT, c4d.BFH_CENTER, name="")
        
        self.GroupEnd()  # End API tab
        return True
    
    def CreateLoggingTab(self):
        """Create the Logging tab content"""
        if not self.GroupBegin(self.TAB_LOGGING, c4d.BFH_SCALEFIT, 1, 0, "Logging"):
            return False
            
        # Log path info
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, ""):
            return False
            
        self.AddStaticText(0, c4d.BFH_LEFT, name="Log Directory:")
        self.AddStaticText(self.LOG_PATH, c4d.BFH_SCALEFIT, name="")
        
        self.GroupEnd()  # End log path group
        
        # Open logs button
        self.AddButton(self.OPEN_LOG, c4d.BFH_LEFT, name="Open Log Folder")
        
        # Clear logs button
        self.AddButton(self.CLEAR_LOGS, c4d.BFH_LEFT, name="Clear All Logs")
        
        self.GroupEnd()  # End Logging tab
        return True
    
    def CreateAdvancedTab(self):
        """Create the Advanced tab content with better organization"""
        if not self.GroupBegin(self.TAB_ADVANCED, c4d.BFH_SCALEFIT, 1, 0, "Advanced"):
            return False
            
        # Python execution section
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT, 1, 0, "Python Execution"):
            return False
            
        self.AddCheckbox(self.PYTHON_ENABLE, c4d.BFH_LEFT, 0, 0, "Enable advanced Python scripting")
        
        # Warning with improved styling - Fix MultiLineEditText implementation
        warning_text = "Warning: Enabling Python scripting allows the AI to execute arbitrary code.\nOnly enable if you understand the security implications."
        # Create empty text field first
        warning_field = self.AddMultiLineEditText(0, c4d.BFH_SCALEFIT, 300, 40)
        # Then set the text content separately
        self.SetString(warning_field, warning_text)
        # Set it to read-only by disabling it
        self.Enable(warning_field, False)
        
        self.GroupEnd()  # End Python execution section
        
        # Separator
        self.AddSeparatorH(c4d.BFH_SCALEFIT)
        
        # Rules editor section with better organization
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT, 1, 0, "Agent Rules"):
            return False
            
        # Rules introduction - Fix MultiLineEditText implementation
        help_text = "Add rules in JSON format, one per line. Rules define how CineCommand responds to specific prompts."
        # Create empty text field first
        help_field = self.AddMultiLineEditText(0, c4d.BFH_SCALEFIT, 300, 40)
        # Then set the text content separately
        self.SetString(help_field, help_text)
        # Set it to read-only
        self.Enable(help_field, False)
        
        # Rules editor - Add a proper ID and proper sizing
        # Create the editable multiline text field for rules
        rules_field = self.AddMultiLineEditText(self.RULES_EDITOR, c4d.BFH_SCALEFIT|c4d.BFV_SCALEFIT, 300, 250)
        
        # Optional: Set a monospaced font for better code editing
        # Note: This depends on your Cinema 4D version's API support
        if hasattr(self, 'SetFont'):
            try:
                self.SetFont(rules_field, "Courier New", 10)  # Attempt to set a monospace font
            except:
                pass  # Ignore if not supported
        
        # Button row
        if not self.GroupBegin(0, c4d.BFH_SCALEFIT, 2, 0, ""):
            return False
            
        # Save and reload buttons
        self.AddButton(self.BTN_SAVE_RULES, c4d.BFH_LEFT, name="Save Rules")
        self.AddButton(self.RELOAD_RULES, c4d.BFH_RIGHT, name="Reload Default Rules")
        
        self.GroupEnd()  # End button row
        
        self.GroupEnd()  # End rules section
        
        self.GroupEnd()  # End Advanced tab
        return True
    
    def InitValues(self):
        """Initialize all dialog values"""
        # Mark as not initialized yet
        self._initialized = False
        
        # Set API key
        api_key = load_pref("api_key", "")
        if api_key:
            self.SetString(self.API_KEY, api_key)
        
        # Set model dropdown
        model_id = load_pref("model", "claude-3-sonnet-20240229")
        models = get_available_models()
        for i, model in enumerate(models):
            if model["id"] == model_id:
                self.SetInt32(self.MODEL_SELECTOR, i)
                break
        
        # Set log path
        log_path = os.path.expanduser("~/Documents/C4D_AI_Logs")
        self.SetString(self.LOG_PATH, log_path)
        
        # Set Python execution toggle
        self.SetBool(self.PYTHON_ENABLE, load_pref("enable_python", False))
        
        # Load rules into editor
        rules_text = self.load_rules_text()
        self.SetString(self.RULES_EDITOR, rules_text)
        
        # Show active tab
        active_tab = load_pref("settings_active_tab", 0)
        self.ShowTab(active_tab)
        
        # Now we're initialized
        self._initialized = True
        
        return True
    
    def load_rules_text(self):
        """Load the rules text from the file"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, "prefs", "agent_rules.txt")
            
            if os.path.exists(rules_path):
                with open(rules_path, "r", encoding="utf-8") as f:
                    return f.read()
            else:
                return "# Add your rules here, one JSON object per line.\n# Example:\n# {\"prompt_contains\":\"Add a cube\",\"commands\":[{\"action\":\"AddCube\",\"args\":{\"size\":200}}]}"
        except Exception as e:
            return f"# Error loading rules: {str(e)}"
    
    def save_rules_text(self, rules_text):
        """Save the rules text to the file"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_dir, "prefs", "agent_rules.txt")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(rules_path), exist_ok=True)
            
            with open(rules_path, "w", encoding="utf-8") as f:
                f.write(rules_text)
            
            return True
        except Exception as e:
            c4d.gui.MessageDialog(f"Error saving rules: {str(e)}")
            return False
    
    def SaveSettings(self):
        """Save all settings"""
        # API Key
        api_key = self.GetString(self.API_KEY)
        save_pref("api_key", api_key)
        
        # Model
        model_index = self.GetInt32(self.MODEL_SELECTOR)
        models = get_available_models()
        if 0 <= model_index < len(models):
            save_pref("model", models[model_index]["id"])
        
        # Python execution
        enable_python = self.GetBool(self.PYTHON_ENABLE)
        save_pref("enable_python", enable_python)
        
        # Save rules
        rules_text = self.GetString(self.RULES_EDITOR)
        self.save_rules_text(rules_text)
        
        return True
    
    # def Command(self, id, msg):
    #     """Handle UI commands"""
    #     if id == self.RUN_BUTTON:
    #         # Get the prompt text
    #         prompt = self.GetString(self.PROMPT_TEXT)
            
    #         if not prompt:
    #             c4d.gui.MessageDialog("Please enter a prompt.")
    #             return True
            
    #         try:
    #             # Set busy state for UI
    #             self.set_busy(True)
                
    #             # Show progress in status bar - Cinema 4D's recommended way
    #             c4d.StatusSetText("Processing prompt...")
    #             c4d.StatusSetBar(10)  # Set to 10%
                
    #             # First check for rule matches
    #             commands = self.agent.match_prompt(prompt)
                
    #             c4d.StatusSetBar(30)  # Update to 30%
                
    #             if commands:
    #                 result = {
    #                     "source": "rule",
    #                     "completion": "Using predefined rule",
    #                     "commands": commands
    #                 }
    #             else:
    #                 # No rules matched, call AI
    #                 c4d.StatusSetText("Calling AI...")
    #                 log_line("info", "No rules matched, calling API")
    #                 api_result = call_claude(prompt)
                    
    #                 # Create AI response object
    #                 completion = api_result.get("completion", "")
                    
    #                 c4d.StatusSetBar(60)  # Update to 60%
    #                 c4d.StatusSetText("Processing AI response...")
                    
    #                 # Process response for commands
    #                 commands = self.agent.parse_commands_from_ai(completion)
                    
    #                 result = {
    #                     "source": "ai",
    #                     "completion": completion,
    #                     "commands": commands
    #                 }
                
    #             # Execute commands if any
    #             if result.get("commands"):
    #                 c4d.StatusSetBar(80)  # Update to 80%
    #                 c4d.StatusSetText(f"Executing {len(result.get('commands'))} commands...")
    #                 log_line("info", f"Executing {len(result.get('commands'))} commands")
    #                 execute_commands(result.get("commands"))
                
    #             # Update UI with result
    #             self.SetString(self.RESULT_TEXT, result.get("completion", ""))
                
    #             c4d.StatusSetBar(100)  # Complete
    #             c4d.StatusSetText("Done")
                
    #         except Exception as e:
    #             log_line("error", f"Error processing prompt: {str(e)}")
    #             self.SetString(self.RESULT_TEXT, f"Error: {str(e)}")
    #         finally:
    #             # Always reset UI state
    #             self.set_busy(False)
    #             c4d.StatusClear()  # Clear the status bar
            
    #         return True
            
    #     # Handle timer events for polling
    #     elif id == getattr(self, 'timer_id', -1):
    #         # This is called by the timer
    #         if hasattr(self, 'processing_finished') and self.processing_finished:
    #             # Stop the timer
    #             if hasattr(self, 'timer_id'):
    #                 c4d.RemoveTimer(self.timer_id)
    #                 del self.timer_id
                
    #             if self.processing_success:
    #                 # Update result text with completion
    #                 if hasattr(self, 'result'):
    #                     self.SetString(self.RESULT_TEXT, self.result.get("completion", ""))
    #             else:
    #                 # Show error message
    #                 if hasattr(self, 'error_message'):
    #                     self.SetString(self.RESULT_TEXT, f"Error: {self.error_message}")
                
    #             # Reset UI state
    #             self.set_busy(False)
    #             # Force redraw
    #             c4d.DrawViews() if hasattr(c4d, "DrawViews") else None
            
    #         return True
        
    #     return False
    
    def Command(self, id, msg):
        """Handle UI commands"""
        if id in [self.TAB_GENERAL, self.TAB_API, self.TAB_LOGGING, self.TAB_ADVANCED]:
        # Calculate tab index (0-3) by subtracting the base tab ID
            tab_index = id - self.TAB_GENERAL
            self.ShowTab(tab_index)
            
            # Add visual feedback for the selected tab
            for i in range(4):
                tab_id = self.TAB_GENERAL + i
                # Highlight the selected tab button
                if hasattr(self, 'SetBgColor'):
                    try:
                        if i == tab_index:
                            self.SetBgColor(tab_id, c4d.COLOR_CUSTOMGUI_BACKGROUND_SELECTED)
                        else:
                            self.SetBgColor(tab_id, c4d.COLOR_CUSTOMGUI_BACKGROUND)
                    except:
                        pass  # Ignore if not supported
            
            return True
        
        elif id == self.BTN_TEST_API:
            # Test the API connection
            self.test_api_connection()
            return True
            
        elif id == self.BTN_OK:
            # Save settings and close dialog
            self.SaveSettings()
            self.Close()
            return True
            
        elif id == self.BTN_CANCEL:
            # Close dialog without saving
            self.Close()
            return True
            
            
        elif id == self.OPEN_LOG:
            # Open log folder
            self.open_log_folder()
            return True
            
        elif id == self.CLEAR_LOGS:
            # Clear log files
            self.clear_log_files()
            return True
            
        elif id == self.BTN_SAVE_RULES:
            # Save rules
            rules_text = self.GetString(self.RULES_EDITOR)
            if self.save_rules_text(rules_text):
                c4d.gui.MessageDialog("Rules saved successfully.")
            return True
            
        elif id == self.RELOAD_RULES:
            # Reload default rules
            if c4d.gui.QuestionDialog("This will reset all rules to default. Continue?"):
                # Reset to default rules
                rules_text = self.load_rules_text()
                self.SetString(self.RULES_EDITOR, rules_text)
            return True
        
        return False
    
    def test_api_connection(self):
        """Test the API connection with visual feedback"""
        api_key = self.GetString(self.API_KEY)
        save_pref("api_key", api_key)
        
        # Update UI to show testing state
        self.SetString(self.API_TEST_RESULT, "Testing connection...")
        self.Enable(self.BTN_TEST_API, False)
        c4d.gui.GetInputState(c4d.BFM_INPUT_MOUSE, c4d.BFM_INPUT_CHANNEL, None)  # Force UI update
        
        # Test connection
        from .api_handler import test_api
        try:
            # Basic validation
            if not api_key or len(api_key) < 10:
                self.SetString(self.API_TEST_RESULT, "⚠️ Please enter a valid API key")
                self.Enable(self.BTN_TEST_API, True)
                return False
                
            # Test API connection
            success, message = test_api(api_key)
            
            if success:
                self.SetString(self.API_TEST_RESULT, "✅ API connection successful!")
            else:
                self.SetString(self.API_TEST_RESULT, f"❌ Connection failed: {message}")
        except Exception as e:
            self.SetString(self.API_TEST_RESULT, f"❌ Error: {str(e)}")
        
        # Re-enable test button
        self.Enable(self.BTN_TEST_API, True)
        return True
    
    def open_log_folder(self):
        """Open the log folder in file explorer"""
        log_path = os.path.expanduser("~/Documents/C4D_AI_Logs")
        os.makedirs(log_path, exist_ok=True)
        
        try:
            # Open folder in file explorer
            if os.name == 'nt':  # Windows
                os.startfile(log_path)
            else:  # macOS or Linux
                import subprocess
                subprocess.Popen(['open', log_path])
        except Exception as e:
            c4d.gui.MessageDialog(f"Could not open log folder: {str(e)}")

    def clear_log_files(self):
        """Delete all log files"""
        log_path = os.path.expanduser("~/Documents/C4D_AI_Logs")
        if not os.path.exists(log_path):
            return
            
        try:
            count = 0
            for file in os.listdir(log_path):
                if file.startswith("cinecommand_") and file.endswith(".log"):
                    os.remove(os.path.join(log_path, file))
                    count += 1
            
            c4d.gui.MessageDialog(f"Successfully deleted {count} log file(s).")
        except Exception as e:
            c4d.gui.MessageDialog(f"Error deleting log files: {str(e)}")