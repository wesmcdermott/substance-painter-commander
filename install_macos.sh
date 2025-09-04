#!/bin/bash

# Substance Painter Commander - macOS Installer
# Author: Wes McDermott

echo "🎨 Substance Painter Commander - macOS Installer"
echo "================================================="
echo ""

# Define paths
PLUGINS_DIR="$HOME/Documents/Adobe/Adobe Substance 3D Painter/python/plugins"
COMMANDER_DIR="$PLUGINS_DIR/commander"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if we're running from the commander directory
if [[ ! -f "$SCRIPT_DIR/__init__.py" ]] || [[ ! -f "$SCRIPT_DIR/plugin.json" ]]; then
    echo "❌ Error: This installer must be run from the commander plugin directory"
    echo "   Make sure you're running it from the folder containing __init__.py and plugin.json"
    exit 1
fi

echo "📁 Checking Substance Painter installation..."

# Check if Adobe directory exists
if [[ ! -d "$HOME/Documents/Adobe" ]]; then
    echo "❌ Error: Adobe documents folder not found"
    echo "   Please ensure Substance Painter is installed"
    echo "   Expected: $HOME/Documents/Adobe"
    exit 1
fi

# Create plugins directory if it doesn't exist
echo "📂 Creating plugins directory..."
mkdir -p "$PLUGINS_DIR"

if [[ $? -ne 0 ]]; then
    echo "❌ Error: Failed to create plugins directory"
    echo "   Check permissions for: $PLUGINS_DIR"
    exit 1
fi

# Check if commander is already installed
if [[ -d "$COMMANDER_DIR" ]]; then
    echo "⚠️  Commander is already installed"
    read -p "   Do you want to overwrite the existing installation? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        exit 0
    fi
    
    echo "🗑️  Removing existing installation..."
    rm -rf "$COMMANDER_DIR"
fi

# Copy commander directory
echo "📦 Installing Commander plugin..."
cp -r "$SCRIPT_DIR" "$COMMANDER_DIR"

if [[ $? -ne 0 ]]; then
    echo "❌ Error: Failed to copy plugin files"
    echo "   Source: $SCRIPT_DIR"
    echo "   Target: $COMMANDER_DIR"
    exit 1
fi

# Remove installer files from the installed copy
rm -f "$COMMANDER_DIR/install_macos.sh"
rm -f "$COMMANDER_DIR/install_windows.bat"
rm -f "$COMMANDER_DIR/uninstall_macos.sh"
rm -f "$COMMANDER_DIR/uninstall_windows.bat"

# Verify installation
if [[ -f "$COMMANDER_DIR/__init__.py" ]] && [[ -f "$COMMANDER_DIR/plugin.json" ]]; then
    echo ""
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. Restart Substance Painter"
    echo "   2. Use Ctrl+; or Ctrl+\` to open Commander"
    echo "   3. Look for the 'C' button in the right toolbar"
    echo ""
    echo "📍 Installation location:"
    echo "   $COMMANDER_DIR"
    echo ""
    echo "📖 Macros will be stored in:"
    echo "   ~/.substance_painter_commander/macros.json"
    echo ""
    echo "🎯 For help and documentation, see README.md"
else
    echo "❌ Installation verification failed"
    echo "   Plugin files may not have been copied correctly"
    exit 1
fi
