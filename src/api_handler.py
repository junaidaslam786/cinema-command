import json
import os

# Try to import requests, fall back to urllib
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    import urllib.request
    import urllib.error
    REQUESTS_AVAILABLE = False
    from .logging import log_line
    log_line("warning", "Using fallback HTTP client (urllib) - functionality may be limited")

from .logging import log_line
from .preferences import load_pref


def get_api_key() -> str:
    """Get API key from preferences"""
    return load_pref("claude_api_key", "")


def get_command_system_prompt():
    """Get system prompt optimized for command generation"""
    return """You are CineCommand, a Cinema 4D automation assistant.
    
    When asked to create or modify 3D content, ALWAYS respond with valid JSON commands.
    
    FORMAT YOUR RESPONSE AS:
    {
      "action": "ActionName",
      "args": {
        "param1": value1,
        "param2": value2
      }
    }
    
    Available commands:
    - AddCube: {"size": 100, "position": [0,0,0], "name": "MyCube"}
    - AddSphere: {"diameter": 100, "position": [0,0,0], "name": "MySphere"}
    - CreateMaterial: {"name": "Material1", "type": "standard", "color": [r,g,b]}
    - ApplyMaterial: {"name": "Material1", "to": "ObjectName"}
    - SelectObject: {"name": "ObjectName"}
    - AddLight: {"type": "point", "position": [0,0,0], "name": "MyLight"}
    - AddCamera: {"focal_length": 35, "position": [0,0,0], "name": "MyCamera"}
    - GroupSelected: {"name": "MyGroup"}
    - AddSpline: {"type": "circle", "radius": 100}
    - SetRenderResolution: {"width": 1920, "height": 1080, "fps": 30}
    
    For a red cube, use:
    {"action": "AddCube", "args": {"size": 100, "name": "RedCube"}}
    {"action": "CreateMaterial", "args": {"name": "Red", "color": [1,0,0]}}
    {"action": "ApplyMaterial", "args": {"name": "Red", "to": "RedCube"}}
    
    ONLY return JSON commands, no other text or explanations.
    """


def call_claude(prompt: str, system_prompt: str = None, model: str = None) -> dict:
    """
    Call Claude API with the given prompt
    
    Args:
        prompt: The prompt to send to Claude
        system_prompt: Optional system prompt to guide Claude's behavior
        model: Model ID to use (will default to preference setting if not provided)
        
    Returns:
        Response dictionary from Claude
    """
    # Get API key from preferences
    api_key = get_api_key()
    
    if not api_key:
        log_line("error", "No Claude API key provided. Check Settings.")
        raise ValueError("Missing API key. Please configure it in Settings.")
    
    # Use specified model or get from preferences
    if not model:
        model = load_pref("model", "claude-3-opus-20240229")  # Updated to correct model ID
    
    # If no system prompt is provided, use the default command system prompt
    if system_prompt is None:
        system_prompt = get_command_system_prompt()
    
    # API URL - The correct Anthropic Messages API endpoint
    url = "https://api.anthropic.com/v1/messages"
    
    # Set up headers with API key
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Construct request payload according to Anthropic's API spec
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000
    }
    
    # Add system prompt if provided
    if system_prompt:
        payload["system"] = system_prompt
    
    log_line("info", f"Calling Claude API with model {model}")
    log_line("debug", f"Request URL: {url}")
    log_line("debug", f"Request Headers: {json.dumps({k: '***' if k == 'x-api-key' else v for k, v in headers.items()})}")
    log_line("debug", f"Request Body: {json.dumps(payload)}")
    
    try:
        if REQUESTS_AVAILABLE:
            # Make the request using requests library
            response = requests.post(url, json=payload, headers=headers)
            
            # Log detailed error information for debugging
            if response.status_code != 200:
                log_line("error", f"API error: {response.status_code} - {response.text}")
                raise Exception(f"{response.status_code} - {response.text}")
                
            response.raise_for_status()  # Raise exception for HTTP errors
            
            # Get response JSON and log the full response
            response_json = response.json()
            log_line("debug", f"Full API response: {json.dumps(response_json)}")
            
            return response_json
        else:
            # Fallback to urllib
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req) as response:
                    response_data = response.read().decode("utf-8")
                    
                    # Log the full response data
                    log_line("debug", f"Full API response: {response_data}")
                    
                    response_json = json.loads(response_data)
                    return response_json
            except urllib.error.HTTPError as e:
                # Log more detailed error information
                error_message = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                log_line("error", f"API error: {e.code} - {error_message}")
                raise Exception(f"HTTP Error {e.code}: {error_message}")
                
    except Exception as e:
        log_line("error", f"API call failed: {str(e)}")
        raise


def get_available_models():
    """Get available Claude models for the settings dropdown"""
    # Updated to only include Claude 4 models as requested
    return [
        {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "description": "Most powerful, highest quality"},
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "description": "Balanced speed & intelligence"}
    ]


def test_api(api_key):
    """
    Test if the API key is valid
    
    Args:
        api_key: The API key to test
        
    Returns:
        Tuple of (success, message)
    """
    url = "https://api.anthropic.com/v1/messages"
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Minimal request to check if API key is valid
    data = {
        "model": "claude-4-sonnet-20240229",  # Updated to Claude 4
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    
    try:
        if REQUESTS_AVAILABLE:
            # Use requests library if available
            resp = requests.post(url, json=data, headers=headers)
            
            if resp.status_code == 200:
                return True, "API key is valid"
            elif resp.status_code == 401:
                return False, "Invalid API key"
            else:
                return False, f"API error: {resp.status_code} - {resp.text}"
        else:
            # Fallback to urllib if requests not available
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
            
            try:
                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        return True, "API key is valid"
                    else:
                        return False, f"API error: {response.status} - {response.read().decode('utf-8')}"
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    return False, "Invalid API key"
                else:
                    return False, f"API error: {e.code} - {e.reason}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"


def extract_text_from_claude_response(response):
    """Extract the text from Claude's response with detailed logging"""
    log_line("debug", "=== extract_text_from_claude_response called ===")
    
    try:
        log_line("debug", f"Response type: {type(response)}")
        log_line("debug", f"Response keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        
        # For the Messages API
        if "content" in response and isinstance(response["content"], list):
            log_line("debug", f"Found content array with {len(response['content'])} items")
            
            # Get text from content blocks
            text_blocks = []
            for i, block in enumerate(response["content"]):
                log_line("debug", f"Content block {i}: type={block.get('type')}, keys={list(block.keys())}")
                if block.get("type") == "text":
                    text_blocks.append(block["text"])
            
            text = "\n".join(text_blocks)
            log_line("debug", f"=== EXTRACTED TEXT (length {len(text)}): {repr(text)} ===")
            return text
        
        else:
            log_line("error", f"Unexpected response format - no content array found")
            return ""
            
    except Exception as e:
        log_line("error", f"Error extracting text from response: {str(e)}")
        import traceback
        log_line("error", f"Traceback: {traceback.format_exc()}")
        return ""


def extract_commands_from_text(text):
    """Extract commands from Claude's text response with extensive debugging"""
    log_line("debug", "=== extract_commands_from_text called ===")
    log_line("debug", f"Input text type: {type(text)}")
    log_line("debug", f"Input text length: {len(text) if text else 0}")
    log_line("debug", f"Input text repr: {repr(text)}")
    
    if not text:
        log_line("error", "No text provided to extract_commands_from_text")
        return []
    
    commands = []
    text = text.strip()
    
    # Split by double newlines
    blocks = text.split('\n\n')
    log_line("debug", f"Split into {len(blocks)} blocks")
    
    for i, block in enumerate(blocks):
        block = block.strip()
        if not block:
            continue
            
        log_line("debug", f"Processing block {i+1}: {repr(block)}")
        
        try:
            cmd = json.loads(block)
            log_line("debug", f"Block {i+1} parsed as JSON: {cmd}")
            
            if isinstance(cmd, dict) and "action" in cmd:
                commands.append(cmd)
                log_line("debug", f"✓ Added command: {cmd['action']}")
            else:
                log_line("debug", f"✗ JSON object but no 'action' field: {cmd}")
                
        except json.JSONDecodeError as e:
            log_line("debug", f"✗ Block {i+1} JSON parse failed: {str(e)}")
    
    log_line("debug", f"=== FINAL RESULT: {len(commands)} commands extracted ===")
    return commands