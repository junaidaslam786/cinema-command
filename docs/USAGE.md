# CineCommand Plugin User Guide

## Overview

CineCommand is a powerful natural language interface for Cinema 4D that allows you to control the software using conversational commands. This guide explains how to use the plugin effectively.

## Getting Started

1. Launch Cinema 4D and ensure the CineCommand plugin is installed.
2. Access CineCommand from the **Plugins > CineCommand** menu.
3. The CineCommand dialog will appear, featuring a text input area where you can type your commands.

## Basic Usage

### Command Prompt

1. Type your desired action in plain English in the command field.
2. Click the **Run** button or press Enter to execute the command.
3. The plugin will process your request and perform the appropriate action in Cinema 4D.

### Examples of Basic Commands

- "Add a red cube to the scene"
- "Create a sphere with a diameter of 100 units"
- "Make a glossy blue material"
- "Draw a circle spline with radius 500"
- "Create an 85-millimeter camera"
- "Set up a quick render preset"

## Command Categories

### Object Creation

CineCommand can create various primitive objects:

- **Cubes**: "Add a cube with size 200"
- **Spheres**: "Create a sphere with diameter 40"
- **Splines**: "Draw a circle spline with radius 500 on the XZ plane"
- **Cameras**: "Add an 85-millimeter camera named CineCam"

### Material Creation and Assignment

- **Create Materials**: "Make a glossy red material named MetalRed"
- **Apply Materials**: "Apply the MetalRed material to the cube"

### Object Manipulation

- **Selection**: "Select the cube named GlossyRed"
- **Duplication**: "Duplicate it four more times along the X axis"
- **Grouping**: "Group the selected objects and name it CubeLine"

### Camera and View Controls

- **Camera Creation**: "Create an 85-millimeter camera"
- **Framing**: "Frame all objects in the view"
- **Composition Guides**: "Enable golden spiral overlay for the camera"

### Render Settings

- **Creating Presets**: "Make a new render preset called QuickPreview"
- **Resolution Control**: "Set render resolution to 1920x1080 at 30fps"
- **Quality Settings**: "Disable global illumination"
- **Frame Range**: "Set frame range from 0 to 120"

## Advanced Features

### Custom Rules

CineCommand uses a rule-based system that can be customized:

1. Go to **Plugins > CineCommand > Settings**.
2. Select the **Advanced** tab.
3. Add or edit rules in JSON format:
   ```json
   {"prompt_contains":"Add a cube","commands":[{"action":"AddCube","args":{"size":200,"name":"GlossyRed","position":[0,0,0]}},{"action":"CreateMaterial","args":{"name":"GlossyRed","type":"glossy","color":[1,0,0]}}]}
   ```
4. Click **Save Rules** to apply your changes.

### Rule Structure

Each rule consists of:
- A `prompt_contains` pattern to match against user input
- An array of `commands` to execute when the pattern is matched
- Each command has an `action` name and optional `args` parameters

### Available Commands

| Action | Description | Key Arguments |
|--------|-------------|--------------|
| AddCube | Creates a cube | size, name, position |
| AddSphere | Creates a sphere | diameter, name, position |
| CreateMaterial | Creates a material | name, type, color |
| ApplyMaterial | Applies material to object | name, to |
| SelectObject | Selects an object by name | name |
| Duplicate | Duplicates selected objects | count, axis, distance |
| GroupSelected | Groups selected objects | name |
| AddSpline | Creates a spline | type, radius, plane |
| CloneAlongSpline | Creates clones along a spline | source, spline_index, count |
| AddCamera | Creates a camera | focal_length, name |
| FrameAll | Frames all objects in view | - |
| EnableOverlay | Enables camera composition guide | type |
| AddRenderSetting | Creates render settings | name |
| SetRenderResolution | Sets render resolution | width, height, fps |
| ToggleGI | Toggles global illumination | enabled |
| SetFrameRange | Sets animation frame range | start, end |

## AI Processing

When a command doesn't match any predefined rule, CineCommand will use the Claude API to interpret your request and generate appropriate actions.

### API Settings

1. Go to **Plugins > CineCommand > Settings**.
2. Select the **API Key** tab.
3. Configure your Claude API key.
4. Select your preferred AI model from the dropdown in the **General** tab.

## Logging and Troubleshooting

### Logging

CineCommand maintains logs of all operations:

1. Go to **Plugins > CineCommand > Settings**.
2. Select the **Logging** tab.
3. View the log directory path.
4. Click **Open Log Folder** to access log files.
5. Click **Clear All Logs** to remove old logs.

### Common Issues

- **Command not recognized**: Try rephrasing your command or add a custom rule.
- **Action not performed**: Check the logs for errors and ensure your commands match the expected format.
- **API errors**: Verify your API key is valid and your internet connection is working.

## Tips and Best Practices

1. **Start Simple**: Begin with basic commands to understand the plugin's capabilities.
2. **Check Logs**: If a command doesn't work, check the logs to see what happened.
3. **Custom Rules**: Create custom rules for commands you use frequently.
4. **Be Specific**: More specific commands yield better results than vague instructions.
5. **API Usage**: Be aware that using the Claude API incurs usage costs according to your Anthropic account plan.

## Keyboard Shortcuts

- **Ctrl+Shift+C** (Windows/Linux) or **Cmd+Shift+C** (macOS): Open CineCommand dialog
- **Enter**: Execute the current command
- **Esc**: Close the dialog
- **Ctrl+Z** (Windows/Linux) or **Cmd+Z** (macOS): Undo the last CineCommand action

## Further Resources

- [Video Tutorials](https://cinecommand.example.com/tutorials)
- [Command Reference](https://cinecommand.example.com/commands)
- [Rule Creation Guide](https://cinecommand.example.com/rules)
- [Community Forum](https://forum.cinecommand.example.com)