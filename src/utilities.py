import c4d

def set_busy(state):
    """
    Set busy state in Cinema 4D UI
    
    Args:
        state: True to show busy state, False to hide
    """
    # The SetInputEnabled method doesn't exist in c4d.gui
    # Use a different approach to show busy state
    if state:
        c4d.StatusSetText("Processing...")  # Show status message
        # Optionally: Change cursor to busy cursor if available
    else:
        c4d.StatusSetText("")  # Clear status message
        # Optionally: Reset cursor if changed

def flash_status(message, is_busy=False):
    """
    Flash a status message
    
    Args:
        message: Message to display
        is_busy: Whether to show busy indicator
    """
    # Display status message
    if is_busy:
        c4d.StatusSetText(message)
    else:
        # Show temporary status message
        c4d.StatusSetText(message)