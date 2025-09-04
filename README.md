# Substance Painter Commander

**Author**: Wes McDermott

A powerful command palette plugin for Substance Painter with macro creation, procedural resource integration, and context-aware layer operations. Inspired by Cinema 4D's Commander with modern workflow enhancements.

## ⚠️ Disclaimer

This software is an independent, personal project and is provided "as is." It is not an official Adobe product, plugin, or service, and it has not been reviewed, endorsed, or supported by Adobe. Any references to Adobe software are for compatibility purposes only. Adobe and related marks are trademarks of Adobe Inc.

## 🚀 Features

### 🎯 Advanced Command Palette
- **Instant Popup**: Appears at mouse cursor position with `Cmd+;` (macOS) or `Ctrl+;` (Windows/Linux)
- **Smart Search**: Fuzzy search through 42+ layer operations
- **Macro Integration**: Record, save, and execute command sequences
- **Procedural Resources**: Browse and apply procedural noises/textures
- **Context Awareness**: Automatically detects mask vs content context
- **Click-away Closing**: Auto-hides when clicking outside

### 🎬 Macro System
- **Record Macros**: Single-click commands to build sequences
- **Smart Execution**: Commands execute in proper order with context awareness
- **Persistent Storage**: Macros saved to `~/.substance_painter_commander/macros.json`
- **Easy Management**: Right-click to rename or delete macros
- **Visual Feedback**: Orange text for macros, yellow selection highlights
- **Context-Aware**: Mask operations automatically switch selection context

### 🎨 Procedural Resources
- **Library Integration**: Access Substance Painter's procedural shelf
- **Smart Application**: Procedurals apply to Roughness channel on content, grayscale on masks
- **Macro Compatible**: Include procedurals in macro sequences
- **Visual Distinction**: Cornflower blue `[PROC]` prefix for easy identification
- **Intelligent Fallbacks**: Multiple channel assignment strategies

### 🔧 Enhanced Layer Operations
- **Smart Fill Layers**: Created with BaseColor channel only by default
- **Context-Aware Masks**: Add Layer Mask switches to mask context for subsequent operations
- **Proper Selection**: Layer creation automatically selects new layers
- **Insert Effects**: Fill, Filter, Generator, Levels, and specialized effects
- **Channel Control**: Fine-grained control over active channels

### 🎪 Dual Access Methods
- **Keyboard**: `Cmd+;` & `Cmd+`` (macOS) or `Ctrl+;` & `Ctrl+`` (Windows/Linux)
- **Toolbar Button**: Custom "C" icon in right toolbar for mouse users
- **Consistent Styling**: Dark theme with proper visual feedback

## Installation

### 🚀 Automated Installation (Recommended)

**macOS/Linux:**
1. Download and extract the Commander plugin
2. Open Terminal and navigate to the commander folder
3. Run: `./install_macos.sh`
4. Restart Substance Painter

**Windows:**
1. Download and extract the Commander plugin  
2. Double-click `install_windows.bat`
3. Follow the prompts
4. Restart Substance Painter

### 📁 Manual Installation

If you prefer manual installation:

1. Copy the `commander` folder to your Substance Painter plugins directory:
   - **Windows**: `C:\Users\[username]\Documents\Adobe\Adobe Substance 3D Painter\python\plugins\`
   - **macOS**: `~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/`
   - **Linux**: `~/Documents/Adobe/Adobe Substance 3D Painter/python/plugins/`

2. Restart Substance Painter

3. Access via `Cmd+;` (macOS) or `Ctrl+;` (Windows/Linux) keyboard shortcut or toolbar button

### 🗑️ Uninstallation

**Automated Removal:**
- **macOS/Linux**: Run `./uninstall_macos.sh` from the installed plugin directory
- **Windows**: Run `uninstall_windows.bat` from the installed plugin directory
- Choose whether to preserve or remove your saved macros

**Manual Removal:**
- Delete the `commander` folder from your plugins directory
- Optionally delete `~/.substance_painter_commander/` (macros)

## 🎮 Usage

### Opening Commander
- **Keyboard**: `Cmd+;` & `Cmd+`` (macOS) or `Ctrl+;` & `Ctrl+`` (Windows/Linux)
- **Toolbar**: Click the "C" button in right toolbar
- **Result**: Popup appears at mouse cursor position

### Basic Operations
1. **Search**: Type to filter commands (e.g., "fill", "mask", "proc")
2. **Navigate**: Arrow keys or mouse to select
3. **Execute**: Double-click or press Enter
4. **Close**: Escape or click outside

### Creating Macros
1. **Start Recording**: Right-click any regular command → "Start Macro Creation"
2. **Select Commands**: Single-click commands to add them (yellow highlight)
3. **Deselect**: Click again to remove from macro
4. **Save**: Right-click → "Create Macro" → enter name
5. **Execute**: Double-click macro or press Enter

### Using Procedurals
1. **Find**: Search for procedural names (e.g., "noise", "grunge")
2. **Apply**: Double-click `[PROC]` items to apply
3. **Context**: Applies to Roughness on content layers, grayscale on masks
4. **Macros**: Include in macro sequences for complex effects

## 💾 Macro Storage

### Storage Location
Macros are automatically saved to your user directory in a dedicated Commander folder:

- **Windows**: `C:\Users\[username]\.substance_painter_commander\macros.json`
- **macOS**: `~/.substance_painter_commander/macros.json` 
- **Linux**: `~/.substance_painter_commander/macros.json`

### File Format
- **Format**: JSON (human-readable text format)
- **Structure**: Each macro contains a name and array of commands
- **Persistence**: Automatically saved when macros are created/modified
- **Portability**: Can be copied between machines/users

### Backup & Restore
- **Backup**: Copy the `macros.json` file to save your macros
- **Restore**: Place a saved `macros.json` file in the Commander directory
- **Share**: Send `macros.json` files to other users to share macro collections
- **Reset**: Delete `macros.json` to start fresh (restart Substance Painter)

### Example File Structure
```json
{
  "My Weathering Setup": [
    "Create Fill Layer",
    "Add Layer Mask", 
    "[PROC] Grunge Brushed Metal"
  ],
  "Quick Paint Setup": [
    "Create Paint Layer",
    "Set Layer Opacity"
  ]
}
```

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
| Add Layer Mask | Add layer mask | Switches to mask context |
| Remove Layer Mask | Delete layer mask | Returns to content context |
| Enable Layer Mask | Enable mask effect | Maintains mask context |
| Disable Layer Mask | Disable mask effect | Maintains mask context |
| Set Mask Background White | White mask background | Reveals content |
| Set Mask Background Black | Black mask background | Hides content |

### Procedural Resources (`[PROC]` prefix)
| Type | Description | Application |
|------|-------------|-------------|
| Procedural Noises | Perlin, Simplex, etc. | Roughness/grayscale |
| Grunge Textures | Wear, dirt, scratches | Roughness/grayscale |
| Pattern Generators | Geometric patterns | Roughness/grayscale |

### Macros (`[MACRO]` prefix)
| Feature | Description | Usage |
|---------|-------------|-------|
| User-Created | Custom command sequences | Right-click to manage |
| Context-Aware | Proper mask/content handling | Automatic context switching |
| Persistent | Saved between sessions | Stored in user directory |

## ⌨️ Keyboard Shortcuts

- **`Cmd+;` (macOS) or `Ctrl+;` (Windows/Linux)**: Open Commander (primary)
- **`Cmd+`` (macOS) or `Ctrl+`` (Windows/Linux)**: Open Commander (alternative)
- **`Enter`**: Execute selected command/macro
- **`Escape`**: Close Commander popup
- **`↑/↓`**: Navigate command list
- **`Type`**: Filter commands/macros/procedurals

## 🧠 Smart Features

### Context Awareness
- **Mask Selection**: Operations apply to mask stack (grayscale)
- **Content Selection**: Operations apply to content stack (channeled)
- **Auto-Switching**: Add Layer Mask switches to mask context
- **Channel Intelligence**: Procedurals choose appropriate channels

### Visual Feedback
- **Macro Creation**: Yellow highlights for selected commands
- **Command Types**: Orange macros, blue procedurals, white commands  
- **Selection**: Dark gray background with high contrast text
- **Status Updates**: Real-time feedback in status bar

### Smart Defaults
- **Fill Layers**: BaseColor channel only (cleaner workflow)
- **Layer Selection**: New layers auto-selected for chaining operations
- **Insertion Logic**: Context-aware positioning in layer stack

## 🔧 Troubleshooting

### Commander doesn't appear
- Check plugin folder location is correct
- Restart Substance Painter completely
- Try both shortcuts: `Cmd+;` & `Cmd+`` (macOS) or `Ctrl+;` & `Ctrl+`` (Windows/Linux)
- Check Console (Windows → Console) for Python errors

### Macro issues
- Ensure commands execute in proper order
- Some operations require specific layer types
- Check that previous command completed successfully
- Verify project is open and layers exist

### Procedural problems  
- Procedurals require an open project
- Select appropriate layer/mask before applying
- Some procedurals may not be compatible with all channel types
- Check resource availability in Substance Painter shelf

## 🛠 Technical Details

- **Framework**: PySide6/Qt6 with PySide2/Qt5 compatibility
- **Plugin Type**: Dock widget (floating, frameless)
- **API Usage**: Official Substance Painter Python API
- **Storage**: JSON-based macro persistence
- **Event System**: Qt event filtering for UI behavior
- **Resource Integration**: Substance Painter resource system

## 📊 Version History

### v2.0.0 (Current)
- **NEW**: Complete macro recording and playback system
- **NEW**: Procedural resource browsing and application  
- **NEW**: Context-aware mask vs content operations
- **NEW**: Toolbar button for mouse access
- **ENHANCED**: Fill layers created with BaseColor only
- **ENHANCED**: Dark theme with improved visual feedback
- **ENHANCED**: Smart layer selection and context switching
- **ENHANCED**: Robust error handling and user feedback

### v1.0.0 (Legacy)
- Basic command palette interface
- 42+ layer stack operations
- Popup positioning and click-away behavior
- Keyboard-only access

## 📄 License

This plugin is provided as-is for educational and productivity purposes.

---

**Commander** - Streamline your Substance Painter workflow with intelligent command automation and resource integration.

## 📚 Documentation

- **README.md** - Installation, features overview, and technical details
- **HOW_TO_USE.md** - Complete step-by-step user guide with examples and workflows