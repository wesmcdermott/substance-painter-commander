# 🎯 Commander - Complete User Guide

**Author**: Wes McDermott  
**For**: Substance Painter Commander Plugin v3.0+

This guide will walk you through every feature of Commander with practical examples and workflows.

---

## 🚀 Getting Started

### First Launch

1. **Install Commander** (see README.md for installation)
2. **Restart Substance Painter**
3. **Open any project** (Commander needs an active project)
4. **Press `Ctrl+;`** - Commander appears at your mouse cursor!

### Interface Overview

When Commander opens, you'll see:
- **Search Box**: Type to filter commands (automatically focused)
- **Command List**: Available operations with color coding
- **Status Bar**: Shows "Found X items..." with counts
- **Background**: Dark theme that matches Substance Painter
- **Golden Macros**: User macros appear at top in golden yellow

---

## 🎮 Basic Usage

### Opening Commander
- **Single Shortcut**: `Ctrl+;` (cross-platform consistency)
- **Persistent**: Stays open until manually closed
- **Refocusable**: Press `Ctrl+;` again to refocus search when already open

### Navigation & Execution
1. **Search**: Type to filter commands (e.g., "fill" shows fill-related commands)
2. **Keyboard Navigation**: Use ↑↓ arrow keys to select items
3. **Execute**: Press Enter or double-click to execute
4. **Close**: Press Escape to hide
5. **Auto-Focus**: Search field automatically focused on open and refocus

### Quick Example
```
1. Press Ctrl+;
2. Type "paint"
3. Press ↓ to select "Create Paint Layer"
4. Press Enter
5. ✅ New paint layer created and selected!
```

---

## 🎨 Layer Operations

### Creating Layers

**Paint Layers** (for brush painting):
```
Ctrl+; → Type "paint" → Enter
Result: New paint layer, ready for brushing
```

**Fill Layers** (for solid colors/materials):
```  
Ctrl+; → Type "fill" → Enter
Result: New fill layer with BaseColor channel only
```

**Groups** (for organization):
```
Ctrl+; → Type "group" → Enter  
Result: New folder to organize layers
```

### Managing Layers

**Add Layer Mask**:
```
1. Select any layer
2. Ctrl+; → Type "mask" → Select "Add Layer Mask" → Enter
3. ✅ White mask added, mask context selected automatically
```

**Set Layer Opacity**:
```
1. Select any layer
2. Ctrl+; → Type "opacity" → Enter
3. Use slider to adjust transparency
```

**Toggle Visibility**:
```
Ctrl+; → Type "toggle" → Enter
Result: Layer visibility toggled on/off
```

---

## 🎬 Advanced Macro System

Macros let you record command sequences with hotkeys for instant execution anywhere in Substance Painter.

### Creating Your First Macro

**Example: "Weathering Setup" Macro with Hotkey**

1. **Start Recording**:
   ```
   Ctrl+; → Click "Start Macro" button
   Status: "Macro Creation Mode - Select commands..."
   ```

2. **Select Commands** (single-click each):
   ```
   ✓ Create Fill Layer        (turns golden yellow)
   ✓ Add Layer Mask          (turns golden yellow)  
   ✓ [PROC] Grunge Brushed   (turns golden yellow)
   ```

3. **Create Macro with Advanced Dialog**:
   ```
   Click "Finish Macro" button
   Advanced Dialog Opens:
   - Command preview shows selected commands
   - Enter name: "Weathering Setup"
   - Click "Record Hotkey" → Press F5
   - Click "Create Macro"
   ✅ Macro created with hotkey F5!
   ```

4. **Execute Macro** (Multiple Ways):
   ```
   Option 1: Press F5 (anywhere in Substance Painter)
   Option 2: Ctrl+; → Type "weather" → Enter
   Option 3: Double-click "[MACRO] Weathering Setup (F5)"
   ✅ All commands execute in sequence!
   ```

### Hotkey System

**Recording Hotkeys**:
- Click "Record Hotkey" in macro dialog
- Press desired key combination
- Examples: F5, Ctrl+Shift+W, Alt+Q, Shift+F1
- Automatic conflict detection with resolution options

**Managing Hotkeys**:
```
Right-click any macro → 
- "Add Hotkey" (if none assigned)
- "Remove Hotkey (F5)" (if assigned)
- "Delete Macro"
```

**Conflict Resolution**:
- Automatic detection of duplicate assignments
- Choice to reassign or keep existing
- Warning for potential Substance Painter conflicts

### Macro Management

**Create Single Command Macro**:
```
Ctrl+; → Right-click any command → "Create Macro from this Command"
Advanced dialog opens for naming and hotkey assignment
```

**Execute Macro**:
```
Option 1: Use assigned hotkey (global)
Option 2: Double-click in Commander
Option 3: Select and press Enter
```

**Delete Macro**:
```  
Ctrl+; → Right-click macro → "Delete Macro" → Confirm
Hotkey automatically unregistered
```

### Advanced Macro Examples

**"Complete Material Setup" (Hotkey: F6)**:
```
1. Create Fill Layer
2. Insert Fill Effect  
3. Add Layer Mask
4. [PROC] Perlin Noise
5. Set Layer Opacity
```

**"Paint Workflow" (Hotkey: Ctrl+P)**:
```
1. Create Paint Layer
2. Add Layer Mask
3. Set Mask Background Black
```

---

## 🎨 Procedural Resources

Commander integrates with Substance Painter's complete procedural library for instant access to noises, grunge textures, and patterns.

### Finding Procedurals

**Search by Name**:
```
Ctrl+; → Type "noise"
Shows: [PROC] Perlin Noise, [PROC] Simplex Noise, etc.
```

**Search by Category**:
```  
Type "grunge" → [PROC] Grunge Brushed, [PROC] Grunge Metal
Type "pattern" → [PROC] Hexagon Pattern, [PROC] Brick Pattern
```

### Applying Procedurals

**To Content (Material Channels)**:
```
1. Select any layer (content mode)
2. Ctrl+; → Double-click [PROC] Perlin Noise
3. ✅ Creates fill effect with procedural on Roughness channel
```

**To Masks (Grayscale)**:
```
1. Select any layer → Add mask (switches to mask mode)
2. Ctrl+; → Double-click [PROC] Grunge Brushed  
3. ✅ Creates grayscale fill effect on mask
```

### Context-Aware Application

Commander automatically detects your current context:

| Context | Procedural Applied To | Use Case |
|---------|----------------------|----------|
| **Content Stack** | Roughness Channel | Material variation, surface detail |
| **Mask Stack** | Grayscale | Masking patterns, wear areas |

---

## 🔧 Advanced Effects

### Insert Effects

**Fill Effects** (color/procedural fills):
```
1. Select layer or mask
2. Ctrl+; → "Insert Fill Effect"
3. ✅ Empty fill effect ready for content
```

**Filter Effects** (image processing):
```
Ctrl+; → "Insert Filter Effect" → Choose filter
```

**Generator Effects** (mask generation):
```  
Ctrl+; → "Insert Generator Effect" → Choose generator
```

### Smart Insertion

Commander intelligently places effects based on your selection:
- **Layer Selected**: Effect goes in content stack
- **Mask Selected**: Effect goes in mask stack  
- **Auto-positioning**: Effects inserted at logical positions

---

## 💡 Pro Workflows

### Material Creation Workflow

**"Realistic Metal Material" Process**:

1. **Base Setup**:
   ```
   Ctrl+; → "Create Fill Layer" → Set base metallic color
   ```

2. **Add Surface Variation**:
   ```  
   Ctrl+; → "Insert Fill Effect" 
   Apply [PROC] Perlin Noise to Roughness
   ```

3. **Add Wear Pattern**:
   ```
   Ctrl+; → "Add Layer Mask"
   Apply [PROC] Grunge Brushed to mask
   ```

4. **Fine-tune**:
   ```
   Ctrl+; → "Set Layer Opacity" → Adjust to taste
   ```

### Hotkey-Powered Workflows

**Lightning Fast Material Creation**:
```
F5 → "Weathering Setup" (instant base + mask + procedural)
F6 → "Metal Variation" (roughness patterns)
F7 → "Edge Wear" (mask-based edge effects)
Ctrl+P → "Paint Ready" (paint layer + mask setup)
```

**Save Complex Setups as Hotkey Macros**:
- **F5**: "Fabric Setup" - Base + Normal + Roughness variation
- **F6**: "Metal Weathering" - Clean base + corrosion + edge wear  
- **F7**: "Wood Grain" - Base + grain procedural + color variation

---

## 🎯 Productivity Tips

### Search Shortcuts

**Fuzzy Search Works**:
```
"fll" finds → Create Fill Layer
"msk" finds → Add Layer Mask  
"proc" finds → All procedurals
"mac" finds → All macros
```

**Command Categories**:
```
"create" → All creation commands
"insert" → All effect insertions
"set" → All property setters
"toggle" → All toggle operations
```

### Keyboard Efficiency

**Stay in Flow**:
```
1. Ctrl+; → Type → ↓↓ → Enter → Continue working
2. Never touch mouse if you don't want to
3. Escape to close, Ctrl+; to refocus
4. Use hotkeys for frequent macros
```

**Navigation Shortcuts**:
- **Arrow Keys**: Navigate visible results only
- **Enter**: Execute selected item
- **Escape**: Hide Commander
- **Type**: Instant filtering

### Visual Feedback System

**Understand the Colors**:
- **Golden Yellow**: Your saved macros (priority at top)
- **White Text**: Regular commands
- **Procedural Colors**: `[PROC]` procedural resources
- **Golden Highlight**: Commands selected for macro creation

**Hotkey Display**:
- Macros show assigned hotkeys: `[MACRO] My Setup (F5)`
- Right-click for hotkey management

---

## 🛠️ Customization & Settings

### Macro & Hotkey Storage

**Auto-Detection Location**: 
- Windows: `%USERPROFILE%\AppData\Local\Commander\commander_macros.json`
- macOS: `~/Library/Application Support/Commander/commander_macros.json`
- Linux: `~/.local/share/Commander/commander_macros.json`
- Fallback: `~/commander_macros.json`

**File Format (with Hotkeys)**:
```json
{
  "Weathering Setup": {
    "commands": [
      "Create Fill Layer",
      "Add Layer Mask", 
      "[PROC] Grunge Brushed Metal"
    ],
    "hotkey": "F5"
  },
  "Quick Paint": {
    "commands": [
      "Create Paint Layer",
      "Set Layer Opacity"
    ]
  }
}
```

**Backup Your Macros & Hotkeys**:
```
1. Find the commander_macros.json file
2. Copy it to safe location  
3. Restore by placing it back in the detected folder
4. All macros and hotkeys restore automatically
```

**Share Workflows**:
```
Send your commander_macros.json file to colleagues
They place it in their Commander folder
Instant shared workflows with hotkeys!
```

---

## 🚨 Troubleshooting

### Common Issues

**Commander doesn't appear**:
- ✅ Try `Ctrl+;` shortcut
- ✅ Restart Substance Painter completely
- ✅ Check Console (Windows → Console) for Python errors
- ✅ Verify plugin folder installation

**Commands fail**:
- ✅ Ensure project is open
- ✅ Select appropriate layer type
- ✅ Check layer isn't locked
- ✅ Some commands need specific contexts

**Macros don't execute**:
- ✅ Verify each command works individually
- ✅ Check command order (masks before procedurals)
- ✅ Ensure proper layer selection between steps
- ✅ Check Console for macro execution errors

**Hotkeys don't work**:
- ✅ Check for conflicts with Substance Painter shortcuts
- ✅ Try removing and re-adding hotkeys
- ✅ Restart Substance Painter if hotkeys stop responding
- ✅ Check Console for hotkey registration errors

**Procedurals don't apply**:
- ✅ Select target layer first
- ✅ Check if you're in mask vs content context
- ✅ Verify procedural resources are installed
- ✅ Check Console for resource loading errors

### Getting Help

**Debug Information**:
```
1. Open Console (Windows → Console)
2. Look for [Python] Commander messages
3. Error messages show exactly what went wrong
4. Hotkey registration and macro execution are logged
```

---

## 🎨 Real-World Examples

### Example 1: Lightning-Fast Leather Material

```
Goal: Professional leather material in 15 seconds

Setup Macro (F8):
1. Create Fill Layer
2. Insert Fill Effect ([PROC] Leather grain to Normal)
3. Add Layer Mask  
4. Apply [PROC] Grunge light wear to mask
5. Set Layer Opacity to 75%

Usage:
Press F8 → Instant professional leather!
Adjust base color → Done!
```

### Example 2: Hotkey Workflow System

```
Goal: Complete material library with hotkeys

Macro Library:
F1 → "Clean Metal" (base metallic setup)
F2 → "Weathered Metal" (rust and wear)
F3 → "Painted Metal" (paint + wear)
F4 → "Fabric Base" (cloth setup)
F5 → "Weathering Pass" (damage layer)
F6 → "Detail Pass" (surface detail)

Workflow:
F1 (base) → F5 (weather) → F6 (detail) = Complete material in 3 keystrokes!
```

### Example 3: Team Standardization

```
Goal: Shared studio workflow

Studio Hotkeys:
Ctrl+1 → "Studio Base Material"
Ctrl+2 → "Studio Weathering"  
Ctrl+3 → "Studio Detail Pass"
Ctrl+4 → "Studio Paint Setup"

Implementation:
1. Create macros with standardized hotkeys
2. Share commander_macros.json file
3. Everyone has identical hotkey workflow
4. Consistent results across team
```

---

## 🎯 Mastery Goals

### Beginner (Week 1)
- ✅ Open Commander with `Ctrl+;`
- ✅ Navigate with arrow keys and Enter
- ✅ Create basic layers (Paint, Fill, Groups)
- ✅ Add and remove masks
- ✅ Search and execute commands efficiently

### Intermediate (Week 2-3)
- ✅ Create macros with advanced dialog
- ✅ Assign hotkeys to frequently used macros
- ✅ Use procedural resources effectively  
- ✅ Understand context switching (mask vs content)
- ✅ Build material workflows with effects

### Advanced (Month 1+)
- ✅ Complete hotkey system for all workflows
- ✅ Complex macro libraries for material types
- ✅ Team macro sharing and standardization
- ✅ Procedural-driven texturing workflows
- ✅ Lightning-fast material creation (F-key workflows)

---

## 🎉 Conclusion

Commander v3.0 transforms Substance Painter into a hotkey-driven powerhouse. With advanced macros and global hotkeys, you can:

- **Lightning Speed**: Complex materials in seconds with hotkeys
- **Global Access**: Hotkeys work anywhere in Substance Painter  
- **Perfect Consistency**: Exact same results every time
- **Team Efficiency**: Share complete workflows with hotkeys
- **Creative Focus**: Spend time on art, not technical steps

**The Ultimate Workflow**: Build your personal F-key library where F1-F12 contain your most-used material setups. Combined with procedural resources and context awareness, you'll have the fastest texturing workflow possible.

**Happy Texturing!** 🎨✨⚡

---

*For technical details and installation, see README.md*  
*For issues and updates, check the plugin directory*