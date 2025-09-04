# 🎯 Commander - Complete User Guide

**Author**: Wes McDermott  
**For**: Substance Painter Commander Plugin v2.0+

This guide will walk you through every feature of Commander with practical examples and workflows.

---

## 🚀 Getting Started

### First Launch

1. **Install Commander** (see README.md for installation)
2. **Restart Substance Painter**
3. **Open any project** (Commander needs an active project)
4. **Press `Cmd+;` (macOS) or `Ctrl+;` (Windows/Linux)** - Commander appears at your mouse cursor!

### Interface Overview

When Commander opens, you'll see:
- **Search Box**: Type to filter commands
- **Command List**: Available operations (white text)
- **Status Bar**: Shows "Found X commands..." 
- **Background**: Dark theme that matches Substance Painter

---

## 🎮 Basic Usage

### Opening Commander
- **Primary**: `Cmd+;` (macOS) or `Ctrl+;` (Windows/Linux)
- **Alternative**: `Cmd+`` (macOS) or `Ctrl+`` (Windows/Linux)
- **Toolbar**: Click the "C" button (right toolbar)

### Executing Commands
1. **Type to search**: e.g., "fill" shows fill-related commands
2. **Navigate**: Use ↑↓ arrow keys or mouse
3. **Execute**: Double-click or press Enter
4. **Close**: Press Escape or click outside

### Quick Example
```
1. Press Cmd+; (macOS) or Ctrl+; (Windows/Linux)
2. Type "paint"
3. Double-click "Create Paint Layer"  
4. ✅ New paint layer created and selected!
```

---

## 🎨 Layer Operations

### Creating Layers

**Paint Layers** (for brush painting):
```
Cmd+; (macOS) or Ctrl+; (Windows) → Type "paint" → Enter
Result: New paint layer, ready for brushing
```

**Fill Layers** (for solid colors/materials):
```  
Cmd+; (macOS) or Ctrl+; (Windows) → Type "fill" → Enter
Result: New fill layer with BaseColor channel only
```

**Groups** (for organization):
```
Cmd+; (macOS) or Ctrl+; (Windows) → Type "group" → Enter  
Result: New folder to organize layers
```

### Managing Layers

**Add Layer Mask**:
```
1. Select any layer
2. Cmd+; (macOS) or Ctrl+; (Windows) → Type "mask" → "Add Layer Mask"
3. ✅ White mask added, mask context selected
```

**Set Layer Opacity**:
```
1. Select any layer
2. Cmd+; (macOS) or Ctrl+; (Windows) → Type "opacity" → Enter
3. Use slider to adjust transparency
```

**Toggle Visibility**:
```
Cmd+; (macOS) or Ctrl+; (Windows) → Type "toggle" → Enter
Result: Layer visibility toggled on/off
```

---

## 🎬 Macro System (Advanced)

Macros let you record sequences of commands and replay them instantly.

### Creating Your First Macro

**Example: "Weathering Setup" Macro**

1. **Start Recording**:
   ```
   Cmd+; (macOS) or Ctrl+; (Windows) → Right-click any command → "Start Macro Creation"
   Status: "Macro Creation Mode - Select commands..."
   ```

2. **Select Commands** (single-click each):
   ```
   ✓ Create Fill Layer        (turns yellow)
   ✓ Add Layer Mask          (turns yellow)  
   ✓ [PROC] Grunge Brushed   (turns yellow)
   ```

3. **Save Macro**:
   ```
   Right-click any selected command → "Create Macro"
   Enter name: "Weathering Setup"
   ✅ Macro created!
   ```

4. **Execute Macro**:
   ```
   Cmd+; (macOS) or Ctrl+; (Windows) → Type "weather" → Double-click "[MACRO] Weathering Setup"
   ✅ All commands execute in sequence!
   ```

### Macro Management

**Rename Macro**:
```
Cmd+; (macOS) or Ctrl+; (Windows) → Right-click macro → "Rename Macro" → Enter new name
```

**Delete Macro**:
```  
Cmd+; (macOS) or Ctrl+; (Windows) → Right-click macro → "Delete Macro" → Confirm
```

**Cancel Creation**:
```
During recording: Right-click → "Cancel Macro Creation"
```

### Advanced Macro Examples

**"Complete Material Setup"**:
```
1. Create Fill Layer
2. Insert Fill Effect  
3. Add Layer Mask
4. [PROC] Perlin Noise
5. Set Layer Opacity
```

**"Paint Workflow"**:
```
1. Create Paint Layer
2. Add Layer Mask
3. Set Mask Background Black
4. Toggle Layer Visibility
```

---

## 🎨 Procedural Resources

Commander integrates with Substance Painter's procedural library for instant access to noises, grunge textures, and patterns.

### Finding Procedurals

**Search by Name**:
```
Cmd+; (macOS) or Ctrl+; (Windows) → Type "noise"
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
2. Cmd+; (macOS) or Ctrl+; (Windows) → Double-click [PROC] Perlin Noise
3. ✅ Creates fill effect with procedural on Roughness channel
```

**To Masks (Grayscale)**:
```
1. Select any layer → Add mask (switches to mask mode)
2. Cmd+; (macOS) or Ctrl+; (Windows) → Double-click [PROC] Grunge Brushed  
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
2. Cmd+; (macOS) or Ctrl+; (Windows) → "Insert Fill Effect"
3. ✅ Empty fill effect ready for content
```

**Filter Effects** (image processing):
```
Cmd+; (macOS) or Ctrl+; (Windows) → "Insert Filter Effect" → Choose filter
```

**Generator Effects** (mask generation):
```  
Cmd+; (macOS) or Ctrl+; (Windows) → "Insert Generator Effect" → Choose generator
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
   Cmd+; (macOS) or Ctrl+; (Windows) → "Create Fill Layer" → Set base color
   ```

2. **Add Variation**:
   ```  
   Cmd+; (macOS) or Ctrl+; (Windows) → "Insert Fill Effect" 
   Apply [PROC] Perlin Noise to Roughness
   ```

3. **Add Wear**:
   ```
   Cmd+; (macOS) or Ctrl+; (Windows) → "Add Layer Mask"
   Apply [PROC] Grunge Brushed to mask
   ```

4. **Fine-tune**:
   ```
   Cmd+; (macOS) or Ctrl+; (Windows) → "Set Layer Opacity" → Adjust to taste
   ```

### Macro-Powered Workflows

**Save Complex Setups as Macros**:

Instead of repeating 8-10 manual steps, create macros like:
- **"Fabric Setup"**: Base + Normal + Roughness variation
- **"Metal Weathering"**: Clean base + corrosion layers + edge wear
- **"Wood Grain"**: Base + grain procedural + color variation

---

## 🎯 Productivity Tips

### Search Shortcuts

**Fuzzy Search Works**:
```
"fll" finds → Create Fill Layer
"msk" finds → Add Layer Mask  
"proc" finds → All procedurals
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
1. Cmd+; (macOS) or Ctrl+; (Windows) → Type → Enter → Continue working
2. Never touch mouse if you don't want to
3. Escape to close, no menu navigation needed
```

### Visual Feedback

**Understand the Colors**:
- **White Text**: Regular commands
- **Orange Text**: Your saved macros  
- **Blue Text**: Procedural resources `[PROC]`
- **Yellow Highlight**: Commands selected for macro creation

---

## 🛠️ Customization & Settings

### Macro Storage

**Location**: 
- Windows: `C:\Users\[you]\.substance_painter_commander\macros.json`
- macOS/Linux: `~/.substance_painter_commander/macros.json`

**Backup Your Macros**:
```
1. Find the macros.json file
2. Copy it to safe location  
3. Restore by placing it back in the folder
```

**Share Macros**:
```
Send your macros.json file to colleagues
They place it in their Commander folder
Instant shared workflows!
```

---

## 🚨 Troubleshooting

### Common Issues

**Commander doesn't appear**:
- ✅ Try both `Cmd+;` & `Cmd+`` (macOS) or `Ctrl+;` & `Ctrl+`` (Windows/Linux) 
- ✅ Restart Substance Painter
- ✅ Check Console for Python errors

**Commands fail**:
- ✅ Ensure project is open
- ✅ Select appropriate layer type
- ✅ Check layer isn't locked
- ✅ Some commands need specific contexts

**Macros don't work**:
- ✅ Verify each command works individually
- ✅ Check command order (masks before procedurals)
- ✅ Ensure proper layer selection between steps

**Procedurals don't apply**:
- ✅ Select target layer first
- ✅ Check if you're in mask vs content context
- ✅ Try different channel (Roughness vs BaseColor)

### Getting Help

**Debug Information**:
```
1. Open Console (Windows → Console)
2. Look for [Python] Commander messages
3. Error messages show what went wrong
```

---

## 🎨 Real-World Examples

### Example 1: Quick Leather Material

```
Goal: Create realistic leather in 30 seconds

Workflow:
1. Cmd+; (macOS) or Ctrl+; (Windows) → "Create Fill Layer" → Set brown base color
2. Cmd+; (macOS) or Ctrl+; (Windows) → "Insert Fill Effect" → Apply [PROC] Leather grain to Normal  
3. Cmd+; (macOS) or Ctrl+; (Windows) → "Add Layer Mask" → Apply [PROC] Grunge light wear
4. Cmd+; (macOS) or Ctrl+; (Windows) → "Set Layer Opacity" → 75%

✅ Professional leather material complete!
```

### Example 2: Weathered Paint Macro

```
Goal: Save complex paint weathering as reusable macro

Recording:
1. Start Macro Creation
2. Select: Create Fill Layer
3. Select: Set base paint color  
4. Select: Add Layer Mask
5. Select: [PROC] Grunge Scratches
6. Select: Insert Fill Effect (for rust bleed)
7. Select: [PROC] Rust stains
8. Create Macro: "Weathered Paint"

Usage:
Cmd+; (macOS) or Ctrl+; (Windows) → "[MACRO] Weathered Paint" → Instant weathered paint setup!
```

### Example 3: Fabric Detailing

```
Goal: Add realistic fabric texture to any material

Workflow:  
1. Select existing material layer
2. Cmd+; (macOS) or Ctrl+; (Windows) → "Insert Fill Effect" 
3. Apply [PROC] Fabric weave to Normal channel
4. Cmd+; (macOS) or Ctrl+; (Windows) → "Set Layer Opacity" → 35% (subtle)
5. Cmd+; (macOS) or Ctrl+; (Windows) → "Toggle Layer Visibility" → Compare before/after

✅ Any material now has fabric micro-detail!
```

---

## 🎯 Mastery Goals

### Beginner (Week 1)
- ✅ Open Commander with shortcuts
- ✅ Create basic layers (Paint, Fill, Groups)
- ✅ Add and remove masks
- ✅ Search and execute commands efficiently

### Intermediate (Week 2-3)
- ✅ Create your first macros
- ✅ Use procedural resources effectively  
- ✅ Understand context switching (mask vs content)
- ✅ Build material workflows with effects

### Advanced (Month 1+)
- ✅ Complex macro libraries for all material types
- ✅ Procedural-driven texturing workflows
- ✅ Team macro sharing and standardization
- ✅ Complete materials without manual operations

---

## 🎉 Conclusion

Commander transforms Substance Painter into a keyboard-driven powerhouse. With macros and procedurals, you can:

- **10x Speed**: Complex setups in seconds, not minutes
- **Consistency**: Exact same results every time  
- **Creativity**: Focus on artistic decisions, not technical steps
- **Team Efficiency**: Share workflows through macro libraries

The more you use Commander, the more powerful it becomes. Start with basic commands, build your macro library, and soon you'll have a completely customized workflow that matches your exact needs.

**Happy Texturing!** 🎨✨

---

*For technical details and installation, see README.md*  
*For issues and updates, check the plugin directory*
