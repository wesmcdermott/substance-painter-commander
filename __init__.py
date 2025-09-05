# --- BLACK BOX LOGGING (with permission handling) ---
import os, sys, signal, atexit, tempfile
import faulthandler

# Try Desktop first, fallback to temp directory
try:
    LOG_DIR = os.path.expanduser("~/Desktop")
    # Test write permission
    test_file = os.path.join(LOG_DIR, "commander_test_write")
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
except (PermissionError, OSError):
    LOG_DIR = tempfile.gettempdir()

PY_LOG = os.path.join(LOG_DIR, "commander_plugin_faulthandler.log")
QT_LOG = os.path.join(LOG_DIR, "commander_plugin_qt.log")

# Python stacks on fatal signals (SEGSEGV/ABRT/BUS/ILL) - with error handling
_fh = None
_qt = None
try:
    _fh = open(PY_LOG, "w", buffering=1)
    _fh.write("=== COMMANDER CRASH LOG STARTED ===\n")
    _fh.flush()
    
    faulthandler.enable(_fh)
    for _sig in (signal.SIGSEGV, signal.SIGABRT, signal.SIGBUS, signal.SIGILL):
        faulthandler.register(_sig, _fh, all_threads=True)
    def _atexit_handler():
        if _fh:
            _fh.write("=== ATEXIT HANDLER CALLED ===\n")
            _fh.flush()
        print("Commander: atexit handler called - Python process ending normally")
    atexit.register(_atexit_handler)

    # Qt messages to file
    _qt = open(QT_LOG, "w", buffering=1)
    _qt.write("=== COMMANDER QT LOG STARTED ===\n")
    _qt.flush()
    
    def _qt_msg(mode, ctx, msg):
        try:
            if _qt:
                _qt.write(f"[QT][{mode}] {msg}\n")
                _qt.flush()  # Force immediate write
        except Exception:
            pass
    
    print(f"Commander: Crash logging initialized successfully")
    print(f"Python log: {PY_LOG}")
    print(f"Qt log: {QT_LOG}")
            
except Exception as e:
    # Fallback: disable logging if it fails
    print(f"Commander: Could not initialize crash logging: {e}")
    _fh = None
    _qt = None
    def _qt_msg(mode, ctx, msg):
        pass

# Commander plugin with hardened popup
from PySide6 import QtWidgets, QtCore, QtGui
import substance_painter.ui
import substance_painter.logging
import json
import os

# Install Qt message handler
try:
    QtCore.qInstallMessageHandler(_qt_msg)
    print(f"Commander: Qt message handler installed, logging to: {QT_LOG if _qt else 'disabled'}")
except Exception as e:
    print(f"Commander: Failed to install Qt message handler: {e}")
import substance_painter.layerstack
import substance_painter.textureset
import substance_painter.resource
from substance_painter.layerstack import (
    InsertPosition, NodeStack, MaskBackground, GeometryMaskType, ProjectionMode,
    SelectionType, BlendingMode, delete_node, get_selected_nodes, set_selected_nodes, set_selection_type,
    insert_fill, insert_paint, insert_group, instantiate,
    insert_levels_effect, insert_compare_mask_effect, insert_filter_effect,
    insert_generator_effect, insert_anchor_point_effect, insert_color_selection_effect,
    insert_smart_material, insert_smart_mask, create_smart_material, create_smart_mask
)
from substance_painter.textureset import ChannelType
from substance_painter.ui import UIMode

# Global references - BACK TO STABLE DOCK WIDGET
COMMANDER_WIDGET = None
COMMANDER_SHORTCUT = None
DOCK_WIDGET = None

class MacroCreationDialog(QtWidgets.QDialog):
    """Advanced dialog for creating macros with hotkey assignment"""
    
    def __init__(self, parent, selected_commands):
        super().__init__(parent)
        self.selected_commands = selected_commands
        self.hotkey_sequence = None
        self.setupUI()
    
    def setupUI(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Create Macro")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QtWidgets.QVBoxLayout()
        
        # Commands preview
        commands_label = QtWidgets.QLabel("Commands in this macro:")
        commands_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(commands_label)
        
        commands_list = QtWidgets.QTextEdit()
        commands_list.setReadOnly(True)
        commands_list.setMaximumHeight(100)
        commands_text = "\n".join([f"• {cmd}" for cmd in self.selected_commands])
        commands_list.setText(commands_text)
        layout.addWidget(commands_list)
        
        # Macro name input
        name_label = QtWidgets.QLabel("Macro name:")
        name_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(name_label)
        
        self.name_input = QtWidgets.QLineEdit()
        self.name_input.setPlaceholderText("Enter macro name...")
        layout.addWidget(self.name_input)
        
        # Hotkey assignment
        hotkey_label = QtWidgets.QLabel("Hotkey (optional):")
        hotkey_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(hotkey_label)
        
        hotkey_layout = QtWidgets.QHBoxLayout()
        
        self.hotkey_input = QtWidgets.QLineEdit()
        self.hotkey_input.setReadOnly(True)
        self.hotkey_input.setPlaceholderText("Click 'Record Hotkey' and press keys...")
        hotkey_layout.addWidget(self.hotkey_input)
        
        self.record_button = QtWidgets.QPushButton("Record Hotkey")
        self.record_button.clicked.connect(self.record_hotkey)
        hotkey_layout.addWidget(self.record_button)
        
        self.clear_hotkey_button = QtWidgets.QPushButton("Clear")
        self.clear_hotkey_button.clicked.connect(self.clear_hotkey)
        hotkey_layout.addWidget(self.clear_hotkey_button)
        
        layout.addLayout(hotkey_layout)
        
        # Help text
        help_text = QtWidgets.QLabel(
            "Examples: F5, Ctrl+Shift+W, Alt+Q, Shift+F1\n" +
            "Avoid conflicts with Substance Painter shortcuts."
        )
        help_text.setStyleSheet("color: #888; font-size: 11px; margin-top: 5px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        
        cancel_button = QtWidgets.QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        self.create_button = QtWidgets.QPushButton("Create Macro")
        self.create_button.clicked.connect(self.accept)
        self.create_button.setDefault(True)
        button_layout.addWidget(self.create_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Focus on name input
        self.name_input.setFocus()
    
    def record_hotkey(self):
        """Record a hotkey sequence"""
        self.record_button.setText("Press keys...")
        self.record_button.setEnabled(False)
        self.hotkey_input.setText("Listening for keys...")
        
        # Install event filter to capture key sequence
        self.installEventFilter(self)
        self.grabKeyboard()
    
    def eventFilter(self, obj, event):
        """Capture keyboard events for hotkey recording"""
        if event.type() == QtCore.QEvent.Type.KeyPress:
            key = event.key()
            modifiers = event.modifiers()
            
            # Ignore standalone modifier keys
            if key in (QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_Alt, 
                      QtCore.Qt.Key.Key_Shift, QtCore.Qt.Key.Key_Meta):
                return False
            
            # Build key sequence
            modifier_names = []
            if modifiers & QtCore.Qt.KeyboardModifier.ControlModifier:
                modifier_names.append("Ctrl")
            if modifiers & QtCore.Qt.KeyboardModifier.AltModifier:
                modifier_names.append("Alt")
            if modifiers & QtCore.Qt.KeyboardModifier.ShiftModifier:
                modifier_names.append("Shift")
            if modifiers & QtCore.Qt.KeyboardModifier.MetaModifier:
                modifier_names.append("Meta")
            
            # Get key name
            key_name = ""
            if key == QtCore.Qt.Key.Key_F1: key_name = "F1"
            elif key == QtCore.Qt.Key.Key_F2: key_name = "F2"
            elif key == QtCore.Qt.Key.Key_F3: key_name = "F3"
            elif key == QtCore.Qt.Key.Key_F4: key_name = "F4"
            elif key == QtCore.Qt.Key.Key_F5: key_name = "F5"
            elif key == QtCore.Qt.Key.Key_F6: key_name = "F6"
            elif key == QtCore.Qt.Key.Key_F7: key_name = "F7"
            elif key == QtCore.Qt.Key.Key_F8: key_name = "F8"
            elif key == QtCore.Qt.Key.Key_F9: key_name = "F9"
            elif key == QtCore.Qt.Key.Key_F10: key_name = "F10"
            elif key == QtCore.Qt.Key.Key_F11: key_name = "F11"
            elif key == QtCore.Qt.Key.Key_F12: key_name = "F12"
            else:
                # Convert to character
                key_name = QtGui.QKeySequence(key).toString()
            
            sequence_text = "+".join(modifier_names + [key_name]) if modifier_names else key_name
            
            if sequence_text:
                self.hotkey_sequence = sequence_text
                self.hotkey_input.setText(sequence_text)
            
            # Stop recording
            self.releaseKeyboard()
            self.removeEventFilter(self)
            self.record_button.setText("Record Hotkey")
            self.record_button.setEnabled(True)
            
            return True
        
        return False
    
    def clear_hotkey(self):
        """Clear the hotkey"""
        self.hotkey_sequence = None
        self.hotkey_input.clear()
    
    def get_macro_name(self):
        """Get the macro name"""
        return self.name_input.text().strip()
    
    def get_hotkey(self):
        """Get the hotkey"""
        return self.hotkey_sequence

class CommanderWidget(QtWidgets.QWidget):
    """Stable dock widget - no crashes!"""

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set required properties for dock widget
        self.setObjectName("CommanderWidget") 
        self.setWindowTitle("Commander")
        
        # Simple layout
        layout = QtWidgets.QVBoxLayout()
        
        # Search input
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search commands and procedurals...")
        layout.addWidget(self.search_input)
        
        # Results list 
        self.results_list = QtWidgets.QListWidget()
        layout.addWidget(self.results_list)
        
        # Macro controls
        macro_layout = QtWidgets.QHBoxLayout()
        
        self.create_macro_button = QtWidgets.QPushButton("Create Macro")
        self.create_macro_button.clicked.connect(self.start_macro_creation)
        macro_layout.addWidget(self.create_macro_button)
        
        self.cancel_macro_button = QtWidgets.QPushButton("Cancel")
        self.cancel_macro_button.clicked.connect(self.cancel_macro_creation)
        self.cancel_macro_button.setVisible(False)
        macro_layout.addWidget(self.cancel_macro_button)
        
        layout.addLayout(macro_layout)
        
        # Procedural refresh controls
        procedural_layout = QtWidgets.QHBoxLayout()
        
        self.refresh_procedurals_button = QtWidgets.QPushButton("Refresh Procedurals")
        self.refresh_procedurals_button.clicked.connect(self.refresh_procedurals)
        self.refresh_procedurals_button.setToolTip("Reload procedural resources from Substance Painter")
        procedural_layout.addWidget(self.refresh_procedurals_button)
        
        layout.addLayout(procedural_layout)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Ready")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Connect events
        self.search_input.textChanged.connect(self.on_search_changed)
        self.results_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.results_list.itemClicked.connect(self.on_single_click)
        
        # Install event filter on search input to capture arrow keys
        self.search_input.installEventFilter(self)
        
        # Context menu
        self.results_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Initialize macro system BEFORE refreshing commands (since refresh_commands uses self.macros)
        self.macro_creation_mode = False
        self.selected_commands = []
        self.macros = {}
        self.macros_file = self._get_macros_file_path()
        self.load_macros()
        
        # Initialize procedural loading state
        self.procedurals_loaded = False
        self.procedurals_cache = []
        
        # Project monitoring
        self.last_project_state = None
        
        # Initialize with commands (now that macros are loaded)
        self.refresh_commands()
        
        # Start project monitoring for automatic procedural loading
        self.start_project_monitoring()
    
    def eventFilter(self, obj, event):
        """Event filter to intercept key events from search input"""
        if obj == self.search_input and event.type() == QtCore.QEvent.Type.KeyPress:
            key = event.key()
            
            if key == QtCore.Qt.Key_Down:
                # Down arrow pressed in search field - jump to results
                self._jump_to_results()
                return True  # Event handled
            elif key == QtCore.Qt.Key_Up:
                # Up arrow in search field - also jump to results (last item)
                self._jump_to_results(select_last=True)
                return True  # Event handled
            elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
                # Enter in search field - execute first visible item
                if self.results_list.count() > 0:
                    for i in range(self.results_list.count()):
                        item = self.results_list.item(i)
                        if not item.isHidden():
                            self.on_item_double_clicked(item)
                            break
                return True  # Event handled
                
        # Pass the event to the parent class
        return super().eventFilter(obj, event)
        
    def keyPressEvent(self, event):
        """Enhanced key press handler for results list navigation"""
        key = event.key()
        
        if key == QtCore.Qt.Key_Escape:
            # Hide dock on ESC
            global DOCK_WIDGET
            if DOCK_WIDGET:
                DOCK_WIDGET.hide()
                
        elif key == QtCore.Qt.Key_Down and self.results_list.hasFocus():
            # Arrow down in results - navigate to next item
            self._navigate_results(1)
            
        elif key == QtCore.Qt.Key_Up and self.results_list.hasFocus():
            # Arrow up in results - navigate to previous item
            self._navigate_results(-1)
            
        elif key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            # Enter key - execute selected command
            if self.results_list.hasFocus():
                current_item = self.results_list.currentItem()
                if current_item:
                    self.on_item_double_clicked(current_item)
            
        else:
            # For any other key, make sure search input gets focus for typing
            if not self.search_input.hasFocus() and event.text().isprintable():
                self.search_input.setFocus()
                # Re-send the key event to the search input
                QtWidgets.QApplication.sendEvent(self.search_input, event)
                return
            super().keyPressEvent(event)
    
    def _navigate_results(self, direction):
        """Navigate through visible items only (direction: 1 for down, -1 for up)"""
        if self.results_list.count() == 0:
            return
            
        # Get list of visible rows
        visible_rows = []
        for i in range(self.results_list.count()):
            if not self.results_list.item(i).isHidden():
                visible_rows.append(i)
        
        if not visible_rows:
            return
            
        # Find current position in visible items
        current_row = self.results_list.currentRow()
        try:
            current_visible_index = visible_rows.index(current_row)
        except ValueError:
            # Current row not visible, start from first/last
            current_visible_index = 0 if direction > 0 else len(visible_rows) - 1
        else:
            # Move to next/previous visible item
            current_visible_index += direction
            
        # Wrap around if needed
        if current_visible_index >= len(visible_rows):
            current_visible_index = 0
        elif current_visible_index < 0:
            current_visible_index = len(visible_rows) - 1
            
        # Select the new row
        new_row = visible_rows[current_visible_index]
        self.results_list.setCurrentRow(new_row)
        
        # Scroll to make sure it's visible
        self.results_list.scrollToItem(self.results_list.item(new_row))
        
        # Focus stays on results list for continued navigation
    
    def _jump_to_results(self, select_last=False):
        """Jump from search field to results list and select first/last visible item"""
        if self.results_list.count() == 0:
            return
            
        # Find visible items
        visible_items = []
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if not item.isHidden():
                visible_items.append((i, item))
        
        if not visible_items:
            return
            
        # Select first or last visible item
        if select_last:
            index, item = visible_items[-1]  # Last visible item
        else:
            index, item = visible_items[0]   # First visible item
            
        self.results_list.setCurrentItem(item)
        self.results_list.scrollToItem(item)
        self.results_list.setFocus()
    
    
    # ---- Core Commander functionality ----
    
    def refresh_commands(self, force_reload_procedurals=False):
        """Populate the list with ALL available layer commands from API"""
        self.results_list.clear()
        
        commands = [
            # === Layer Creation (Real API: insert_*) ===
            "Create Paint Layer",           # → insert_paint()
            "Create Fill Layer",            # → insert_fill()
            "Create Group Layer",           # → insert_group()
            "Create Layer Instance",        # → instantiate()
            
            # === Effect Creation (Real API: insert_*_effect) ===
            "Insert Levels Effect",         # → insert_levels_effect()
            "Insert Filter Effect",         # → insert_filter_effect()
            "Insert Fill Effect",           # → insert_fill() (creates FillEffectNode when in effect stack)
            "Insert Paint Effect",          # → insert_paint() (creates PaintEffectNode when in effect stack)
            "Insert Generator Effect",      # → insert_generator_effect()
            "Insert Compare Mask Effect",   # → insert_compare_mask_effect()
            "Insert Color Selection Effect", # → insert_color_selection_effect()
            "Insert Anchor Point Effect",   # → insert_anchor_point_effect()
            
            # === Layer Management (Real API) ===
            "Delete Selected Layers",      # → delete_node()
            "Rename Selected Layer",       # → node.set_name()
            
            # === Layer Properties (Real API: Node methods) ===
            "Toggle Layer Visibility",     # → node.set_visible()
            "Show Layer",                  # → node.set_visible(True)
            "Hide Layer",                  # → node.set_visible(False)
            "Set Layer Opacity",          # → node.set_opacity()
            "Get Layer Opacity",          # → node.get_opacity()
            "Set Blend Mode",              # → node.set_blending_mode()
            "Get Blend Mode",              # → node.get_blending_mode()
            
            # === Layer Masks (Real API: LayerNode methods) ===
            "Add Layer Mask",             # → layer.add_mask()
            "Remove Layer Mask",          # → layer.remove_mask()
            "Enable Layer Mask",          # → layer.enable_mask(True)
            "Disable Layer Mask",         # → layer.enable_mask(False)
            "Set Mask Background White",  # → layer.set_mask_background(MaskBackground.White)
            "Set Mask Background Black",  # → layer.set_mask_background(MaskBackground.Black)
            
            # === Smart Materials/Masks (Real API) ===
            "Insert Smart Material",      # → insert_smart_material()
            "Create Smart Material",      # → create_smart_material()
            "Insert Smart Mask",          # → insert_smart_mask()
            "Create Smart Mask",          # → create_smart_mask()
            
            # === Geometry Masks (Real API: LayerNode methods) ===
            "Set Geometry Mask Mesh",     # → layer.set_geometry_mask_type(GeometryMaskType.Mesh)
            "Set Geometry Mask UV Tile",  # → layer.set_geometry_mask_type(GeometryMaskType.UVTile)
            "Enable Geometry Mask",       # → layer.set_geometry_mask_enabled_meshes()
            
            # === Projection Modes (Real API: FillParamsEditorMixin) ===
            "Set Projection UV",          # → layer.set_projection_mode(ProjectionMode.UV)
            "Set Projection Triplanar",   # → layer.set_projection_mode(ProjectionMode.Triplanar)
            "Set Projection Planar",      # → layer.set_projection_mode(ProjectionMode.Planar)
            "Set Projection Spherical",   # → layer.set_projection_mode(ProjectionMode.Spherical)
            "Set Projection Cylindrical", # → layer.set_projection_mode(ProjectionMode.Cylindrical)
            "Enable Symmetry",            # → layer.set_symmetry_enabled(True)
            "Disable Symmetry"            # → layer.set_symmetry_enabled(False)
        ]
        
        for cmd in commands:
            self.results_list.addItem(cmd)
        
        # Add procedural resources with lazy loading
        procedural_count = 0
        try:
            if force_reload_procedurals or not self.procedurals_loaded:
                substance_painter.logging.info("Commander: Loading procedural resources...")
                procedurals = self.get_procedural_resources()
                substance_painter.logging.info(f"Commander: Found {len(procedurals)} procedural resources")
                
                if len(procedurals) > 0:
                    self.procedurals_cache = procedurals
                    self.procedurals_loaded = True
                    substance_painter.logging.info("Commander: Successfully cached procedural resources")
                else:
                    substance_painter.logging.warning("Commander: No procedural resources found - resource system may not be ready yet")
            else:
                procedurals = self.procedurals_cache
                substance_painter.logging.info(f"Commander: Using cached procedural resources ({len(procedurals)} items)")
            
            for procedural in procedurals:
                item = QtWidgets.QListWidgetItem(f"[PROC] {procedural['name']}")
                item.setForeground(QtGui.QBrush(QtGui.QColor(100, 149, 237)))  # Cornflower blue
                item.setToolTip(f"Procedural: {procedural.get('category', 'Unknown')}\nApplies to Roughness channel")
                # Store the resource identifier for later use
                item.setData(QtCore.Qt.UserRole, procedural)
                self.results_list.addItem(item)
                procedural_count += 1
                
        except Exception as e:
            substance_painter.logging.error(f"Commander: Error loading procedural resources: {e}")
            import traceback
            substance_painter.logging.error(f"Commander: Traceback: {traceback.format_exc()}")
        
        # Add macros to the list FIRST (at the top) in yellow
        macro_count = 0
        for macro_name, macro_data in self.macros.items():
            # Display macro with hotkey if it has one
            hotkey_suffix = f" ({macro_data['hotkey']})" if 'hotkey' in macro_data else ""
            display_text = f"[MACRO] {macro_name}{hotkey_suffix}"
            
            item = QtWidgets.QListWidgetItem(display_text)
            item.setForeground(QtGui.QBrush(QtGui.QColor(255, 215, 0)))  # Golden yellow
            self.results_list.insertItem(macro_count, item)  # Insert at top
            macro_count += 1
        
        total_items = len(commands) + procedural_count + macro_count
        status_text = f"Found {total_items} items ({len(commands)} commands, {procedural_count} procedurals, {macro_count} macros)"
        if not self.procedurals_loaded and procedural_count == 0:
            status_text += " - Try 'Refresh Procedurals' if missing"
        self.status_label.setText(status_text)
    
    def on_search_changed(self, text):
        """Filter commands based on search and auto-select first visible item"""
        # Check if user is searching for procedurals but they haven't been loaded yet
        if text.lower() in ['proc', 'procedural', 'noise', 'grunge', 'pattern'] and not self.procedurals_loaded:
            substance_painter.logging.info("Commander: User searching for procedurals - triggering lazy load")
            self.refresh_commands(force_reload_procedurals=True)
        
        first_visible_item = None
        
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            is_match = text.lower() in item.text().lower()
            item.setHidden(not is_match)
            
            # Track first visible item for auto-selection
            if is_match and first_visible_item is None:
                first_visible_item = item
        
        # Auto-select first visible item for easy arrow navigation
        if first_visible_item:
            self.results_list.setCurrentItem(first_visible_item)
        else:
            self.results_list.setCurrentItem(None)
    
    def on_item_double_clicked(self, item):
        """Execute the selected command using official API functions"""
        global DOCK_WIDGET
        command = item.text()
        
        try:
            # Handle macro execution
            if command.startswith("[MACRO]"):
                macro_display = command[7:].strip()  # Remove "[MACRO] " prefix
                
                # Extract actual macro name (remove hotkey suffix if present)
                if '(' in macro_display and macro_display.endswith(')'):
                    macro_name = macro_display.rsplit(' (', 1)[0].strip()
                else:
                    macro_name = macro_display
                
                self.execute_macro(macro_name)
                return
            
            # Handle procedural resources
            elif command.startswith("[PROC]"):
                procedural_data = item.data(QtCore.Qt.UserRole)
                if procedural_data:
                    result = self.apply_procedural(procedural_data)
                    self.status_label.setText(result)
                    # Keep dock open after procedural execution - user can use shortcut to refocus
                else:
                    raise ValueError("No procedural data found")
                return
            
            # === Layer Creation Commands ===
            if command == "Create Paint Layer":
                self.create_paint_layer()
            elif command == "Create Fill Layer":
                self.create_fill_layer()
            elif command == "Create Group Layer":
                self.create_group_layer()
            elif command == "Create Layer Instance":
                self.create_instance_layer()
                
            # === Effect Commands ===  
            elif command == "Insert Fill Effect":
                self.insert_fill_effect()
            elif command == "Insert Paint Effect":
                self.insert_paint_effect()
            elif command == "Insert Levels Effect":
                self.insert_levels_effect()
            elif command == "Insert Compare Mask Effect":
                self.insert_compare_mask_effect()
            elif command == "Insert Filter Effect":
                self.insert_filter_effect()
            elif command == "Insert Generator Effect":
                self.insert_generator_effect()
            elif command == "Insert Anchor Point Effect":
                self.insert_anchor_point_effect()
            elif command == "Insert Color Selection Effect":
                self.insert_color_selection_effect()
                
            # === Layer Management ===
            elif command == "Delete Selected Layers":
                self.delete_selected()
            elif command == "Rename Selected Layer":
                self.rename_selected_layer()
                
            # === Layer Properties ===
            elif command == "Toggle Layer Visibility":
                self.toggle_layer_visibility()
            elif command == "Show Layer":
                self.show_layer()
            elif command == "Hide Layer":
                self.hide_layer()
            elif command == "Set Layer Opacity":
                self.set_layer_opacity()
            elif command == "Get Layer Opacity":
                self.get_layer_opacity()
            elif command == "Set Blend Mode":
                self.set_blend_mode()
            elif command == "Get Blend Mode":
                self.get_blend_mode()
                
            # === Mask Operations ===
            elif command == "Add Layer Mask":
                self.add_layer_mask()
            elif command == "Remove Layer Mask":
                self.remove_layer_mask()
            elif command == "Enable Layer Mask":
                self.enable_layer_mask()
            elif command == "Disable Layer Mask":
                self.disable_layer_mask()
            elif command == "Set Mask Background White":
                self.set_mask_white()
            elif command == "Set Mask Background Black":
                self.set_mask_black()
                
            # === Smart Materials/Masks ===
            elif command == "Insert Smart Material":
                self.insert_smart_material()
            elif command == "Create Smart Material":
                self.create_smart_material()
            elif command == "Insert Smart Mask":
                self.insert_smart_mask()
            elif command == "Create Smart Mask":
                self.create_smart_mask()
                
            # === Geometry Masks ===
            elif command == "Set Geometry Mask Mesh":
                self.set_geometry_mask_mesh()
            elif command == "Set Geometry Mask UV Tile":
                self.set_geometry_mask_uv_tile()
            elif command == "Enable Geometry Mask":
                self.enable_geometry_mask()
                
            # === Projection Modes ===
            elif command == "Set Projection UV":
                self.set_projection_uv()
            elif command == "Set Projection Triplanar":
                self.set_projection_triplanar()
            elif command == "Set Projection Planar":
                self.set_projection_planar()
            elif command == "Set Projection Spherical":
                self.set_projection_spherical()
            elif command == "Set Projection Cylindrical":
                self.set_projection_cylindrical()
            elif command == "Enable Symmetry":
                self.enable_symmetry()
            elif command == "Disable Symmetry":
                self.disable_symmetry()
                
            # === Selection ===
            elif command == "Select Content":
                self.select_content()
            elif command == "Select Mask":
                self.select_mask()
            elif command == "Select Properties":
                self.select_properties()
            else:
                raise ValueError(f"Unknown command: {command}")
                
            self.status_label.setText(f"✓ Executed: {command}")
            # Keep dock open after execution - user can use shortcut to refocus
            
        except Exception as e:
            self.status_label.setText(f"✗ Failed: {command}")
            substance_painter.logging.error(f"Command failed: {e}")
    
    # ---- Macro System Methods ----
    
    def _get_macros_file_path(self):
        """Get the path for the macros file"""
        try:
            import substance_painter.application
            app_data = substance_painter.application.application_data_folder()
            return os.path.join(app_data, "commander_macros.json")
        except:
            # Fallback to user home directory
            return os.path.expanduser("~/commander_macros.json")
    
    def load_macros(self):
        """Load macros from file and register their hotkeys"""
        try:
            if os.path.exists(self.macros_file):
                with open(self.macros_file, 'r') as f:
                    self.macros = json.load(f)
                
                # Register hotkeys for existing macros
                hotkey_count = 0
                for macro_name, macro_data in self.macros.items():
                    if 'hotkey' in macro_data:
                        self.register_macro_hotkey(macro_name, macro_data['hotkey'])
                        hotkey_count += 1
                
                substance_painter.logging.info(f"Loaded {len(self.macros)} macros ({hotkey_count} with hotkeys)")
            else:
                self.macros = {}
                substance_painter.logging.info("No macros file found, starting with empty macros")
        except Exception as e:
            substance_painter.logging.error(f"Failed to load macros: {str(e)}")
            self.macros = {}
    
    def save_macros(self):
        """Save macros to file"""
        try:
            with open(self.macros_file, 'w') as f:
                json.dump(self.macros, f, indent=2)
            substance_painter.logging.info(f"Saved {len(self.macros)} macros")
        except Exception as e:
            substance_painter.logging.error(f"Failed to save macros: {str(e)}")
    
    def is_hotkey_conflict(self, hotkey, macro_name):
        """Check if hotkey conflicts with existing assignments"""
        # Check against other macros
        for name, macro_data in self.macros.items():
            if name != macro_name and 'hotkey' in macro_data:
                if macro_data['hotkey'] == hotkey:
                    reply = QtWidgets.QMessageBox.question(
                        self, "Hotkey Conflict",
                        f"Hotkey '{hotkey}' is already assigned to macro '{name}'.\n" +
                        f"Remove it from '{name}' and assign to '{macro_name}'?",
                        QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
                    )
                    if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                        # Remove from old macro
                        self.unregister_macro_hotkey(name)
                        del self.macros[name]['hotkey']
                        return False  # No conflict, we resolved it
                    else:
                        return True  # Conflict, user declined to resolve
        
        # Check against known Substance Painter shortcuts
        sp_shortcuts = [
            'Ctrl+N', 'Ctrl+O', 'Ctrl+S', 'Ctrl+Z', 'Ctrl+Y', 'Ctrl+C', 'Ctrl+V', 'Ctrl+X',
            'Ctrl+A', 'F1', 'F11', 'Ctrl+Shift+S', 'Ctrl+R', 'Space'
        ]
        
        if hotkey in sp_shortcuts:
            reply = QtWidgets.QMessageBox.question(
                self, "Potential Conflict",
                f"Hotkey '{hotkey}' might conflict with Substance Painter.\n" +
                "Use it anyway?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            return reply != QtWidgets.QMessageBox.StandardButton.Yes
        
        return False  # No conflict
    
    def register_macro_hotkey(self, macro_name, hotkey):
        """Register a hotkey for a macro"""
        try:
            # Create QShortcut and connect to macro execution
            main_window = substance_painter.ui.get_main_window()
            shortcut = QtGui.QShortcut(QtGui.QKeySequence(hotkey), main_window)
            shortcut.activated.connect(lambda: self.execute_macro_by_name(macro_name))
            
            # Store shortcut reference for later cleanup
            if not hasattr(self, 'macro_shortcuts'):
                self.macro_shortcuts = {}
            self.macro_shortcuts[macro_name] = shortcut
            
            substance_painter.logging.info(f"Registered hotkey '{hotkey}' for macro '{macro_name}'")
        except Exception as e:
            substance_painter.logging.error(f"Failed to register hotkey for macro '{macro_name}': {e}")
    
    def unregister_macro_hotkey(self, macro_name):
        """Unregister a hotkey for a macro"""
        try:
            if hasattr(self, 'macro_shortcuts') and macro_name in self.macro_shortcuts:
                shortcut = self.macro_shortcuts[macro_name]
                shortcut.activated.disconnect()
                shortcut.setParent(None)
                shortcut.deleteLater()
                del self.macro_shortcuts[macro_name]
                substance_painter.logging.info(f"Unregistered hotkey for macro '{macro_name}'")
        except Exception as e:
            substance_painter.logging.error(f"Failed to unregister hotkey for macro '{macro_name}': {e}")
    
    def execute_macro_by_name(self, macro_name):
        """Execute a macro by name (called by hotkey)"""
        if macro_name in self.macros:
            substance_painter.logging.info(f"Executing macro '{macro_name}' via hotkey")
            self.execute_macro(macro_name)
        else:
            substance_painter.logging.error(f"Macro '{macro_name}' not found")
    
    def start_macro_creation(self):
        """Start macro creation mode"""
        self.macro_creation_mode = True
        self.selected_commands = []
        self.status_label.setText("Macro Creation Mode: Click commands to select")
        substance_painter.logging.info("Started macro creation mode")
        
        # Update UI
        self.create_macro_button.setText("Done Selecting")
        self.create_macro_button.clicked.disconnect()
        self.create_macro_button.clicked.connect(self.finish_macro_creation)
        self.cancel_macro_button.setVisible(True)
    
    def cancel_macro_creation(self):
        """Cancel macro creation mode"""
        self.macro_creation_mode = False
        self.selected_commands = []
        self.status_label.setText("Macro creation cancelled")
        substance_painter.logging.info("Cancelled macro creation mode")
        
        # Reset UI
        self.create_macro_button.setText("Create Macro")
        self.create_macro_button.clicked.disconnect()
        self.create_macro_button.clicked.connect(self.start_macro_creation)
        self.cancel_macro_button.setVisible(False)
        
        # Refresh to restore normal colors
        self.refresh_commands()
    
    def finish_macro_creation(self):
        """Finish selecting commands and create macro"""
        if len(self.selected_commands) == 0:
            QtWidgets.QMessageBox.warning(self, "No Commands", "Please select some commands first.")
            return
        
        # Use advanced macro creation dialog
        dialog = MacroCreationDialog(self, self.selected_commands)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name = dialog.get_macro_name()
            hotkey = dialog.get_hotkey()
            if name:
                self.create_macro(name, hotkey)
    
    def create_macro(self, name, hotkey=None):
        """Create a macro with the selected commands and optional hotkey"""
        if name in self.macros:
            reply = QtWidgets.QMessageBox.question(
                self, "Macro Exists", 
                f"Macro '{name}' already exists. Replace it?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                return
        
        # Check hotkey conflicts
        if hotkey and self.is_hotkey_conflict(hotkey, name):
            return
        
        # Save macro
        macro_data = {
            'commands': self.selected_commands.copy()
        }
        if hotkey:
            macro_data['hotkey'] = hotkey
        
        self.macros[name] = macro_data
        self.save_macros()
        
        # Register hotkey if provided
        if hotkey:
            self.register_macro_hotkey(name, hotkey)
        
        # Reset UI
        self.cancel_macro_creation()
        
        hotkey_text = f" with hotkey {hotkey}" if hotkey else ""
        self.status_label.setText(f"Created macro '{name}'{hotkey_text} with {len(self.selected_commands)} commands")
        substance_painter.logging.info(f"Created macro '{name}'{hotkey_text} with {len(self.selected_commands)} commands")
        
        # Refresh to show new macro
        self.refresh_commands()
    
    def on_single_click(self, item):
        """Handle single-click for macro creation"""
        if self.macro_creation_mode:
            command = item.text()
            
            # Skip macro items themselves
            if command.startswith("[MACRO]"):
                return
            
            # Toggle selection
            if command in self.selected_commands:
                self.selected_commands.remove(command)
                # Remove visual feedback
                item.setForeground(QtGui.QBrush(QtCore.Qt.GlobalColor.white))
            else:
                self.selected_commands.append(command)
                # Add visual feedback (golden yellow)
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 215, 0)))
            
            self.status_label.setText(f"Macro Mode: {len(self.selected_commands)} commands selected")
    
    def show_context_menu(self, position):
        """Show right-click context menu"""
        item = self.results_list.itemAt(position)
        if not item:
            return
            
        menu = QtWidgets.QMenu(self)
        command = item.text()
        
        if command.startswith("[MACRO]"):
            # Context menu for existing macros
            macro_display = command[7:].strip()  # Remove "[MACRO] " prefix
            
            # Extract actual macro name (remove hotkey suffix if present)
            if '(' in macro_display and macro_display.endswith(')'):
                macro_name = macro_display.rsplit(' (', 1)[0].strip()
            else:
                macro_name = macro_display
            
            execute_action = menu.addAction("Execute Macro")
            execute_action.triggered.connect(lambda: self.execute_macro(macro_name))
            
            # Hotkey management
            macro_data = self.macros.get(macro_name, {})
            if 'hotkey' in macro_data:
                remove_hotkey_action = menu.addAction(f"Remove Hotkey ({macro_data['hotkey']})")
                remove_hotkey_action.triggered.connect(lambda: self.remove_macro_hotkey(macro_name))
            else:
                add_hotkey_action = menu.addAction("Add Hotkey")
                add_hotkey_action.triggered.connect(lambda: self.add_macro_hotkey(macro_name))
            
            menu.addSeparator()
            delete_action = menu.addAction("Delete Macro")
            delete_action.triggered.connect(lambda: self.delete_macro(macro_name))
        
        else:
            # Context menu for regular commands
            if not self.macro_creation_mode:
                create_action = menu.addAction("Create Macro from this Command")
                create_action.triggered.connect(lambda: self.create_single_command_macro(command))
        
        menu.exec(self.results_list.mapToGlobal(position))
    
    def create_single_command_macro(self, command):
        """Create a macro from a single command using advanced dialog"""
        dialog = MacroCreationDialog(self, [command])
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name = dialog.get_macro_name()
            hotkey = dialog.get_hotkey()
            if name:
                # Check hotkey conflicts
                if hotkey and self.is_hotkey_conflict(hotkey, name):
                    return
                
                # Save macro
                macro_data = {'commands': [command]}
                if hotkey:
                    macro_data['hotkey'] = hotkey
                
                self.macros[name] = macro_data
                self.save_macros()
                
                # Register hotkey if provided
                if hotkey:
                    self.register_macro_hotkey(name, hotkey)
                
                hotkey_text = f" with hotkey {hotkey}" if hotkey else ""
                self.status_label.setText(f"Created macro '{name}'{hotkey_text} with 1 command")
                self.refresh_commands()
    
    def execute_macro(self, name):
        """Execute a macro by running all its commands in sequence"""
        if name not in self.macros:
            substance_painter.logging.error(f"Macro '{name}' not found")
            return False
        
        macro = self.macros[name]
        commands = macro['commands']
        substance_painter.logging.info(f"Executing macro '{name}' with {len(commands)} commands")
        
        success_count = 0
        failed_commands = []
        
        for i, command in enumerate(commands):
            try:
                substance_painter.logging.info(f"  [{i+1}/{len(commands)}] {command}")
                
                # Find and execute the command
                if command.startswith("[PROC]"):
                    # Handle procedural command
                    success = self.execute_procedural_from_command(command)
                else:
                    # Handle regular command
                    success = self.execute_single_command(command)
                
                if success:
                    success_count += 1
                else:
                    failed_commands.append(command)
                    
            except Exception as e:
                failed_commands.append(command)
                substance_painter.logging.error(f"    Error: {e}")
        
        # Report results
        if failed_commands:
            self.status_label.setText(f"Macro '{name}': {success_count}/{len(commands)} succeeded")
        else:
            self.status_label.setText(f"Macro '{name}': All {len(commands)} commands succeeded")
        
        return len(failed_commands) == 0
    
    def execute_single_command(self, command):
        """Execute a single command (used by macro execution)"""
        try:
            # Create a temporary list item to use existing execute logic
            temp_item = QtWidgets.QListWidgetItem(command)
            
            # For procedural commands, we need to set the user data
            if command.startswith("[PROC]"):
                proc_name = command[7:].strip()
                # Find the procedural in our list
                for proc in self.get_procedural_resources():
                    if proc['name'] == proc_name:
                        temp_item.setData(QtCore.Qt.UserRole, proc)
                        break
            
            self.on_item_double_clicked(temp_item)
            return True
        except Exception as e:
            substance_painter.logging.error(f"Failed to execute command '{command}': {e}")
            return False
    
    def execute_procedural_from_command(self, command):
        """Execute a procedural command from a macro"""
        try:
            proc_name = command[7:].strip()  # Remove "[PROC] " prefix
            # Find the matching procedural resource
            for proc in self.get_procedural_resources():
                if proc['name'] == proc_name:
                    result = self.apply_procedural(proc)
                    return True
            return False
        except Exception as e:
            substance_painter.logging.error(f"Failed to execute procedural '{command}': {e}")
            return False
    
    def delete_macro(self, name):
        """Delete a macro"""
        reply = QtWidgets.QMessageBox.question(
            self, "Delete Macro", 
            f"Are you sure you want to delete macro '{name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if name in self.macros:
                # Unregister hotkey if it exists
                self.unregister_macro_hotkey(name)
                del self.macros[name]
                self.save_macros()
                self.status_label.setText(f"Deleted macro '{name}'")
                self.refresh_commands()
    
    def add_macro_hotkey(self, macro_name):
        """Add a hotkey to an existing macro"""
        # Simple hotkey input dialog
        hotkey, ok = QtWidgets.QInputDialog.getText(
            self, "Add Hotkey", 
            f"Enter hotkey for macro '{macro_name}':\n" +
            "(Examples: F5, Ctrl+Shift+W, Alt+Q)"
        )
        
        if ok and hotkey.strip():
            hotkey = hotkey.strip()
            if self.is_hotkey_conflict(hotkey, macro_name):
                return
            
            # Add hotkey to macro
            self.macros[macro_name]['hotkey'] = hotkey
            self.save_macros()
            self.register_macro_hotkey(macro_name, hotkey)
            
            self.status_label.setText(f"Added hotkey '{hotkey}' to macro '{macro_name}'")
            self.refresh_commands()
    
    def remove_macro_hotkey(self, macro_name):
        """Remove a hotkey from a macro"""
        reply = QtWidgets.QMessageBox.question(
            self, "Remove Hotkey", 
            f"Remove hotkey from macro '{macro_name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if macro_name in self.macros and 'hotkey' in self.macros[macro_name]:
                self.unregister_macro_hotkey(macro_name)
                del self.macros[macro_name]['hotkey']
                self.save_macros()
                self.refresh_commands()
                self.status_label.setText(f"Removed hotkey for '{macro_name}'")
    
    # ---- End Macro System ----
    
    def refresh_procedurals(self):
        """Refresh procedural resources on demand"""
        try:
            self.status_label.setText("Refreshing procedural resources...")
            # Force a fresh reload of procedurals
            self.procedurals_loaded = False
            self.procedurals_cache = []
            
            # Refresh the command list which will reload procedurals
            self.refresh_commands(force_reload_procedurals=True)
            
            # Update button text temporarily to show success
            original_text = self.refresh_procedurals_button.text()
            self.refresh_procedurals_button.setText("✓ Refreshed!")
            
            # Timer to reset button text
            QtCore.QTimer.singleShot(2000, lambda: self.refresh_procedurals_button.setText(original_text))
            
            substance_painter.logging.info("Commander: Manual procedural refresh completed")
            
        except Exception as e:
            self.status_label.setText(f"Error refreshing procedurals: {str(e)}")
            substance_painter.logging.error(f"Commander: Error during manual procedural refresh: {e}")
    
    # ---- End Procedural System ----
    
    def set_layer_opacity(self):
        """Set opacity for selected layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if layer.has_blending():
                # Prompt user for opacity value
                opacity, ok = QtWidgets.QInputDialog.getDouble(
                    self, "Set Layer Opacity", "Enter opacity (0.0 - 1.0):",
                    layer.get_opacity() if not layer.is_in_mask_stack() else layer.get_opacity(),
                    0.0, 1.0, 2
                )
                if ok:
                    if layer.is_in_mask_stack():
                        layer.set_opacity(opacity)  # No channel needed for mask
                        substance_painter.logging.info(f"Set mask opacity to {opacity}")
                    else:
                        # For content layers, prompt for channel or apply to all channels
                        layer.set_opacity(opacity)  # This will apply to all channels if no channel specified
                        substance_painter.logging.info(f"Set layer opacity to {opacity}")
            else:
                raise ValueError("Selected layer does not support opacity")
        else:
            raise ValueError("No layer selected")
    
    def get_layer_opacity(self):
        """Get opacity of selected layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if layer.has_blending():
                opacity = layer.get_opacity() if layer.is_in_mask_stack() else layer.get_opacity()
                substance_painter.logging.info(f"Layer '{layer.get_name()}' opacity: {opacity}")
                self.status_label.setText(f"Layer opacity: {opacity}")
            else:
                raise ValueError("Selected layer does not support opacity")
        else:
            raise ValueError("No layer selected")
    
    def set_blend_mode(self):
        """Set blend mode for selected layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if layer.has_blending():
                # Get available blend modes
                blend_modes = [
                    "Normal", "PassThrough", "Disable", "Replace", "Multiply", "Divide", 
                    "InverseDivide", "Darken", "Lighten", "LinearDodge", "Subtract", 
                    "InverseSubtract", "Difference", "Exclusion", "SignedAddition", 
                    "Overlay", "Screen", "LinearBurn", "ColorBurn", "ColorDodge", 
                    "SoftLight", "HardLight", "VividLight", "LinearLight", "PinLight", 
                    "Tint", "Saturation", "Color", "Value", "NormalMapCombine", 
                    "NormalMapDetail", "NormalMapInverseDetail"
                ]
                
                # Get current blend mode
                current_mode = layer.get_blending_mode() if layer.is_in_mask_stack() else layer.get_blending_mode()
                current_index = 0
                try:
                    current_index = blend_modes.index(current_mode.name)
                except:
                    pass
                
                # Prompt user for blend mode
                blend_mode_name, ok = QtWidgets.QInputDialog.getItem(
                    self, "Set Blend Mode", "Select blend mode:",
                    blend_modes, current_index, False
                )
                
                if ok and blend_mode_name:
                    # Convert string to BlendingMode enum
                    blend_mode = getattr(BlendingMode, blend_mode_name)
                    
                    if layer.is_in_mask_stack():
                        layer.set_blending_mode(blend_mode)  # No channel needed for mask
                        substance_painter.logging.info(f"Set mask blend mode to {blend_mode_name}")
                    else:
                        layer.set_blending_mode(blend_mode)  # This will apply to all channels if no channel specified
                        substance_painter.logging.info(f"Set layer blend mode to {blend_mode_name}")
            else:
                raise ValueError("Selected layer does not support blending")
        else:
            raise ValueError("No layer selected")
    
    def get_blend_mode(self):
        """Get blend mode of selected layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if layer.has_blending():
                blend_mode = layer.get_blending_mode() if layer.is_in_mask_stack() else layer.get_blending_mode()
                substance_painter.logging.info(f"Layer '{layer.get_name()}' blend mode: {blend_mode.name}")
                self.status_label.setText(f"Layer blend mode: {blend_mode.name}")
            else:
                raise ValueError("Selected layer does not support blending")
        else:
            raise ValueError("No layer selected")
    
    def start_project_monitoring(self):
        """Start monitoring project state changes for automatic procedural loading"""
        try:
            # Create timer for project monitoring
            self.project_timer = QtCore.QTimer()
            self.project_timer.timeout.connect(self.check_project_status)
            self.project_timer.start(2000)  # Check every 2 seconds
            
            # Initial check
            self.check_project_status()
            
            substance_painter.logging.info("Commander: Started project monitoring for automatic procedural loading")
            
        except Exception as e:
            substance_painter.logging.error(f"Commander: Error starting project monitoring: {e}")
    
    def check_project_status(self):
        """Check for project state changes and load procedurals when project opens"""
        try:
            current_state = substance_painter.project.is_open()
            
            # Check for state changes
            if self.last_project_state != current_state:
                if current_state:
                    # Project just opened - perfect time to load procedurals!
                    substance_painter.logging.info("Commander: Project opened - automatically loading procedurals")
                    
                    # Force a fresh reload of procedurals since project context is now available
                    self.procedurals_loaded = False
                    self.procedurals_cache = []
                    self.refresh_commands(force_reload_procedurals=True)
                    
                    substance_painter.logging.info("Commander: Automatic procedural loading completed")
                else:
                    substance_painter.logging.info("Commander: Project closed")
                
                self.last_project_state = current_state
        
        except Exception as e:
            # Don't log monitoring errors as they're not critical and could spam the log
            pass
    
    # ---- End Project Monitoring ----
    
    def create_paint_layer(self):
        """Create a paint layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        insert_position = InsertPosition.from_textureset_stack(stack)
        layer = substance_painter.layerstack.insert_paint(insert_position)
        layer.set_name("Paint Layer")
        
        # Select the newly created layer for macro chaining
        set_selected_nodes([layer])
        substance_painter.logging.info("Created and selected paint layer")
    
    def create_fill_layer(self):
        """Create a fill layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        insert_position = InsertPosition.from_textureset_stack(stack)
        layer = substance_painter.layerstack.insert_fill(insert_position)
        layer.set_name("Fill Layer")
        
        # Select the newly created layer for macro chaining
        set_selected_nodes([layer])
        substance_painter.logging.info("Created and selected fill layer")
    
    def create_group_layer(self):
        """Create a group layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        insert_position = InsertPosition.from_textureset_stack(stack)
        layer = substance_painter.layerstack.insert_group(insert_position)
        layer.set_name("Group")
        
        # Select the newly created layer for macro chaining
        set_selected_nodes([layer])
        substance_painter.logging.info("Created and selected group layer")
    
    def create_instance_layer(self):
        """Create instance layer from selected layer using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            source_layer = selected_nodes[0]
            insert_position = InsertPosition.from_textureset_stack(stack)
            instance = instantiate(insert_position, source_layer)
            instance.set_name(f"Instance of {source_layer.get_name()}")
            
            # Select the newly created instance for macro chaining
            set_selected_nodes([instance])
            substance_painter.logging.info("Created and selected instance layer")
        else:
            raise ValueError("No layer selected to instance")
    
    def insert_smart_material(self):
        """Insert smart material - requires resource selection (simplified for now)"""
        stack = substance_painter.textureset.get_active_stack()
        insert_position = InsertPosition.from_textureset_stack(stack)
        # Note: This would require resource selection UI in full implementation
        raise ValueError("Smart Material insertion requires resource selection (not implemented in minimal version)")
    
    # === EFFECT COMMANDS ===
    def insert_fill_effect(self):
        """Insert fill effect on selected layer using official API - context aware"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            
            # Check selection context to determine where to insert
            selection_type = substance_painter.layerstack.get_selection_type(layer)
            
            if selection_type == SelectionType.Mask and layer.has_mask():
                # Insert into mask stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                context_name = "mask"
            else:
                # Insert into content stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Content)
                context_name = "content"
            
            effect = insert_fill(insert_position)
            effect.set_name(f"Fill Effect ({context_name})")
            substance_painter.logging.info(f"Inserted fill effect into {context_name} stack")
        else:
            raise ValueError("No layer selected")
    
    def insert_paint_effect(self):
        """Insert paint effect on selected layer using official API - context aware"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            
            # Check selection context to determine where to insert
            selection_type = substance_painter.layerstack.get_selection_type(layer)
            
            if selection_type == SelectionType.Mask and layer.has_mask():
                # For masks, use insert_fill (paint doesn't work properly in mask context)
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                effect = insert_fill(insert_position)  # Use fill for masks
                effect.set_name("Paint Effect (mask)")
                context_name = "mask"
            else:
                # For content, use insert_paint
                insert_position = InsertPosition.inside_node(layer, NodeStack.Content)
                effect = insert_paint(insert_position)
                effect.set_name("Paint Effect (content)")
                context_name = "content"
            
            substance_painter.logging.info(f"Inserted paint effect into {context_name} stack")
        else:
            raise ValueError("No layer selected")
    
    def insert_levels_effect(self):
        """Insert levels effect using official API - context aware"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            
            # Check selection context to determine where to insert
            selection_type = substance_painter.layerstack.get_selection_type(layer)
            
            if selection_type == SelectionType.Mask and layer.has_mask():
                # Insert into mask stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                context_name = "mask"
            else:
                # Insert into content stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Content)
                context_name = "content"
            
            effect = insert_levels_effect(insert_position)
            effect.set_name(f"Levels ({context_name})")
            substance_painter.logging.info(f"Inserted levels effect into {context_name} stack")
        else:
            raise ValueError("No layer selected")
    
    def insert_compare_mask_effect(self):
        """Insert compare mask effect using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if layer.has_mask():
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                effect = insert_compare_mask_effect(insert_position)
                effect.set_name("Compare Mask")
            else:
                raise ValueError("Layer needs a mask for compare mask effect")
        else:
            raise ValueError("No layer selected")
    
    def insert_filter_effect(self):
        """Insert filter effect using official API - context aware"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            
            # Check selection context to determine where to insert
            selection_type = substance_painter.layerstack.get_selection_type(layer)
            
            if selection_type == SelectionType.Mask and layer.has_mask():
                # Insert into mask stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                context_name = "mask"
            else:
                # Insert into content stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Content)
                context_name = "content"
            
            effect = insert_filter_effect(insert_position)
            effect.set_name(f"Filter ({context_name})")
            substance_painter.logging.info(f"Inserted filter effect into {context_name} stack")
        else:
            raise ValueError("No layer selected")
    
    def insert_generator_effect(self):
        """Insert generator effect using official API - context aware"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            
            # Check selection context to determine where to insert
            selection_type = substance_painter.layerstack.get_selection_type(layer)
            
            if selection_type == SelectionType.Mask and layer.has_mask():
                # Insert into mask stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                context_name = "mask"
            else:
                # Insert into content stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Content)
                context_name = "content"
            
            effect = insert_generator_effect(insert_position)
            effect.set_name(f"Generator ({context_name})")
            substance_painter.logging.info(f"Inserted generator effect into {context_name} stack")
        else:
            raise ValueError("No layer selected")
    
    def insert_anchor_point_effect(self):
        """Insert anchor point effect using official API - context aware"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            
            # Check selection context to determine where to insert
            selection_type = substance_painter.layerstack.get_selection_type(layer)
            
            if selection_type == SelectionType.Mask and layer.has_mask():
                # Insert into mask stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                context_name = "mask"
            else:
                # Insert into content stack
                insert_position = InsertPosition.inside_node(layer, NodeStack.Content)
                context_name = "content"
            
            effect = insert_anchor_point_effect(insert_position, "Anchor Point")
            effect.set_name(f"Anchor Point ({context_name})")
            substance_painter.logging.info(f"Inserted anchor point effect into {context_name} stack")
        else:
            raise ValueError("No layer selected")
    
    def insert_color_selection_effect(self):
        """Insert color selection effect using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if layer.has_mask():
                insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                effect = insert_color_selection_effect(insert_position)
                effect.set_name("Color Selection")
            else:
                raise ValueError("Layer needs a mask for color selection effect")
        else:
            raise ValueError("No layer selected")
    
    # === MASK OPERATIONS ===
    def get_selected_nodes(self):
        """Get currently selected layer nodes using real API"""
        try:
            # Get active texture set
            texture_sets = substance_painter.textureset.all_texture_sets()
            if not texture_sets:
                return []
            
            active_set = texture_sets[0]
            stack = active_set.get_stack()
            if not stack:
                return []
            
            # Get selected nodes - this is the actual API call
            return substance_painter.layerstack.get_selected_nodes(stack)
        except Exception:
            return []
    
    def add_layer_mask(self):
        """Add mask to selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                raise ValueError("No layer selected")
            
            layer = selected[0]
            if layer.has_mask():
                raise ValueError("Layer already has a mask")
            
            # Add mask with white background (default)
            layer.add_mask(MaskBackground.White)
            
            # Switch selection context to the mask for subsequent macro commands
            from substance_painter.layerstack import set_selection_type, SelectionType
            set_selection_type(layer, SelectionType.Mask)
            substance_painter.logging.info("Added layer mask and switched to mask context")
            return True
            
        except Exception as e:
            raise ValueError(f"Error adding layer mask: {e}")
    
    def remove_layer_mask(self):
        """Remove mask from selected layer using official API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                raise ValueError("No layer selected")
            
            layer = selected[0]
            if not layer.has_mask():
                raise ValueError("Layer has no mask to remove")
            
            layer.remove_mask()
            substance_painter.logging.info("Removed layer mask")
            return True
            
        except Exception as e:
            raise ValueError(f"Error removing layer mask: {e}")
    
    def toggle_mask(self):
        """Toggle mask enable/disable using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if hasattr(layer, 'is_mask_enabled') and layer.has_mask():
                current_state = layer.is_mask_enabled()
                layer.enable_mask(not current_state)
            else:
                raise ValueError("Layer has no mask to toggle")
        else:
            raise ValueError("No layer selected")
    
    def set_mask_black(self):
        """Set mask background to black using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if hasattr(layer, 'set_mask_background') and layer.has_mask():
                layer.set_mask_background(MaskBackground.Black)
            else:
                raise ValueError("Layer has no mask")
        else:
            raise ValueError("No layer selected")
    
    def set_mask_white(self):
        """Set mask background to white using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if hasattr(layer, 'set_mask_background') and layer.has_mask():
                layer.set_mask_background(MaskBackground.White)
            else:
                raise ValueError("Layer has no mask")
        else:
            raise ValueError("No layer selected")
    
    # === SELECTION & DELETION ===
    def delete_selected(self):
        """Delete selected nodes using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            for node in selected_nodes:
                delete_node(node)
        else:
            raise ValueError("No nodes selected")
    
    def select_content(self):
        """Select layer content using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            set_selection_type(layer, SelectionType.Content)
        else:
            raise ValueError("No layer selected")
    
    def select_mask(self):
        """Select layer mask using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            if hasattr(layer, 'has_mask') and layer.has_mask():
                set_selection_type(layer, SelectionType.Mask)
            else:
                raise ValueError("Layer has no mask to select")
        else:
            raise ValueError("No layer selected")
    
    def select_properties(self):
        """Select layer properties using official API"""
        stack = substance_painter.textureset.get_active_stack()
        selected_nodes = get_selected_nodes(stack)
        
        if selected_nodes:
            layer = selected_nodes[0]
            # Properties selection is only for instance layers
            if hasattr(layer, 'instance_source'):
                set_selection_type(layer, SelectionType.Properties)
            else:
                raise ValueError("Properties selection only available for instance layers")
        else:
            raise ValueError("No layer selected")

    def get_procedural_resources(self):
        """Get list of available procedural resources"""
        try:
            from substance_painter.resource import Usage
            # First try to get all resources and filter by usage
            all_resources = substance_painter.resource.search("")  # Get all resources
            substance_painter.logging.info(f"Commander: Total resources found: {len(all_resources)}")
            
            procedurals = []
            for resource in all_resources:
                try:
                    # Check if this resource has procedural usage
                    if hasattr(resource, 'usages'):
                        usages = resource.usages()
                        # Check if Usage.PROCEDURAL is in the usages
                        if Usage.PROCEDURAL in usages:
                            identifier = resource.identifier()
                            procedurals.append({
                                'name': resource.gui_name(),
                                'category': resource.category() if hasattr(resource, 'category') else 'Unknown',
                                'resource_id': identifier,
                                'resource': resource
                            })
                            substance_painter.logging.info(f"Commander: Found procedural: {resource.gui_name()}")
                except Exception as e:
                    # Skip resources that cause errors - don't log each one
                    continue
            
            substance_painter.logging.info(f"Commander: Final procedural count: {len(procedurals)}")
            return procedurals
            
        except Exception as e:
            substance_painter.logging.error(f"Error searching for procedural resources: {e}")
            import traceback
            substance_painter.logging.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def apply_procedural(self, procedural_data):
        """Apply a procedural resource to a fill effect"""
        try:
            # Get the resource from procedural_data
            resource = procedural_data.get('resource')
            if not resource:
                raise ValueError("No resource found in procedural data")
            
            # Get current selection and context
            stack = substance_painter.textureset.get_active_stack()
            selected_nodes = get_selected_nodes(stack)
            
            # Determine insertion context
            if selected_nodes:
                layer = selected_nodes[0]
                # Check selection type to determine context (mask vs content)
                selection_type = substance_painter.layerstack.get_selection_type(layer)
                
                if selection_type == SelectionType.Mask:
                    # Insert as fill effect in mask stack (grayscale)
                    if not layer.has_mask():
                        layer.add_mask(MaskBackground.Black)
                    insert_position = InsertPosition.inside_node(layer, NodeStack.Mask)
                    context_name = "mask"
                else:
                    # Insert as fill effect in content stack (roughness)
                    insert_position = InsertPosition.inside_node(layer, NodeStack.Content)
                    context_name = "content"
            else:
                # No selection - create at top of stack
                insert_position = InsertPosition.from_textureset_stack(stack)
                context_name = "content"
            
            # Create the fill effect
            effect = insert_fill(insert_position)
            effect.set_name(f"{procedural_data['name']}")
            
            # Apply the procedural resource to the effect
            # Get the resource ID from the procedural data
            resource_id = resource.identifier()
            
            if context_name == "mask":
                # For masks, set to grayscale channel (channel type = None)
                effect.set_source(None, resource_id)
                substance_painter.logging.info(f"Commander: Applied procedural to mask (grayscale)")
            else:
                # For content, target Roughness channel with BaseColor fallback
                # The correct signature is: set_source(channel_type, resource_id)
                try:
                    # Try to set source to Roughness channel - CHANNEL TYPE FIRST!
                    effect.set_source(ChannelType.Roughness, resource_id)
                    substance_painter.logging.info(f"Commander: Applied to Roughness channel")
                except Exception as e:
                    # Fallback to BaseColor if Roughness fails
                    try:
                        effect.set_source(ChannelType.BaseColor, resource_id)
                        substance_painter.logging.info(f"Commander: Applied to BaseColor channel")
                    except Exception as fallback_error:
                        # Final fallback - no channel specification
                        effect.set_source(resource_id)
                        substance_painter.logging.info(f"Commander: Applied to default channel")
            
            return f"✓ Applied procedural '{procedural_data['name']}' as fill effect in {context_name}"
            
        except Exception as e:
            raise ValueError(f"Failed to apply procedural: {e}")

def show_commander():
    """Show dock widget at cursor OR refocus if already visible"""
    global DOCK_WIDGET, COMMANDER_WIDGET
    
    if not DOCK_WIDGET or not COMMANDER_WIDGET:
        return
    
    # If dock is already visible, just refocus the search input
    if DOCK_WIDGET.isVisible():
        DOCK_WIDGET.raise_()
        DOCK_WIDGET.activateWindow()
        COMMANDER_WIDGET.search_input.setFocus()
        COMMANDER_WIDGET.search_input.selectAll()
        
        # Select first visible item for immediate arrow navigation
        if COMMANDER_WIDGET.results_list.count() > 0:
            # Find first visible item (not hidden by search filter)
            for i in range(COMMANDER_WIDGET.results_list.count()):
                item = COMMANDER_WIDGET.results_list.item(i)
                if not item.isHidden():
                    COMMANDER_WIDGET.results_list.setCurrentRow(i)
                    break
        return
    
    # If procedurals haven't been loaded yet, try a lazy load when first opening
    if not COMMANDER_WIDGET.procedurals_loaded:
        substance_painter.logging.info("Commander: First time opening - attempting procedural lazy load")
        COMMANDER_WIDGET.refresh_commands(force_reload_procedurals=True)
    
    # Dock is hidden - show it at cursor position
    # Get cursor position
    cursor_pos = QtGui.QCursor.pos()
    
    # Get screen geometry for bounds checking
    screen = QtWidgets.QApplication.primaryScreen().geometry()
    
    # Set floating and move to cursor
    DOCK_WIDGET.setFloating(True)
    
    # Calculate size and position
    size = DOCK_WIDGET.sizeHint()
    x = cursor_pos.x()
    y = cursor_pos.y()
    
    # Keep within screen bounds
    if x + size.width() > screen.right():
        x = max(0, screen.right() - size.width())
    if y + size.height() > screen.bottom():
        y = max(0, cursor_pos.y() - size.height())
    
    # Position and show
    DOCK_WIDGET.move(x, y)
    DOCK_WIDGET.show()
    DOCK_WIDGET.raise_()
    DOCK_WIDGET.activateWindow()
    
    # Focus search input and select first item for arrow navigation
    COMMANDER_WIDGET.search_input.setFocus()
    COMMANDER_WIDGET.search_input.selectAll()
    
    # Select first item in results for immediate arrow navigation
    if COMMANDER_WIDGET.results_list.count() > 0:
        COMMANDER_WIDGET.results_list.setCurrentRow(0)

def start_plugin():
    """STABLE DOCK WIDGET with popup-like behavior - No crashes!"""
    global COMMANDER_WIDGET, COMMANDER_SHORTCUT, DOCK_WIDGET
    
    try:
        # Create Commander widget  
        COMMANDER_WIDGET = CommanderWidget()
        
        # Create dock widget
        DOCK_WIDGET = substance_painter.ui.add_dock_widget(COMMANDER_WIDGET)
        DOCK_WIDGET.hide()  # Hidden by default
        
        # Create keyboard shortcut
        main_window = substance_painter.ui.get_main_window()
        from PySide6.QtGui import QShortcut
        COMMANDER_SHORTCUT = QShortcut(QtGui.QKeySequence("Ctrl+;"), main_window)
        COMMANDER_SHORTCUT.activated.connect(show_commander)
        
        substance_painter.logging.info("Commander Plugin started - STABLE DOCK with popup behavior")
        
    except Exception as e:
        substance_painter.logging.error(f"Failed to start Commander Plugin: {e}")
        import traceback
        traceback.print_exc()

def close_plugin():
    """STABLE DOCK cleanup - No crashes!"""
    global COMMANDER_WIDGET, COMMANDER_SHORTCUT, DOCK_WIDGET
    
    substance_painter.logging.info("Commander: Starting stable dock cleanup")
    
    # Stop project monitoring timer if it exists
    if COMMANDER_WIDGET and hasattr(COMMANDER_WIDGET, 'project_timer'):
        try:
            COMMANDER_WIDGET.project_timer.stop()
            COMMANDER_WIDGET.project_timer.deleteLater()
            substance_painter.logging.info("Commander: Project monitoring timer cleaned up")
        except Exception as e:
            substance_painter.logging.error(f"Error cleaning up project timer: {e}")
    
    # Clean up macro hotkey shortcuts
    if COMMANDER_WIDGET and hasattr(COMMANDER_WIDGET, 'macro_shortcuts'):
        try:
            for macro_name, shortcut in COMMANDER_WIDGET.macro_shortcuts.items():
                try:
                    shortcut.activated.disconnect()
                    shortcut.setParent(None)
                    shortcut.deleteLater()
                except Exception:
                    pass
            COMMANDER_WIDGET.macro_shortcuts.clear()
            substance_painter.logging.info("Commander: Macro hotkeys cleaned up")
        except Exception as e:
            substance_painter.logging.error(f"Error cleaning up macro hotkeys: {e}")
    
    # Clean up shortcut
    if COMMANDER_SHORTCUT:
        try:
            COMMANDER_SHORTCUT.activated.disconnect()
            COMMANDER_SHORTCUT.setParent(None)
            COMMANDER_SHORTCUT.deleteLater()
        except Exception as e:
            substance_painter.logging.error(f"Error cleaning up shortcut: {e}")
        COMMANDER_SHORTCUT = None
    
    # Clean up dock widget (uses official API)
    if DOCK_WIDGET:
        try:
            substance_painter.ui.delete_ui_element(DOCK_WIDGET)
        except Exception as e:
            substance_painter.logging.error(f"Error cleaning up dock: {e}")
        DOCK_WIDGET = None
        
    COMMANDER_WIDGET = None
    substance_painter.logging.info("Commander Plugin closed - Stable cleanup complete")

if __name__ == "__main__":
    start_plugin()
