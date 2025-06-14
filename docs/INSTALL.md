# CineCommand Plugin Installation Guide

## System Requirements

- Cinema 4D R21 or newer
- Python 3.7+ (included with Cinema 4D)
- Internet connection for API features
- Windows, macOS, or Linux operating system

## Installation Methods

### Method 1: Using the Plugin Installer (Recommended)

1. Download the latest CineCommand plugin installer from the [official website](https://cinecommand.example.com/downloads) or the Cinema 4D plugin marketplace.
2. Close Cinema 4D if it's currently running.
3. Run the installer and follow the on-screen instructions.
4. The installer will automatically place the plugin in the correct directory.
5. Start Cinema 4D and verify that CineCommand appears in the Plugins menu.

### Method 2: Manual Installation

1. Download the CineCommand ZIP archive from the [official website](https://cinecommand.example.com/downloads).
2. Close Cinema 4D if it's currently running.
3. Extract the ZIP file to get the CineCommand folder.
4. Locate your Cinema 4D plugins directory:
   - **Windows**: `C:\Users\[Username]\AppData\Roaming\MAXON\Cinema 4D [Version]\plugins\`
   - **macOS**: `/Users/[Username]/Library/Preferences/MAXON/Cinema 4D [Version]/plugins/`
   - **Linux**: `~/MAXON/Cinema 4D [Version]/plugins/`
5. Copy the CineCommand folder into the plugins directory.
6. Start Cinema 4D and verify that CineCommand appears in the Plugins menu.

## API Key Setup

CineCommand leverages Claude AI for advanced natural language processing. To use these features:

1. Create an account at [Anthropic's website](https://www.anthropic.com/).
2. Generate an API key from your account dashboard.
3. In Cinema 4D, go to **Plugins > CineCommand > Settings**.
4. Select the **API Key** tab.
5. Enter your Claude API key in the provided field.
6. Click **Test API Connection** to verify your key is working.
7. Click **OK** to save your settings.

## Troubleshooting

### Plugin Not Appearing in Cinema 4D

- Verify that you've installed the plugin in the correct directory.
- Check Cinema 4D's console for any error messages during startup.
- Ensure that your Cinema 4D version is compatible with CineCommand.

### API Connection Issues

- Confirm your internet connection is working.
- Verify that your API key is entered correctly without any extra spaces.
- Check your firewall settings to ensure Cinema 4D has internet access.
- Try restarting Cinema 4D after entering your API key.

### Permission Errors During Installation

- Ensure you have administrative privileges when installing the plugin.
- Try running the installer as administrator (right-click → Run as administrator).
- Check if your antivirus software is blocking the installation.

## Uninstallation

### Method 1: Using the Installer

1. Run the CineCommand installer again.
2. Select the "Uninstall" option.
3. Follow the on-screen instructions.

### Method 2: Manual Uninstallation

1. Close Cinema 4D.
2. Navigate to your Cinema 4D plugins directory.
3. Delete the CineCommand folder.
4. Optional: Delete the CineCommand preferences folder at:
   - **Windows**: `C:\Users\[Username]\AppData\Roaming\MAXON\Cinema 4D [Version]\plugins\CineCommand\prefs\`
   - **macOS**: `/Users/[Username]/Library/Preferences/MAXON/Cinema 4D [Version]/plugins/CineCommand/prefs/`
   - **Linux**: `~/MAXON/Cinema 4D [Version]/plugins/CineCommand/prefs/`

## Updating

1. Close Cinema 4D.
2. Follow the installation steps with the newer version.
3. Your previous settings should be preserved automatically.

## Support

If you encounter any issues during installation, please contact our support team:

- Email: support@cinecommand.example.com
- Forum: [CineCommand User Forum](https://forum.cinecommand.example.com)
- Documentation: [CineCommand Documentation](https://docs.cinecommand.example.com)