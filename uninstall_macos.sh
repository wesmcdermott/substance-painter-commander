#!/bin/bash

# Substance Painter Commander - macOS Uninstaller
# Author: Wes McDermott

echo "🗑️  Substance Painter Commander - macOS Uninstaller"
echo "==================================================="
echo ""

# Define paths
PLUGINS_DIR="$HOME/Documents/Adobe/Adobe Substance 3D Painter/python/plugins"
COMMANDER_DIR="$PLUGINS_DIR/commander"
MACROS_DIR="$HOME/Library/Application Support/Commander"

echo "🔍 Checking for Commander installation..."

# Check if Commander is installed
if [[ ! -d "$COMMANDER_DIR" ]]; then
    echo "ℹ️  Commander is not currently installed"
    echo "   Directory not found: $COMMANDER_DIR"
    exit 0
fi

echo "📍 Found Commander installation at:"
echo "   $COMMANDER_DIR"

if [[ -d "$MACROS_DIR" ]]; then
    echo "📍 Found macro storage at:"
    echo "   $MACROS_DIR"
fi

echo ""
echo "⚠️  This will completely remove Commander and all associated files"
read -p "   Are you sure you want to uninstall Commander? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Uninstallation cancelled"
    exit 0
fi

# Ask about macros
if [[ -d "$MACROS_DIR" ]]; then
    echo ""
    read -p "🔄 Do you also want to remove saved macros & hotkeys? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        REMOVE_MACROS=true
        echo "🗑️  Will remove macros and settings"
    else
        REMOVE_MACROS=false
        echo "💾 Will preserve macros and settings"
    fi
fi

echo ""
echo "🗑️  Removing Commander plugin..."

# Remove the commander directory
rm -rf "$COMMANDER_DIR"

if [[ $? -ne 0 ]]; then
    echo "❌ Error: Failed to remove Commander directory"
    echo "   Please close Substance Painter and try again"
    echo "   Manual removal may be required: $COMMANDER_DIR"
    exit 1
fi

# Remove macros if requested
if [[ "$REMOVE_MACROS" == true ]] && [[ -d "$MACROS_DIR" ]]; then
    echo "🗑️  Removing macros and settings..."
    rm -rf "$MACROS_DIR"
    
    if [[ $? -ne 0 ]]; then
        echo "⚠️  Warning: Failed to remove macro directory"
        echo "   You may need to manually remove: $MACROS_DIR"
    fi
fi

# Verify removal
if [[ ! -d "$COMMANDER_DIR" ]]; then
    echo ""
    echo "✅ Commander has been successfully uninstalled!"
    echo ""
    echo "🔄 Next steps:"
    echo "   1. Restart Substance Painter"  
    echo "   2. Commander shortcuts and hotkeys will be removed"
    
    if [[ "$REMOVE_MACROS" != true ]] && [[ -d "$MACROS_DIR" ]]; then
        echo ""
        echo "💾 Your macros are preserved in:"
        echo "   $MACROS_DIR"
        echo "   You can restore them if you reinstall Commander"
    fi
    
    echo ""
    echo "Thank you for using Commander! 🎨"
else
    echo "❌ Uninstallation may not have completed successfully"
    echo "   Please check: $COMMANDER_DIR"
    exit 1
fi
