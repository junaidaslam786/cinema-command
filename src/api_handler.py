import os
from .logging import log_line
from .preferences import load_pref

# Try to import requests, fall back to urlib
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    import urllib.request
    import urllib.error
    import json
    REQUESTS_AVAILABLE = False
    log_line("warning", "Using fallback HTTP client (urllib) - functionality may be limited")

def get_api_key() -> str:
    """Get API key from preferences or environment"""
    return load_pref("api_key") or os.getenv("ANTHROPIC_API_KEY", "")

def call_claude(prompt: str, system_prompt: str = None, model: str = None) -> dict:
    """
    Call the Claude API with the given prompt
    
    Args:
        prompt: The user prompt
        system_prompt: Optional system prompt for Claude
        model: Model to use (defaults to preference)
        
    Returns:
        Dict containing the API response
    """
    url = "https://api.anthropic.com/v1/messages"
    api_key = load_pref("claude_api_key", "")
    
    if not api_key:
        log_line("error", "No Claude API key provided. Check Settings.")
        return {"completion": "Error: No Claude API key provided. Please check Settings."}
    
    # Default to the model in preferences, or use a fallback
    if model is None:
        model = load_pref("model", "claude-3-sonnet-20240229")
    
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Construct the request message
    messages = [{"role": "user", "content": prompt}]
    
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": 1000
    }
    
    # Add system prompt if provided
    if system_prompt:
        data["system"] = system_prompt
    
    try:
        log_line("info", f"Calling Claude API with model {model}")
        
        if REQUESTS_AVAILABLE:
            # Use requests library if available
            resp = requests.post(url, json=data, headers=headers)
            resp.raise_for_status()  # Raise exception for 4XX/5XX responses
            
            response_data = resp.json()
            completion = response_data.get("content", [{}])[0].get("text", "")
        else:
            # Fallback to urllib if requests not available
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method='POST')
            
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                completion = response_data.get("content", [{}])[0].get("text", "")
        
        return {"completion": completion}
    except Exception as e:
        error_msg = f"API call failed: {str(e)}"
        log_line("error", error_msg)
        return {"completion": f"Error: {error_msg}"}

def get_available_models():
    """Get available Claude models for the settings dropdown"""
    return [
        {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "description": "Fastest, most compact"},
        {"id": "claude-3-sonnet-20240229", "name": "Claude 3.5 Sonnet", "description": "Balanced speed & intelligence"},
        {"id": "claude-3-opus-20240229", "name": "Claude 4 Opus", "description": "Most powerful, slowest"},
    ]