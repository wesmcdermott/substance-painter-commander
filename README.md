# Substance Painter Commander

**Author**: Wes McDermott

A powerful command palette plugin for Substance Painter with advanced macro creation, hotkey system, procedural resource integration, and context-aware layer operations. Inspired by Cinema 4D's Commander with modern workflow enhancements.

## ⚠️ Disclaimer

This software is an independent, personal project and is provided "as is." It is not an official Adobe product, plugin, or service, and it has not been reviewed, endorsed, or supported by Adobe. Any references to Adobe software are for compatibility purposes only. Adobe and related marks are trademarks of Adobe Inc.

**🎓 Learning Project Notice**: This plugin was developed as a learning exercise to explore Substance Painter's Python API and advanced Qt UI development. While fully functional and stable, users should thoroughly test all features in non-critical projects before considering any production implementation.

## 🚀 Features

### 🎯 Advanced Command Palette
- **Smart Dock Widget**: Appears at mouse cursor position with `Ctrl+;` (all platforms)
- **Persistent & Refocusable**: Stays open until closed, refocuses on subsequent shortcuts
- **Keyboard Navigation**: Arrow keys to navigate, Enter to execute, Escape to hide
- **Smart Search**: Fuzzy search through 40+ layer operations and procedural resources
- **Visual Priority**: Macros at top in golden yellow, procedurals in different colors
- **Click-away Compatible**: Stable dock behavior without crashes

### 🎬 Advanced Macro System
- **Visual Creation**: Interactive command selection with golden highlighting
- **Advanced Dialog**: Professional macro creation with command preview
- **Hotkey Support**: Assign custom hotkeys (F5, Ctrl+Shift+W, Alt+Q, etc.)
- **Conflict Detection**: Smart hotkey conflict resolution with user choices  
- **Context Menu**: Right-click macros for Execute, Add/Remove Hotkey, Delete
- **Persistent Storage**: Macros with hotkeys saved to JSON file
- **Global Execution**: Hotkeys work anywhere in Substance Painter
- **Smart Execution**: Commands execute in proper order with context awareness

### 🎨 Procedural Resources
- **Library Integration**: Access Substance Painter's complete procedural shelf
- **Smart Application**: Procedurals apply to Roughness channel on content, grayscale on masks
- **Macro Compatible**: Include procedurals in macro sequences for complex workflows
- **Visual Distinction**: Clear `[PROC]` prefix for easy identification
- **Intelligent Fallbacks**: Multiple channel assignment strategies

### 🔧 Enhanced Layer Operations
- **Smart Fill Layers**: Created with BaseColor channel only by default
- **Context-Aware Masks**: Add Layer Mask switches to mask context automatically
- **Proper Selection**: Layer creation automatically selects new layers
- **Effect System**: Fill, Filter, Generator, Levels, and specialized effects
- **Channel Control**: Fine-grained control over active channels
- **Error Handling**: Clear feedback for operation failures

### 🎪 User Experience
- **Single Shortcut**: `Ctrl+;` opens Commander (cross-platform consistency)
- **Keyboard First**: Full keyboard navigation without mouse dependency
- **Persistent Interface**: No auto-hiding, stays open until manually closed
- **Refocus Behavior**: Shortcut refocuses search when already open
- **Status Feedback**: Real-time operation status and command counts

## Installation

### 🚀 Automated Installation (Recommended)

**All Platforms:**
1. Download and extract the Commander plugin
2. Open Terminal/Command Prompt and navigate to the commander folder
3. Run the appropriate installer:
   - **macOS/Linux**: `./install_macos.sh` 
   - **Windows**: `install_windows.bat`
4. Restart Substance Painter

### 📁 Manual Installation

If you prefer manual installation:

1. Copy the `commander` folder to your Substance Painter plugins directory:
   - **Windows**: `C:\Users\[username]\Documents\Adobe\Adobe Substance 3D Painter\python\plugins\`
   - **macOS**: `~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/`
   - **Linux**: `~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/`

2. Restart Substance Painter

3. Access via `Ctrl+;` keyboard shortcut

### 🗑️ Uninstallation

**Automated Removal:**
- **macOS/Linux**: Run `./uninstall_macos.sh` from the installed plugin directory
- **Windows**: Run `uninstall_windows.bat` from the installed plugin directory
- Choose whether to preserve or remove your saved macros and hotkeys

**Manual Removal:**
- Delete the `commander` folder from your plugins directory
- Optionally delete macro storage directory (see Macro Storage section)

## 🎮 Usage

### Opening Commander
- **Primary Shortcut**: `Ctrl+;` (all platforms - consistent experience)
- **Behavior**: Dock widget appears at mouse cursor, floating above other panels
- **Persistence**: Stays open until manually closed with Escape

### Basic Operations
1. **Open**: Press `Ctrl+;` - appears at mouse cursor position
2. **Search**: Type to filter commands (e.g., "fill", "mask", "proc") 
3. **Navigate**: Use ↑/↓ arrow keys to select items
4. **Execute**: Press Enter or double-click to execute
5. **Close**: Press Escape to hide
6. **Refocus**: Press `Ctrl+;` again to refocus search field when already open

### Creating Advanced Macros
1. **Start Recording**: Click "Start Macro" button
2. **Select Commands**: Single-click commands to add them (golden yellow highlight)
3. **Toggle Selection**: Click again to remove commands from macro
4. **Create Macro**: Click "Finish Macro" button
5. **Advanced Dialog**: 
   - Enter macro name in dedicated field
   - Optionally record hotkey by clicking "Record Hotkey" and pressing keys
   - View command preview in scrollable list
   - Handle conflicts automatically
6. **Global Access**: Use assigned hotkeys anywhere in Substance Painter

### Macro Management
- **Execute**: Double-click macro name or press Enter
- **Hotkey Management**: Right-click macro → "Add Hotkey" or "Remove Hotkey"
- **Delete**: Right-click macro → "Delete Macro"
- **Single Command Macros**: Right-click any command → "Create Macro from this Command"

### Using Procedurals
1. **Find**: Search for procedural names (e.g., "noise", "grunge", "pattern")
2. **Apply**: Double-click `[PROC]` items to apply to selected layer
3. **Context**: Automatically applies to appropriate channels based on selection
4. **Macros**: Include in macro sequences for repeatable complex effects

## 💾 Macro Storage

### Storage Location
Macros and hotkeys are automatically saved to:

- **Windows**: `%USERPROFILE%\AppData\Local\Commander\commander_macros.json`
- **macOS**: `~/Library/Application Support/Commander/commander_macros.json`
- **Linux**: `~/.local/share/Commander/commander_macros.json`
- **Fallback**: `~/commander_macros.json` (if standard locations unavailable)

### File Format
```json
{
  "My Weathering Setup": {
    "commands": [
      "Create Fill Layer",
      "Add Layer Mask", 
      "[PROC] Grunge Brushed Metal"
    ],
    "hotkey": "F5"
  },
  "Quick Paint Setup": {
    "commands": [
      "Create Paint Layer",
      "Set Layer Opacity"
    ]
  }
}
```

### Backup & Restore
- **Backup**: Copy the `commander_macros.json` file to preserve macros and hotkeys
- **Restore**: Place saved file in the storage location
- **Share**: Send files to other users to share macro collections
- **Reset**: Delete the JSON file to start fresh

## 📋 Available Commands

### Layer Creation
| Command | Description | Notes |
|---------|-------------|-------|
| Create Paint Layer | New paint layer | Auto-selects for subsequent operations |
| Create Fill Layer | New fill layer | BaseColor channel only by default |
| Create Group Layer | Layer folder/group | Organizes layer stack |
| Create Layer Instance | Instance layer | References another layer |

### Layer Management  
| Command | Description | Notes |
|---------|-------------|-------|
| Delete Selected Layers | Remove selected | Works with multiple selections |
| Rename Selected Layer | Change layer name | Interactive dialog |

### Layer Properties
| Command | Description | Notes |
|---------|-------------|-------|
| Toggle Layer Visibility | Show/hide layer | Maintains selection |
| Show Layer | Make layer visible | Forces visibility on |
| Hide Layer | Make layer invisible | Forces visibility off |
| Set Layer Opacity | Adjust transparency | Interactive slider |
| Set Blend Mode | Change blending | Modal selection |

### Effects & Inserts
| Command | Description | Context |
|---------|-------------|---------|
| Insert Fill Effect | Add fill effect | Content/mask aware |
| Insert Filter Effect | Add filter effect | Content/mask aware |  
| Insert Generator Effect | Add generator | Content/mask aware |
| Insert Levels Effect | Add levels adjustment | Content/mask aware |
| Insert Compare Mask Effect | Add compare mask | Mask operations |
| Insert Color Selection Effect | Add color selection | Mask operations |
| Insert Anchor Point Effect | Add anchor point | Reference operations |

### Mask Operations
| Command | Description | Notes |
|---------|-------------|-------|
| Add Layer Mask | Add layer mask | Switches to mask context automatically |
| Remove Layer Mask | Delete layer mask | Returns to content context |
| Enable Layer Mask | Enable mask effect | Maintains mask context |
| Disable Layer Mask | Disable mask effect | Maintains mask context |

### Smart Materials & Resources
| Command | Description | Context |
|---------|-------------|---------|
| Insert Smart Material | Apply smart material | Content layers |
| Create Smart Material | Create from selection | Selected layers |
| Insert Smart Mask | Apply smart mask | Mask context |
| Create Smart Mask | Create from mask | Selected mask |

### Procedural Resources (`[PROC]` prefix)
| Type | Description | Application |
|------|-------------|-------------|
| Procedural Noises | Perlin, Simplex, Cellular, etc. | Roughness/grayscale channels |
| Grunge Textures | Wear, dirt, scratches, damage | Roughness/grayscale channels |
| Pattern Generators | Geometric, organic patterns | Roughness/grayscale channels |
| Material Effects | Surface treatments | Context-appropriate channels |

### Macros (`[MACRO]` prefix)
- **Display**: Golden yellow text at top of list
- **Hotkeys**: Shown in parentheses when assigned: `[MACRO] My Macro (F5)`
- **Management**: Right-click for Execute, hotkey management, and Delete
- **Creation**: Advanced dialog with hotkey recording and conflict detection

## ⌨️ Keyboard Shortcuts

### Global Shortcuts
- **`Ctrl+;`**: Open/refocus Commander (primary, cross-platform)

### Commander Interface
- **`Enter`**: Execute selected command/macro
- **`Escape`**: Hide Commander dock
- **`↑/↓`**: Navigate command list (visible items only)
- **`Type`**: Filter commands/macros/procedurals in real-time

### Macro Hotkeys
- **User-Defined**: F1-F12, Ctrl+Key, Alt+Key, Shift+Key combinations
- **Global**: Work anywhere in Substance Painter
- **Conflict Detection**: Automatic detection and resolution of duplicate assignments

## 🧠 Smart Features

### Context Awareness
- **Mask Selection**: Operations apply to mask stack (grayscale channels)
- **Content Selection**: Operations apply to content stack (color channels)
- **Auto-Switching**: Add Layer Mask automatically switches to mask context
- **Channel Intelligence**: Procedurals choose appropriate channels based on context

### Advanced Macro System
- **Hotkey Recording**: Click "Record Hotkey" and press key combination
- **Conflict Resolution**: Smart detection of duplicate hotkeys with user choice
- **Global Registration**: Hotkeys work throughout Substance Painter
- **Persistent Storage**: Hotkeys saved with macros and restored on plugin load
- **Context Menu**: Right-click management for all macro operations

### Visual Feedback
- **Golden Yellow**: Macros at top of list for priority access
- **Selection Highlighting**: Golden yellow for selected commands during creation
- **Status Updates**: Real-time feedback for operations and macro actions
- **Hotkey Display**: Clear indication of assigned hotkeys in macro names
- **Error Messages**: Descriptive feedback for failed operations

### Smart Interface
- **Cursor Positioning**: Appears at mouse location for quick access  
- **Persistent Display**: No auto-hiding, stays open until dismissed
- **Refocus Behavior**: Subsequent shortcuts refocus search field
- **Keyboard Navigation**: Full operation without mouse dependency
- **Smart Search**: Instant filtering with fuzzy matching

## 🔧 Troubleshooting

### Commander doesn't appear
- Check plugin folder location is correct
- Restart Substance Painter completely  
- Try the shortcut: `Ctrl+;`
- Check Console (Windows → Console) for Python errors
- Verify plugin.json is present and valid

### Macro issues
- Ensure commands execute in proper order within macros
- Some operations require specific layer types or contexts
- Check that previous command completed successfully before next executes
- Verify project is open and appropriate layers exist
- Check Console for macro execution errors

### Hotkey problems
- Verify hotkey isn't conflicting with Substance Painter shortcuts
- Check Console for hotkey registration errors
- Try removing and re-adding problematic hotkeys
- Restart Substance Painter if hotkeys stop working

### Procedural problems  
- Procedurals require an open project with active texture set
- Select appropriate layer/mask before applying procedurals
- Some procedurals may not be compatible with all channel types
- Check resource availability in Substance Painter's shelf
- Verify procedural resources are installed and accessible

## 🛠 Technical Details

- **Framework**: PySide6/Qt6 with PySide2/Qt5 fallback compatibility
- **Plugin Type**: Dock widget with popup-like positioning behavior
- **API Usage**: Official Substance Painter Python API exclusively
- **Storage**: JSON-based macro and hotkey persistence
- **Event System**: Qt global shortcuts for hotkey system
- **Resource Integration**: Native Substance Painter resource system
- **Error Handling**: Comprehensive try-catch with user feedback
- **Cross-Platform**: Consistent behavior on Windows, macOS, and Linux

## 📊 Version History

### v3.0.0 (Current)
- **NEW**: Advanced macro creation dialog with hotkey recording
- **NEW**: Global hotkey system with conflict detection and resolution
- **NEW**: Macros displayed at top in golden yellow with hotkey indicators
- **NEW**: Comprehensive keyboard navigation with arrow keys and Enter
- **NEW**: Right-click context menus for macro and hotkey management
- **NEW**: Persistent dock widget behavior - no auto-hiding
- **NEW**: Refocus behavior when shortcut pressed while already open
- **ENHANCED**: Cross-platform `Ctrl+;` shortcut consistency
- **ENHANCED**: Improved mask addition with proper API usage
- **ENHANCED**: Professional macro storage with hotkey persistence
- **ENHANCED**: Robust error handling with descriptive user feedback
- **FIXED**: All stability issues - no crashes on quit or disable
- **OPTIMIZED**: Single shortcut system for simplified user experience

### v2.0.0 (Previous)
- Complete macro recording and playback system
- Procedural resource browsing and application  
- Context-aware mask vs content operations
- Dark theme with improved visual feedback
- Smart layer selection and context switching

### v1.0.0 (Legacy)
- Basic command palette interface
- 40+ layer stack operations
- Popup positioning and click-away behavior
- Keyboard-only access

## 📄 License

This plugin is provided as-is for educational and productivity purposes.

---

**Commander** - Streamline your Substance Painter workflow with intelligent command automation, advanced macro system, and seamless resource integration.

## 📚 Documentation

- **README.md** - Installation, features overview, and technical details
- **HOW_TO_USE.md** - Complete step-by-step user guide with examples and workflows