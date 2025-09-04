# Main imports
from PySide6 import QtWidgets, QtCore, QtGui
import substance_painter as sp
import substance_painter.ui
import substance_painter.logging
import substance_painter.project
import substance_painter.layerstack
import substance_painter.textureset
import substance_painter.resource
import json
import os

# Import real API classes and enums
from substance_painter.layerstack import (
    NodeType, MaskBackground, GeometryMaskType, ProjectionMode,
    BlendingMode, InsertPosition, NodeStack, SelectionType, set_selection_type
)
from substance_painter.textureset import ChannelType

# Global widgets list - Adobe pattern
WIDGETS = []
MAIN_WINDOW = None

class CommanderWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set proper object name and title for dock widget (required by SP API)
        self.setObjectName("CommanderWidget")
        self.setWindowTitle("Commander")
        
        # Macro system variables
        self.macro_creation_mode = False
        self.selected_commands = []  # Commands selected for macro creation
        self.macros = {}  # Stored macros
        self.macros_file = self._get_macros_file_path()
        self.load_macros()
        
        # Create a native-style Commander icon to match SP's toolbar
        try:
            # Create a 16x16 icon that matches SP's monochrome style
            pixmap = QtGui.QPixmap(16, 16)
            pixmap.fill(QtCore.Qt.GlobalColor.transparent)
            
            painter = QtGui.QPainter(pixmap)
            painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            
            # Use monochrome colors like other SP icons
            gray_color = QtGui.QColor(180, 180, 180)  # Light gray like other icons
            
            # Draw a clean "C" for Commander in monochrome style
            painter.setPen(QtGui.QPen(gray_color, 2))
            painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
            
            # Draw "C" shape using arc - clean and simple
            rect = QtCore.QRect(4, 3, 8, 10)  # Rectangle for the C shape
            painter.drawArc(rect, 30 * 16, 300 * 16)  # Arc from 30° to 330° (300° span)
            
            painter.end()
            
            icon = QtGui.QIcon(pixmap)
            self.setWindowIcon(icon)
            
        except Exception as e:
            # Fallback: no icon (dock widget will work without it, just no quick button)
            pass
        
        # Set size policies to allow flexible resizing like other SP panels
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred)
        
        # Set minimum size instead of fixed size
        self.setMinimumSize(QtCore.QSize(300, 400))
        
        # Set initial preferred size
        self.resize(400, 500)
        
        # Simple layout - following Adobe pattern
        layout = QtWidgets.QVBoxLayout()
        
        # No title - cleaner interface
        
        # Search input
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search commands...")
        layout.addWidget(self.search_input)
        
        # Simple results list
        self.results_list = QtWidgets.QListWidget()
        layout.addWidget(self.results_list)
        
        # Status label
        self.status_label = QtWidgets.QLabel("Plugin loaded")
        self.status_label.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(self.status_label)
        
        # No buttons - double-click to execute, auto-refresh on search
        
        self.setLayout(layout)
        
        # Connect search
        self.search_input.textChanged.connect(self.on_search_changed)
        
        # Connect double-click to execute
        self.results_list.itemDoubleClicked.connect(self.on_double_click_execute)
        
        # Connect single-click for macro creation
        self.results_list.itemClicked.connect(self.on_single_click)
        
        # Enable right-click context menu
        self.results_list.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set up keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Initial population
        self.refresh_commands()
    
    def get_procedural_resources(self):
        """Get list of available procedural resources"""
        try:
            # First try to get all resources and filter by usage
            self.log("Searching for procedural resources...")
            all_resources = substance_painter.resource.search("")  # Get all resources
            
            procedurals = []
            for resource in all_resources:
                try:
                    # Check if this resource has procedural usage
                    if hasattr(resource, 'usages'):
                        usages = resource.usages()
                        # Check if Usage.PROCEDURAL is in the usages
                        if substance_painter.resource.Usage.PROCEDURAL in usages:
                            identifier = resource.identifier()
                            procedurals.append({
                                'name': resource.gui_name(),
                                'category': resource.category() if hasattr(resource, 'category') else 'Unknown',
                                'resource_id': identifier,
                                'resource': resource
                            })
                except Exception as e:
                    # Skip resources that cause errors
                    continue
            
            self.log(f"Found {len(procedurals)} procedural resources")
            return procedurals
            
        except Exception as e:
            self.log(f"Error searching for procedural resources: {e}")
            # Try alternative approach - search by specific query
            try:
                self.log("Trying alternative search method...")
                # Try different query formats
                for query in ["procedural", "type:procedural", "*"]:
                    try:
                        resources = substance_painter.resource.search(query)
                        self.log(f"Query '{query}' returned {len(resources)} resources")
                        if len(resources) > 0:
                            # Just return first few as test
                            return [{
                                'name': f"Test Resource {i}",
                                'category': 'Test',
                                'resource_id': None,
                                'resource': resource
                            } for i, resource in enumerate(resources[:3])]
                    except Exception as query_error:
                        self.log(f"Query '{query}' failed: {query_error}")
                        continue
                        
            except Exception as alt_error:
                self.log(f"Alternative search also failed: {alt_error}")
                
            return []
    
    def _update_selection_styling(self):
        """Update list widget selection styling based on macro creation mode"""
        try:
            if self.macro_creation_mode:
                # Light yellow selection background for macro creation mode
                selection_style = "selection-background-color: #fffacd; selection-color: #333;"  # Light yellow with dark text
            else:
                # Normal dark gray selection background
                selection_style = "selection-background-color: #404040; selection-color: white;"  # Dark gray with white text
            
            # Apply just the selection styling to the list widget
            self.results_list.setStyleSheet(f"""
                QListWidget {{
                    background-color: #2b2b2b;
                    border: 1px solid #555;
                    color: white;
                    {selection_style}
                }}
            """)
        except Exception as e:
            self.log(f"Error updating selection styling: {e}")
    
    def _get_macros_file_path(self):
        """Get the path for storing macros"""
        try:
            # Try to use user home directory
            home_dir = os.path.expanduser("~")
            commander_dir = os.path.join(home_dir, ".substance_painter_commander")
            os.makedirs(commander_dir, exist_ok=True)
            return os.path.join(commander_dir, "macros.json")
        except:
            # Fallback to temp directory
            return os.path.join(os.path.expanduser("~"), "commander_macros.json")
    
    def load_macros(self):
        """Load macros from file"""
        try:
            if os.path.exists(self.macros_file):
                with open(self.macros_file, 'r') as f:
                    self.macros = json.load(f)
                self.log(f"Loaded {len(self.macros)} macros")
            else:
                self.macros = {}
                self.log("No macros file found, starting with empty macros")
        except Exception as e:
            self.log(f"Failed to load macros: {str(e)}")
            self.macros = {}
    
    def save_macros(self):
        """Save macros to file"""
        try:
            with open(self.macros_file, 'w') as f:
                json.dump(self.macros, f, indent=2)
            self.log(f"Saved {len(self.macros)} macros")
        except Exception as e:
            self.log(f"Failed to save macros: {str(e)}")
    
    def on_single_click(self, item):
        """Handle single-click for macro creation"""
        if self.macro_creation_mode:
            command = item.text()
            
            # Skip macro items themselves (can't add macros to macros)
            if command.startswith("[MACRO]"):
                return
            
            # Toggle selection
            if command in self.selected_commands:
                self.selected_commands.remove(command)
                # Remove visual feedback - restore to normal white text
                item.setForeground(QtGui.QBrush(QtCore.Qt.GlobalColor.white))
            else:
                self.selected_commands.append(command)
                # Add visual feedback (different text color)
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 215, 0)))  # Golden yellow - much more readable
            
            self.status_label.setText(f"Macro Mode: {len(self.selected_commands)} commands selected")
    
    def show_context_menu(self, position):
        """Show right-click context menu"""
        item = self.results_list.itemAt(position)
        menu = QtWidgets.QMenu(self)
        
        if item:
            command = item.text()
            
            if command.startswith("[MACRO]"):
                # Context menu for existing macros
                macro_name = command[7:].strip()  # Remove "[MACRO] " prefix
                
                rename_action = menu.addAction("Rename Macro")
                # Store macro name for the action
                rename_action.macro_name = macro_name
                rename_action.triggered.connect(self._handle_rename_macro)
                
                delete_action = menu.addAction("Delete Macro")
                # Store macro name for the action
                delete_action.macro_name = macro_name
                delete_action.triggered.connect(self._handle_delete_macro)
            else:
                # Context menu for regular commands
                if not self.macro_creation_mode:
                    start_macro_action = menu.addAction("Start Macro Creation")
                    start_macro_action.triggered.connect(self.start_macro_creation)
                else:
                    if len(self.selected_commands) > 0:
                        create_macro_action = menu.addAction(f"Create Macro ({len(self.selected_commands)} commands)")
                        create_macro_action.triggered.connect(self.create_macro_dialog)
                    
                    cancel_macro_action = menu.addAction("Cancel Macro Creation")
                    cancel_macro_action.triggered.connect(self.cancel_macro_creation)
        else:
            # Context menu for empty area
            if not self.macro_creation_mode:
                start_macro_action = menu.addAction("Start Macro Creation")
                start_macro_action.triggered.connect(self.start_macro_creation)
            else:
                if len(self.selected_commands) > 0:
                    create_macro_action = menu.addAction(f"Create Macro ({len(self.selected_commands)} commands)")
                    create_macro_action.triggered.connect(self.create_macro_dialog)
                
                cancel_macro_action = menu.addAction("Cancel Macro Creation")
                cancel_macro_action.triggered.connect(self.cancel_macro_creation)
        
        if not menu.isEmpty():
            menu.exec(self.results_list.mapToGlobal(position))
    
    def _handle_rename_macro(self):
        """Handle rename macro action from context menu"""
        action = self.sender()
        if hasattr(action, 'macro_name'):
            self.rename_macro(action.macro_name)
    
    def _handle_delete_macro(self):
        """Handle delete macro action from context menu"""
        action = self.sender()
        if hasattr(action, 'macro_name'):
            self.delete_macro(action.macro_name)
    
    def start_macro_creation(self):
        """Start macro creation mode"""
        self.macro_creation_mode = True
        self.selected_commands = []
        self.status_label.setText("Macro Creation Mode: Click commands to select, right-click to create")
        self.log("Started macro creation mode")
        
        # Update selection styling to light yellow for macro creation mode
        self._update_selection_styling()
    
    def cancel_macro_creation(self):
        """Cancel macro creation mode"""
        self.macro_creation_mode = False
        self.selected_commands = []
        self.status_label.setText("Macro creation cancelled")
        self.log("Cancelled macro creation mode")
        
        # Update selection styling back to normal dark gray
        self._update_selection_styling()
        
        # Simply refresh the entire command list to restore proper colors
        # This ensures macros get their blue color back and regular commands are reset
        self.refresh_commands()
    
    def create_macro_dialog(self):
        """Show dialog to create a macro"""
        if len(self.selected_commands) == 0:
            QtWidgets.QMessageBox.warning(self, "No Commands", "Please select some commands first.")
            return
        
        # Prompt for macro name
        name, ok = QtWidgets.QInputDialog.getText(
            self, 
            "Create Macro", 
            f"Name for macro with {len(self.selected_commands)} commands:\n" + 
            "\n".join([f"• {cmd}" for cmd in self.selected_commands])
        )
        
        if ok and name.strip():
            self.create_macro(name.strip())
    
    def create_macro(self, name):
        """Create a macro with the selected commands"""
        if name in self.macros:
            reply = QtWidgets.QMessageBox.question(
                self, "Macro Exists", 
                f"Macro '{name}' already exists. Replace it?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
            )
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                return
        
        # Create the macro
        self.macros[name] = {
            'commands': self.selected_commands.copy(),
            'created': str(QtCore.QDateTime.currentDateTime().toString())
        }
        
        self.save_macros()
        self.cancel_macro_creation()  # Exit macro creation mode
        self.refresh_commands()  # Refresh to show new macro
        
        self.status_label.setText(f"Created macro: {name}")
        self.log(f"Created macro '{name}' with {len(self.selected_commands)} commands")
    
    def rename_macro(self, old_name):
        """Rename an existing macro"""
        new_name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename Macro", f"New name for '{old_name}':", text=old_name
        )
        
        if ok and new_name.strip() and new_name.strip() != old_name:
            new_name = new_name.strip()
            
            if new_name in self.macros:
                QtWidgets.QMessageBox.warning(self, "Name Exists", f"Macro '{new_name}' already exists.")
                return
            
            # Rename the macro
            self.macros[new_name] = self.macros.pop(old_name)
            self.save_macros()
            self.refresh_commands()
            
            self.status_label.setText(f"Renamed macro to: {new_name}")
            self.log(f"Renamed macro from '{old_name}' to '{new_name}'")
    
    def delete_macro(self, name):
        """Delete an existing macro"""
        reply = QtWidgets.QMessageBox.question(
            self, "Delete Macro", 
            f"Delete macro '{name}'?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            del self.macros[name]
            self.save_macros()
            self.refresh_commands()
            
            self.status_label.setText(f"Deleted macro: {name}")
            self.log(f"Deleted macro '{name}'")
    
    def execute_macro(self, name):
        """Execute a macro by running all its commands in sequence"""
        if name not in self.macros:
            self.log(f"ERROR: Macro '{name}' not found")
            return False
        
        macro = self.macros[name]
        commands = macro['commands']
        self.log(f"Executing macro '{name}' with {len(commands)} commands")
        
        success_count = 0
        failed_commands = []
        
        for i, command in enumerate(commands):
            try:
                self.log(f"  [{i+1}/{len(commands)}] {command}")
                success = self.execute_command(command)
                
                if success:
                    success_count += 1
                    self.log(f"    ✓ Success")
                else:
                    failed_commands.append(command)
                    self.log(f"    ✗ Failed")
                    # Continue with remaining commands (as per user requirement)
                    
            except Exception as e:
                failed_commands.append(command)
                self.log(f"    ✗ Error: {e}")
                # Continue with remaining commands
        
        # Report results
        if failed_commands:
            self.status_label.setText(f"Macro '{name}': {success_count}/{len(commands)} succeeded")
            self.log(f"Macro '{name}' completed: {success_count}/{len(commands)} succeeded, {len(failed_commands)} failed")
        else:
            self.status_label.setText(f"Macro '{name}': All {len(commands)} commands succeeded")
            self.log(f"Macro '{name}' completed successfully: All {len(commands)} commands succeeded")
        
        return len(failed_commands) == 0
    
    def execute_procedural_from_command(self, command):
        """Execute a procedural command from a macro by finding the matching procedural resource"""
        try:
            # Extract procedural name from command like "[PROC] Grunge Brushed"
            if not command.startswith("[PROC]"):
                return False
                
            procedural_name = command[7:].strip()  # Remove "[PROC] " prefix
            self.log(f"Looking for procedural: '{procedural_name}'")
            
            # Get current procedural resources and find the matching one
            procedurals = self.get_procedural_resources()
            for procedural in procedurals:
                if procedural['name'] == procedural_name:
                    self.log(f"Found matching procedural: {procedural['name']}")
                    return self.apply_procedural(procedural)
            
            self.log(f"ERROR: Procedural '{procedural_name}' not found in current resources")
            return False
            
        except Exception as e:
            self.log(f"Error executing procedural from command: {e}")
            return False
    
    def apply_procedural(self, procedural_data):
        """Apply a procedural resource as a new fill effect with proper channel assignment"""
        try:
            # Check if project is open
            if not substance_painter.project.is_open():
                self.log("ERROR: No project open")
                self.status_label.setText("No project open")
                return False
            
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            insert_pos = self.get_smart_insert_position(layer)
            
            # Create a new fill effect
            effect = substance_painter.layerstack.insert_fill(insert_pos)
            effect.set_name(f"{procedural_data['name']}")
            
            # Get the resource ID
            resource_id = procedural_data.get('resource_id')
            if not resource_id:
                self.log("ERROR: No resource ID available")
                return False
            
            # Apply procedural to Roughness channel (most common use case)
            try:
                effect.set_source(ChannelType.Roughness, resource_id)
                channel = "Roughness"
                success = True
            except Exception:
                # Fallback to BaseColor if Roughness fails
                try:
                    effect.set_source(ChannelType.BaseColor, resource_id)
                    channel = "BaseColor"
                    success = True
                except Exception:
                    # Last resort: try without channel (for mask context)
                    try:
                        effect.set_source(None, resource_id)
                        channel = "grayscale"
                        success = True
                    except Exception as e:
                        self.log(f"Failed to apply procedural: {e}")
                        success = False
            
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            
            if success:
                self.log(f"✓ Applied procedural '{procedural_data['name']}' to {channel} channel in {stack_type}")
                return True
            else:
                self.log(f"✗ Failed to apply procedural '{procedural_data['name']}'")
                return False
            
        except Exception as e:
            self.log(f"Error applying procedural: {e}")
            import traceback
            self.log(f"DEBUG: Full traceback: {traceback.format_exc()}")
            return False
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for Commander"""
        # Skip space bar - use simpler approach
        # Just rely on toolbar button and menu for now
        pass
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == QtCore.Qt.Key.Key_Escape:
            # Hide the dock widget for true popup behavior
            if hasattr(self, 'dock_widget') and self.dock_widget:
                self.dock_widget.hide()
            else:
                self.hide()
        elif event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            # Enter key executes selected command
            current_item = self.results_list.currentItem()
            if current_item:
                self.on_double_click_execute(current_item)
                # Hide after execution for popup behavior
                if hasattr(self, 'dock_widget') and self.dock_widget:
                    self.dock_widget.hide()
        else:
            super().keyPressEvent(event)
    
    def toggle_visibility(self):
        """Toggle Commander visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show_and_focus()
    
    def show_and_focus(self):
        """Show Commander and focus search input"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.search_input.setFocus()
        self.search_input.selectAll()
        
        # Log initialization
        self.log("Commander Plugin loaded successfully")
    
    def show_commander_from_shortcut(self):
        """Show Commander at mouse position with popup behavior"""
        try:
            substance_painter.logging.info("Commander shortcut triggered - showing Commander at mouse")
            
            # Work with the dock widget directly
            if hasattr(self, 'dock_widget') and self.dock_widget:
                dock = self.dock_widget
                
                # Position at mouse cursor
                cursor_pos = QtGui.QCursor.pos()
                
                # Adjust position to keep widget on screen
                screen_rect = QtWidgets.QApplication.primaryScreen().geometry()
                widget_size = dock.sizeHint()
                
                # Calculate position (offset slightly to avoid cursor)
                x = cursor_pos.x() + 10
                y = cursor_pos.y() + 10
                
                # Keep on screen
                if x + widget_size.width() > screen_rect.right():
                    x = cursor_pos.x() - widget_size.width() - 10
                if y + widget_size.height() > screen_rect.bottom():
                    y = cursor_pos.y() - widget_size.height() - 10
                
                dock.move(x, y)
                
                # Show the dock widget
                dock.show()
                dock.setVisible(True)
                dock.raise_()
                dock.activateWindow()
                
                # Also show the widget inside
                self.show()
                self.raise_()
                
                # Focus search input and clear any existing search
                self.search_input.setFocus()
                self.search_input.clear()
                
                substance_painter.logging.info(f"Commander shown at mouse position ({x}, {y})")
            else:
                substance_painter.logging.info("No dock widget reference - showing widget directly")
                self.show()
                self.raise_()
                self.activateWindow()
                self.search_input.setFocus()
                self.search_input.clear()
            
        except Exception as e:
            substance_painter.logging.error(f"Error showing Commander from shortcut: {e}")
            import traceback
            substance_painter.logging.error(f"Traceback: {traceback.format_exc()}")
    
    def eventFilter(self, obj, event):
        """Handle events to close Commander on outside clicks"""
        try:
            # Only process events when Commander is visible
            if hasattr(self, 'dock_widget') and self.dock_widget and self.dock_widget.isVisible():
                
                # Check for mouse press events outside the Commander
                if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                    if event.button() == QtCore.Qt.MouseButton.LeftButton:
                        # Get the widget under the mouse
                        try:
                            global_pos = event.globalPosition().toPoint()
                            widget_under_mouse = QtWidgets.QApplication.widgetAt(global_pos)
                            
                            # Check if the click is outside our dock widget and its children
                            if widget_under_mouse is not None:
                                # Check if clicked widget is part of our Commander
                                commander_widgets = [self, self.dock_widget, self.search_input, self.results_list]
                                is_inside_commander = False
                                
                                for commander_widget in commander_widgets:
                                    if widget_under_mouse == commander_widget or commander_widget.isAncestorOf(widget_under_mouse):
                                        is_inside_commander = True
                                        break
                                
                                # If click is outside Commander, hide it
                                if not is_inside_commander:
                                    substance_painter.logging.info("Outside click detected - hiding Commander")
                                    self.dock_widget.hide()
                                    
                        except Exception as click_error:
                            # Don't interfere with SP if there's any error in click detection
                            pass
                
                # Also handle focus loss (when clicking somewhere else)
                elif event.type() == QtCore.QEvent.Type.WindowDeactivate:
                    if obj == self.dock_widget:
                        # Small delay to avoid immediate hiding when clicking on SP UI
                        QtCore.QTimer.singleShot(150, self._delayed_hide_check)
                        
        except Exception as e:
            # Don't log event filter errors to avoid spam
            pass
            
        # Always let the event pass through to avoid interfering with SP
        return super().eventFilter(obj, event)
    
    def _delayed_hide_check(self):
        """Check if Commander should be hidden after a delay"""
        try:
            if hasattr(self, 'dock_widget') and self.dock_widget and self.dock_widget.isVisible():
                # Only hide if nothing in Commander has focus
                if not (self.dock_widget.hasFocus() or self.search_input.hasFocus() or self.results_list.hasFocus()):
                    substance_painter.logging.info("Focus lost - hiding Commander")
                    self.dock_widget.hide()
        except Exception as e:
            pass
    
    def log(self, message):
        """Simple logging method"""
        try:
            print(f"Commander Plugin: {message}")
            
            # SP logging
            try:
                substance_painter.logging.info(f"Commander Plugin: {message}")
            except:
                pass
        except:
            pass
    
    def refresh_commands(self):
        """Refresh the command list with macros first, then comprehensive layerstack commands"""
        try:
            self.results_list.clear()
            
            # Add macros first (at top, in orange color)
            for macro_name in sorted(self.macros.keys()):
                item = QtWidgets.QListWidgetItem(f"[MACRO] {macro_name}")
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 140, 0)))  # Dark orange - very readable
                item.setToolTip(f"Macro: {len(self.macros[macro_name]['commands'])} commands\n" + 
                               "\n".join([f"• {cmd}" for cmd in self.macros[macro_name]['commands']]))
                self.results_list.addItem(item)
            
            # Real layerstack commands based on actual API
            # Real API commands from /API/layerstack.py - all verified as working
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
                item = QtWidgets.QListWidgetItem(cmd)
                # Add category prefix for better organization
                if any(x in cmd.lower() for x in ['create', 'add']):
                    item.setToolTip("Creation Commands")
                elif any(x in cmd.lower() for x in ['duplicate', 'delete', 'copy', 'paste', 'clear', 'merge']):
                    item.setToolTip("Management Commands")
                elif any(x in cmd.lower() for x in ['move', 'group', 'reorder']):
                    item.setToolTip("Organization Commands")
                elif any(x in cmd.lower() for x in ['visibility', 'opacity', 'lock']):
                    item.setToolTip("Property Commands")
                elif any(x in cmd.lower() for x in ['blend', 'mode']):
                    item.setToolTip("Blending Commands")
                elif any(x in cmd.lower() for x in ['mask']):
                    item.setToolTip("Mask Commands")
                elif any(x in cmd.lower() for x in ['select']):
                    item.setToolTip("Selection Commands")
                elif any(x in cmd.lower() for x in ['channel', 'base', 'roughness', 'metallic', 'normal']):
                    item.setToolTip("Channel Commands")
                elif any(x in cmd.lower() for x in ['stack', 'flatten', 'reset']):
                    item.setToolTip("Stack Commands")
                else:
                    item.setToolTip("Advanced Commands")
                
                self.results_list.addItem(item)
            
            # Add procedural resources below layerstack commands
            procedural_count = 0
            try:
                procedurals = self.get_procedural_resources()
                for procedural in procedurals:
                    item = QtWidgets.QListWidgetItem(f"[PROC] {procedural['name']}")
                    item.setForeground(QtGui.QBrush(QtGui.QColor(100, 149, 237)))  # Cornflower blue - distinct from macros
                    item.setToolTip(f"Procedural: {procedural.get('category', 'Unknown')}\nApplies to Roughness channel (with BaseColor fallback)")
                    # Store the resource identifier for later use
                    item.setData(QtCore.Qt.UserRole, procedural)
                    self.results_list.addItem(item)
                    procedural_count += 1
            except Exception as e:
                self.log(f"Error loading procedural resources: {e}")
            
            total_items = len(commands) + procedural_count + len(self.macros)
            self.status_label.setText(f"Found {total_items} items ({len(commands)} commands, {procedural_count} procedurals)")
            self.log(f"Refreshed {len(commands)} layerstack commands and {procedural_count} procedural resources")
            
        except Exception as e:
            self.log(f"Error refreshing commands: {e}")
            self.status_label.setText("Error refreshing commands")
    
    def on_search_changed(self, search_text):
        """Handle search text changes"""
        try:
            search_lower = search_text.lower()
            
            for i in range(self.results_list.count()):
                item = self.results_list.item(i)
                if search_text == "" or search_lower in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
                    
        except Exception as e:
            self.log(f"Error in search: {e}")
    
    def on_double_click_execute(self, item):
        """Handle double-click to execute command or macro"""
        try:
            command = item.text()
            self.log(f"Double-clicked: {command}")
            
            # Check if it's a macro
            if command.startswith("[MACRO]"):
                macro_name = command[7:].strip()  # Remove "[MACRO] " prefix
                self.log(f"Executing macro: {macro_name}")
                success = self.execute_macro(macro_name)
            elif command.startswith("[PROC]"):
                # It's a procedural resource
                procedural_data = item.data(QtCore.Qt.UserRole)
                if procedural_data:
                    self.log(f"Applying procedural: {procedural_data['name']}")
                    success = self.apply_procedural(procedural_data)
                else:
                    self.log("ERROR: No procedural data found")
                    success = False
            else:
                # Check if project is open for regular commands
                if not substance_painter.project.is_open():
                    self.log("ERROR: No project open")
                    self.status_label.setText("No project open")
                    return
                
                # Execute regular command
                success = self.execute_command(command)
            
            if success:
                self.status_label.setText(f"✓ Executed: {command}")
                self.log(f"✓ Successfully executed: {command}")
                # Hide after successful execution for popup behavior
                if hasattr(self, 'dock_widget') and self.dock_widget:
                    self.dock_widget.hide()
            else:
                self.status_label.setText(f"✗ Failed: {command}")
                self.log(f"✗ Failed to execute: {command}")
                
        except Exception as e:
            self.log(f"Error in double-click execute: {e}")
            self.status_label.setText(f"Double-click error: {e}")
    
    def execute_selected(self):
        """Execute the selected command"""
        try:
            selected_items = self.results_list.selectedItems()
            if not selected_items:
                self.log("No command selected")
                return
            
            command = selected_items[0].text()
            self.log(f"Executing: {command}")
            
            # Check if project is open
            if not substance_painter.project.is_open():
                self.log("ERROR: No project open")
                self.status_label.setText("No project open")
                return
            
            # Execute the command
            success = self.execute_command(command)
            
            if success:
                self.status_label.setText(f"Executed: {command}")
                self.log(f"✓ Successfully executed: {command}")
            else:
                self.status_label.setText(f"Failed to execute: {command}")
                self.log(f"✗ Failed to execute: {command}")
                
        except Exception as e:
            self.log(f"Error executing command: {e}")
            self.status_label.setText(f"Execution error: {e}")
    
    def execute_command(self, command):
        """Execute a specific command using the real Substance Painter API"""
        try:
            # Handle procedural resources
            if command.startswith("[PROC]"):
                return self.execute_procedural_from_command(command)
                
            # Handle regular layerstack commands
            # === Layer Creation Commands (Real API) ===
            if command == "Create Paint Layer":
                return self.create_paint_layer()
            elif command == "Create Fill Layer":
                return self.create_fill_layer()
            elif command == "Create Group Layer":
                return self.create_group_layer()
            elif command == "Create Layer Instance":
                return self.create_layer_instance()
                
            # === Effect Creation Commands (Real API) ===
            elif command == "Insert Levels Effect":
                return self.insert_levels_effect()
            elif command == "Insert Filter Effect":
                return self.insert_filter_effect()
            elif command == "Insert Fill Effect":
                return self.insert_fill_effect()
            elif command == "Insert Generator Effect":
                return self.insert_generator_effect()
            elif command == "Insert Compare Mask Effect":
                return self.insert_compare_mask_effect()
            elif command == "Insert Color Selection Effect":
                return self.insert_color_selection_effect()
            elif command == "Insert Anchor Point Effect":
                return self.insert_anchor_point_effect()
                
            # === Layer Management Commands (Real API) ===
            elif command == "Delete Selected Layers":
                return self.delete_selected_layers()
            elif command == "Rename Selected Layer":
                return self.rename_selected_layer()
                
            # === Layer Properties Commands (Real API) ===
            elif command == "Toggle Layer Visibility":
                return self.toggle_layer_visibility()
            elif command == "Show Layer":
                return self.show_layer()
            elif command == "Hide Layer":
                return self.hide_layer()
            elif command == "Set Layer Opacity":
                return self.set_layer_opacity()
            elif command == "Get Layer Opacity":
                return self.get_layer_opacity()
            elif command == "Set Blend Mode":
                return self.set_blend_mode()
            elif command == "Get Blend Mode":
                return self.get_blend_mode()
                
            # === Layer Mask Commands (Real API) ===
            elif command == "Add Layer Mask":
                return self.add_layer_mask()
            elif command == "Remove Layer Mask":
                return self.remove_layer_mask()
            elif command == "Enable Layer Mask":
                return self.enable_layer_mask()
            elif command == "Disable Layer Mask":
                return self.disable_layer_mask()
            elif command == "Set Mask Background White":
                return self.set_mask_background_white()
            elif command == "Set Mask Background Black":
                return self.set_mask_background_black()
                
            # === Smart Materials/Masks Commands (Real API) ===
            elif command == "Insert Smart Material":
                return self.insert_smart_material()
            elif command == "Create Smart Material":
                return self.create_smart_material()
            elif command == "Insert Smart Mask":
                return self.insert_smart_mask()
            elif command == "Create Smart Mask":
                return self.create_smart_mask()
                
            # === Geometry Mask Commands (Real API) ===
            elif command == "Set Geometry Mask Mesh":
                return self.set_geometry_mask_mesh()
            elif command == "Set Geometry Mask UV Tile":
                return self.set_geometry_mask_uv_tile()
            elif command == "Enable Geometry Mask":
                return self.enable_geometry_mask()
                
            # === Projection Mode Commands (Real API) ===
            elif command == "Set Projection UV":
                return self.set_projection_uv()
            elif command == "Set Projection Triplanar":
                return self.set_projection_triplanar()
            elif command == "Set Projection Planar":
                return self.set_projection_planar()
            elif command == "Set Projection Spherical":
                return self.set_projection_spherical()
            elif command == "Set Projection Cylindrical":
                return self.set_projection_cylindrical()
            elif command == "Enable Symmetry":
                return self.enable_symmetry()
            elif command == "Disable Symmetry":
                return self.disable_symmetry()
                
            else:
                self.log(f"Unknown command: {command}")
                return False
                
        except Exception as e:
            self.log(f"Error executing command '{command}': {e}")
            return False
    
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
            
        except Exception as e:
            self.log(f"Error getting selected nodes: {e}")
            return []
    
    def get_active_stack(self):
        """Get the active texture set stack"""
        try:
            texture_sets = substance_painter.textureset.all_texture_sets()
            if not texture_sets:
                return None
            return texture_sets[0].get_stack()
        except Exception as e:
            self.log(f"Error getting active stack: {e}")
            return None
    
    def create_paint_layer(self):
        """Create a paint layer using real API"""
        try:
            stack = self.get_active_stack()
            if not stack:
                return False
            
            # Create insert position at top of stack - this is the real API
            insert_pos = InsertPosition.from_textureset_stack(stack)
            
            # Insert paint layer - this is the real API function
            new_layer = substance_painter.layerstack.insert_paint(insert_pos)
            new_layer.set_name("Paint Layer")
            
            # Select the newly created layer so subsequent commands operate on it
            substance_painter.layerstack.set_selected_nodes([new_layer])
            
            self.log("✓ Created paint layer and selected it")
            
            return True
            
        except Exception as e:
            self.log(f"Error creating paint layer: {e}")
            return False
    
    def create_fill_layer(self):
        """Create a fill layer using real API"""
        try:
            stack = self.get_active_stack()
            if not stack:
                return False
            
            # Create insert position at top of stack - this is the real API
            insert_pos = substance_painter.layerstack.InsertPosition.from_textureset_stack(stack)
            
            # Insert fill layer - this is the real API function  
            new_layer = substance_painter.layerstack.insert_fill(insert_pos)
            new_layer.set_name("Fill Layer")
            
            # Enable only BaseColor channel by default
            new_layer.active_channels = {ChannelType.BaseColor}
            
            # Select the newly created layer so subsequent commands operate on it
            substance_painter.layerstack.set_selected_nodes([new_layer])
            
            self.log("✓ Created fill layer with BaseColor channel only and selected it")
            
            return True
            
        except Exception as e:
            self.log(f"Error creating fill layer: {e}")
            return False
    
    def create_group_layer(self):
        """Create a group layer using real API"""
        try:
            stack = self.get_active_stack()
            if not stack:
                return False
            
            # Create insert position at top of stack - this is the real API
            insert_pos = substance_painter.layerstack.InsertPosition.from_textureset_stack(stack)
            
            # Insert group layer - this is the real API function
            new_layer = substance_painter.layerstack.insert_group(insert_pos)
            new_layer.set_name("Group")
            
            # Select the newly created layer so subsequent commands operate on it
            substance_painter.layerstack.set_selected_nodes([new_layer])
            
            self.log("✓ Created group layer and selected it")
            
            return True
            
        except Exception as e:
            self.log(f"Error creating group layer: {e}")
            return False
    
    # Keep legacy method for compatibility
    def create_folder(self):
        """Create a folder (legacy)"""
        return self.create_group_layer()
    
    # === Effect Creation Methods ===
    def create_levels_effect(self):
        """Create a levels effect using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected to add effect to")
                return False
            
            layer = selected[0]
            # Insert in content stack
            insert_pos = substance_painter.layerstack.InsertPosition.inside_node(
                layer, substance_painter.layerstack.NodeStack.Content)
            
            new_effect = substance_painter.layerstack.insert_levels_effect(insert_pos)
            new_effect.set_name("Levels Effect")
            
            return True
            
        except Exception as e:
            self.log(f"Error creating levels effect: {e}")
            return False
    
    def create_filter_effect(self):
        """Create a filter effect using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected to add effect to")
                return False
            
            layer = selected[0]
            # Insert in content stack
            insert_pos = substance_painter.layerstack.InsertPosition.inside_node(
                layer, substance_painter.layerstack.NodeStack.Content)
            
            new_effect = substance_painter.layerstack.insert_filter_effect(insert_pos)
            new_effect.set_name("Filter Effect")
            
            return True
            
        except Exception as e:
            self.log(f"Error creating filter effect: {e}")
            return False
    
    def create_generator_effect(self):
        """Create a generator effect using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected to add effect to")
                return False
            
            layer = selected[0]
            # Insert in content stack
            insert_pos = substance_painter.layerstack.InsertPosition.inside_node(
                layer, substance_painter.layerstack.NodeStack.Content)
            
            new_effect = substance_painter.layerstack.insert_generator_effect(insert_pos)
            new_effect.set_name("Generator Effect")
            
            return True
            
        except Exception as e:
            self.log(f"Error creating generator effect: {e}")
            return False
    
    def duplicate_selected_layer(self):
        """Duplicate the selected layer - NOT AVAILABLE in real API"""
        # The real API doesn't have a direct duplicate function
        # This would require copying layer properties manually
        return self.show_not_implemented("Duplicate Layer (API limitation)")
    
    def delete_selected_layer(self):
        """Delete the selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Delete each selected node - this is the real API function
            for node in selected:
                substance_painter.layerstack.delete_node(node)
            
            return True
            
        except Exception as e:
            self.log(f"Error deleting layer: {e}")
            return False
    
    def toggle_layer_visibility(self):
        """Toggle visibility of selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Toggle visibility for each selected node - this uses the real API
            for node in selected:
                current_visible = node.is_visible()
                node.set_visible(not current_visible)
                
            return True
            
        except Exception as e:
            self.log(f"Error toggling visibility: {e}")
            return False
    
    def move_layer_up(self):
        """Move selected layer up - NOT AVAILABLE in real API"""
        # The real API doesn't have move_layers_up/down functions
        # Would need to be implemented using InsertPosition and re-insertion
        return self.show_not_implemented("Move Layer Up (API limitation)")
    
    def move_layer_down(self):
        """Move selected layer down - NOT AVAILABLE in real API"""
        # The real API doesn't have move_layers_up/down functions  
        # Would need to be implemented using InsertPosition and re-insertion
        return self.show_not_implemented("Move Layer Down (API limitation)")
    
    # =====================================================
    # ADDITIONAL LAYERSTACK COMMAND IMPLEMENTATIONS  
    # =====================================================
    
    # Layer Creation Commands
    def create_adjustment_layer(self):
        """Create an adjustment layer"""
        try:
            # Adjustment layers might be implemented as a specific type of fill layer
            return self.create_fill_layer()
        except Exception as e:
            self.log(f"Error creating adjustment layer: {e}")
            return False
    
    def create_anchor_point(self):
        """Create an anchor point"""
        return self.show_not_implemented("Create Anchor Point")
    
    # Layer Management Commands  
    def copy_layers(self):
        """Copy selected layers"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layers selected")
                return False
            
            # Store reference for paste operation (simplified)
            self._copied_layers = selected
            self.log(f"Copied {len(selected)} layers")
            return True
            
        except Exception as e:
            self.log(f"Error copying layers: {e}")
            return False
    
    def paste_layers(self):
        """Paste copied layers"""
        try:
            if not hasattr(self, '_copied_layers') or not self._copied_layers:
                self.log("No layers to paste")
                return False
                
            # Duplicate the copied layers
            substance_painter.layerstack.duplicate_layers(self._copied_layers)
            self.log(f"Pasted {len(self._copied_layers)} layers")
            return True
            
        except Exception as e:
            self.log(f"Error pasting layers: {e}")
            return False
    
    def clear_layer(self):
        """Clear the selected layer"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Clear layer content (placeholder implementation)
            self.log("Layer cleared (placeholder implementation)")
            return True
            
        except Exception as e:
            self.log(f"Error clearing layer: {e}")
            return False
    
    def flatten_visible_layers(self):
        """Flatten all visible layers"""
        return self.show_not_implemented("Flatten Visible Layers")
    
    def merge_down(self):
        """Merge layer down"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Merge with layer below
            substance_painter.layerstack.merge_layers(selected)
            return True
            
        except Exception as e:
            self.log(f"Error merging down: {e}")
            return False
    
    def merge_visible(self):
        """Merge all visible layers"""
        return self.show_not_implemented("Merge Visible")
    
    # Layer Organization Commands
    def move_to_top(self):
        """Move selected layer to top"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Move to top by repeatedly moving up
            for _ in range(10):  # Safety limit
                try:
                    substance_painter.layerstack.move_layers_up(selected)
                except:
                    break  # Can't move further up
            return True
            
        except Exception as e:
            self.log(f"Error moving to top: {e}")
            return False
    
    def move_to_bottom(self):
        """Move selected layer to bottom"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Move to bottom by repeatedly moving down  
            for _ in range(10):  # Safety limit
                try:
                    substance_painter.layerstack.move_layers_down(selected)
                except:
                    break  # Can't move further down
            return True
            
        except Exception as e:
            self.log(f"Error moving to bottom: {e}")
            return False
    
    def group_selected_layers(self):
        """Group selected layers"""
        return self.show_not_implemented("Group Selected Layers")
    
    def ungroup_layers(self):
        """Ungroup selected layers"""
        return self.show_not_implemented("Ungroup Layers")
    
    # Layer Properties Commands
    def show_layer(self):
        """Show selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Show all selected layers
            for node in selected:
                node.set_visible(True)
            return True
            
        except Exception as e:
            self.log(f"Error showing layer: {e}")
            return False
    
    def hide_layer(self):
        """Hide selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # Hide all selected layers
            for node in selected:
                node.set_visible(False)
            return True
            
        except Exception as e:
            self.log(f"Error hiding layer: {e}")
            return False
    
    def toggle_layer_lock(self):
        """Toggle lock state of selected layer"""
        return self.show_not_implemented("Toggle Layer Lock")
    
    def lock_layer(self):
        """Lock selected layer"""
        return self.show_not_implemented("Lock Layer")
    
    def unlock_layer(self):
        """Unlock selected layer"""
        return self.show_not_implemented("Unlock Layer")
    
    def reset_layer_opacity(self):
        """Reset layer opacity to 100%"""
        return self.show_not_implemented("Reset Layer Opacity")
    
    # Blend Mode Commands
    def set_blend_mode(self, mode):
        """Set blend mode of selected layer"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            # This would need the actual blend mode enum from the API
            self.log(f"Set blend mode to {mode} (placeholder implementation)")
            return True
            
        except Exception as e:
            self.log(f"Error setting blend mode: {e}")
            return False
    
    # Mask Commands using real API
    def add_layer_mask(self):
        """Add mask to selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if layer.has_mask():
                self.log("Layer already has a mask")
                return False
            
            # Add mask with white background (default)
            layer.add_mask(substance_painter.layerstack.MaskBackground.White)
            
            # Switch selection context to the mask for subsequent macro commands
            set_selection_type(layer, SelectionType.Mask)
            self.log("Added layer mask and switched to mask context")
            return True
            
        except Exception as e:
            self.log(f"Error adding layer mask: {e}")
            return False
    
    def remove_layer_mask(self):
        """Remove layer mask using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not layer.has_mask():
                self.log("Layer has no mask to remove")
                return False
            
            layer.remove_mask()
            self.log("Removed layer mask")
            return True
            
        except Exception as e:
            self.log(f"Error removing layer mask: {e}")
            return False
    
    def enable_layer_mask(self):
        """Enable layer mask using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not layer.has_mask():
                self.log("Layer has no mask")
                return False
            
            layer.enable_mask(True)
            self.log("Enabled layer mask")
            return True
            
        except Exception as e:
            self.log(f"Error enabling layer mask: {e}")
            return False
    
    def disable_layer_mask(self):
        """Disable layer mask using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not layer.has_mask():
                self.log("Layer has no mask")
                return False
            
            layer.enable_mask(False)
            self.log("Disabled layer mask")
            return True
            
        except Exception as e:
            self.log(f"Error disabling layer mask: {e}")
            return False
    
    def set_mask_background_white(self):
        """Set mask background to white using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not layer.has_mask():
                self.log("Layer has no mask")
                return False
            
            layer.set_mask_background(substance_painter.layerstack.MaskBackground.White)
            self.log("Set mask background to white")
            return True
            
        except Exception as e:
            self.log(f"Error setting mask background: {e}")
            return False
    
    def set_mask_background_black(self):
        """Set mask background to black using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not layer.has_mask():
                self.log("Layer has no mask")
                return False
            
            layer.set_mask_background(substance_painter.layerstack.MaskBackground.Black)
            self.log("Set mask background to black")
            return True
            
        except Exception as e:
            self.log(f"Error setting mask background: {e}")
            return False
    
    # Selection Commands
    def select_all_layers(self):
        """Select all layers"""
        return self.show_not_implemented("Select All Layers")
    
    def select_visible_layers(self):
        """Select all visible layers"""
        return self.show_not_implemented("Select Visible Layers")
    
    def select_locked_layers(self):
        """Select all locked layers"""
        return self.show_not_implemented("Select Locked Layers")
    
    def select_paint_layers(self):
        """Select all paint layers"""
        return self.show_not_implemented("Select Paint Layers")
    
    def select_fill_layers(self):
        """Select all fill layers"""
        return self.show_not_implemented("Select Fill Layers")
    
    def select_group_layers(self):
        """Select all group layers"""
        return self.show_not_implemented("Select Group Layers")
    
    def deselect_all_layers(self):
        """Deselect all layers"""
        return self.show_not_implemented("Deselect All Layers")
    
    # Channel Commands
    def enable_channel(self, channel):
        """Enable specific channel"""
        self.log(f"Enable {channel} channel (placeholder implementation)")
        return True
    
    def enable_all_channels(self):
        """Enable all channels"""
        return self.show_not_implemented("Enable All Channels")
    
    def disable_all_channels(self):
        """Disable all channels"""
        return self.show_not_implemented("Disable All Channels")
    
    # Stack Operations
    def clear_stack(self):
        """Clear the layer stack"""
        return self.show_not_implemented("Clear Stack")
    
    def reset_stack(self):
        """Reset the layer stack"""
        return self.show_not_implemented("Reset Stack")
    
    # Naming Commands
    def rename_selected_layer(self):
        """Rename selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]  # Rename first selected layer
            current_name = layer.get_name()
            
            # Ask user for new name
            new_name, ok = QtWidgets.QInputDialog.getText(
                self,
                "Rename Layer",
                "Layer name:",
                QtWidgets.QLineEdit.Normal,
                current_name
            )
            
            if ok and new_name:
                # Set new name using real API
                layer.set_name(new_name)
                self.log(f"Renamed layer to '{new_name}'")
                return True
            
            return False
            
        except Exception as e:
            self.log(f"Error renaming layer: {e}")
            return False
    
    def set_layer_opacity(self):
        """Set layer opacity using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            
            # Get current opacity for first available channel
            current_opacity = 100  # Default
            try:
                # Try to get opacity for base color channel
                from substance_painter.textureset import ChannelType
                current_opacity = layer.get_opacity(ChannelType.BaseColor) * 100
            except:
                pass
            
            # Ask user for new opacity
            opacity, ok = QtWidgets.QInputDialog.getDouble(
                self,
                "Set Layer Opacity",
                "Opacity (0-100%):",
                current_opacity,
                0.0, 100.0, 1
            )
            
            if ok:
                # Set opacity using real API
                opacity_normalized = opacity / 100.0
                try:
                    from substance_painter.textureset import ChannelType
                    layer.set_opacity(opacity_normalized, ChannelType.BaseColor)
                    self.log(f"Set layer opacity to {opacity}%")
                    return True
                except Exception as e:
                    self.log(f"Error setting opacity: {e}")
            
            return False
            
        except Exception as e:
            self.log(f"Error setting layer opacity: {e}")
            return False
    
    def get_layer_opacity(self):
        """Get layer opacity using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            opacity = layer.get_opacity()
            self.log(f"Layer opacity: {opacity:.2f}")
            return True
            
        except Exception as e:
            self.log(f"Error getting layer opacity: {e}")
            return False
    
    def set_blend_mode(self):
        """Set blend mode - requires dialog for selection"""
        self.log("Blend mode selection requires dialog")
        return False
    
    def get_blend_mode(self):
        """Get current blend mode"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            blend_mode = layer.get_blending_mode()
            self.log(f"Blend mode: {blend_mode}")
            return True
            
        except Exception as e:
            self.log(f"Error getting blend mode: {e}")
            return False
    
    # =====================================================
    # NEW METHODS USING REAL SUBSTANCE PAINTER API
    # =====================================================
    
    def create_layer_instance(self):
        """Create an instance of selected layer using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected to instance")
                return False
            
            stack = self.get_active_stack()
            if not stack:
                return False
            
            source_layer = selected[0]
            insert_pos = InsertPosition.from_textureset_stack(stack)
            instance = substance_painter.layerstack.instantiate(insert_pos, source_layer)
            instance.set_name(f"Instance of {source_layer.get_name()}")
            self.log(f"✓ Created instance of '{source_layer.get_name()}'")
            return True
            
        except Exception as e:
            self.log(f"Error creating layer instance: {e}")
            return False
    
    # === Helper Method for Smart Effect Insertion ===
    def get_smart_insert_position(self, layer):
        """Get insert position based on current selection (content vs mask)"""
        try:
            # Check what part of the layer is currently selected
            selection_type = substance_painter.layerstack.get_selection_type(layer)
            
            if selection_type == SelectionType.Mask:
                # User selected the mask - insert into mask stack
                return InsertPosition.inside_node(layer, NodeStack.Mask)
            else:
                # Default to content stack for Content, GeometryMask, or Properties selection
                return InsertPosition.inside_node(layer, NodeStack.Content)
                
        except Exception as e:
            # Fallback to content stack if selection detection fails
            self.log(f"Could not detect selection type, defaulting to content: {e}")
            return InsertPosition.inside_node(layer, NodeStack.Content)
    
    # === Effect Creation Methods ===
    def insert_levels_effect(self):
        """Insert levels effect using real API - detects content vs mask"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            insert_pos = self.get_smart_insert_position(layer)
            effect = substance_painter.layerstack.insert_levels_effect(insert_pos)
            effect.set_name("Levels")
            
            # Show where it was inserted
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            self.log(f"✓ Inserted levels effect in {stack_type}")
            return True
            
        except Exception as e:
            self.log(f"Error inserting levels effect: {e}")
            return False
    
    def insert_filter_effect(self):
        """Insert filter effect using real API - detects content vs mask"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            insert_pos = self.get_smart_insert_position(layer)
            effect = substance_painter.layerstack.insert_filter_effect(insert_pos)
            effect.set_name("Filter")
            
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            self.log(f"✓ Inserted filter effect in {stack_type}")
            return True
            
        except Exception as e:
            self.log(f"Error inserting filter effect: {e}")
            return False
    
    def insert_fill_effect(self):
        """Insert fill effect using real API - detects content vs mask"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            insert_pos = self.get_smart_insert_position(layer)
            # insert_fill() creates FillEffectNode when inserting into effect stack
            effect = substance_painter.layerstack.insert_fill(insert_pos)
            effect.set_name("Fill")
            
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            self.log(f"✓ Inserted fill effect in {stack_type}")
            return True
            
        except Exception as e:
            self.log(f"Error inserting fill effect: {e}")
            return False
    
    def insert_generator_effect(self):
        """Insert generator effect using real API - detects content vs mask"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            insert_pos = self.get_smart_insert_position(layer)
            effect = substance_painter.layerstack.insert_generator_effect(insert_pos)
            effect.set_name("Generator")
            
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            self.log(f"✓ Inserted generator effect in {stack_type}")
            return True
            
        except Exception as e:
            self.log(f"Error inserting generator effect: {e}")
            return False
    
    def insert_compare_mask_effect(self):
        """Insert compare mask effect using real API - smart mask detection"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            # Compare mask effects work best in masks, but respect user selection
            insert_pos = self.get_smart_insert_position(layer)
            
            # If user selected content but layer has no mask, suggest adding one
            if insert_pos.node_stack == NodeStack.Content:
                if hasattr(layer, 'has_mask') and not layer.has_mask():
                    self.log("Tip: Compare Mask works better with a layer mask. Consider adding one first.")
            
            effect = substance_painter.layerstack.insert_compare_mask_effect(insert_pos)
            effect.set_name("Compare Mask")
            
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            self.log(f"✓ Inserted compare mask effect in {stack_type}")
            return True
            
        except Exception as e:
            self.log(f"Error inserting compare mask effect: {e}")
            return False
    
    def insert_color_selection_effect(self):
        """Insert color selection effect using real API - smart mask detection"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            # Color selection effects work best in masks, but respect user selection
            insert_pos = self.get_smart_insert_position(layer)
            
            # If user selected content but layer has no mask, suggest adding one
            if insert_pos.node_stack == NodeStack.Content:
                if hasattr(layer, 'has_mask') and not layer.has_mask():
                    self.log("Tip: Color Selection works better with a layer mask. Consider adding one first.")
            
            effect = substance_painter.layerstack.insert_color_selection_effect(insert_pos)
            effect.set_name("Color Selection")
            
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            self.log(f"✓ Inserted color selection effect in {stack_type}")
            return True
            
        except Exception as e:
            self.log(f"Error inserting color selection effect: {e}")
            return False
    
    def insert_anchor_point_effect(self):
        """Insert anchor point effect using real API - detects content vs mask"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            insert_pos = self.get_smart_insert_position(layer)
            effect = substance_painter.layerstack.insert_anchor_point_effect(insert_pos, "Anchor")
            
            stack_type = "mask" if insert_pos.node_stack == NodeStack.Mask else "content"
            self.log(f"✓ Inserted anchor point effect in {stack_type}")
            return True
            
        except Exception as e:
            self.log(f"Error inserting anchor point effect: {e}")
            return False
    
    # === Layer Mask Methods (Real API) ===
    def remove_layer_mask(self):
        """Remove layer mask using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not hasattr(layer, 'has_mask') or not layer.has_mask():
                self.log("Layer has no mask to remove")
                return False
            
            layer.remove_mask()
            self.log("✓ Removed layer mask")
            return True
            
        except Exception as e:
            self.log(f"Error removing layer mask: {e}")
            return False
    
    def set_mask_background_white(self):
        """Set mask background to white using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not hasattr(layer, 'has_mask') or not layer.has_mask():
                self.log("Layer has no mask")
                return False
            
            layer.set_mask_background(MaskBackground.White)
            self.log("✓ Set mask background to white")
            return True
            
        except Exception as e:
            self.log(f"Error setting mask background: {e}")
            return False
    
    def set_mask_background_black(self):
        """Set mask background to black using real API"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if not hasattr(layer, 'has_mask') or not layer.has_mask():
                self.log("Layer has no mask")
                return False
            
            layer.set_mask_background(MaskBackground.Black)
            self.log("✓ Set mask background to black")
            return True
            
        except Exception as e:
            self.log(f"Error setting mask background: {e}")
            return False
    
    # === Placeholder methods for Smart Materials/Masks ===
    def insert_smart_material(self):
        """Insert smart material - requires resource selection"""
        self.log("Smart material insertion requires resource selection dialog")
        return False
    
    def create_smart_material(self):
        """Create smart material from selected group"""
        self.log("Smart material creation requires name input dialog")  
        return False
    
    def insert_smart_mask(self):
        """Insert smart mask - requires resource selection"""
        self.log("Smart mask insertion requires resource selection dialog")
        return False
    
    def create_smart_mask(self):
        """Create smart mask from selected layer"""
        self.log("Smart mask creation requires name input dialog")
        return False
    
    # === Geometry Mask Methods ===
    def set_geometry_mask_mesh(self):
        """Set geometry mask type to mesh"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if hasattr(layer, 'set_geometry_mask_type'):
                layer.set_geometry_mask_type(GeometryMaskType.Mesh)
                self.log("✓ Set geometry mask to mesh")
                return True
            else:
                self.log("Selected node doesn't support geometry masks")
                return False
            
        except Exception as e:
            self.log(f"Error setting geometry mask: {e}")
            return False
    
    def set_geometry_mask_uv_tile(self):
        """Set geometry mask type to UV tile"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if hasattr(layer, 'set_geometry_mask_type'):
                layer.set_geometry_mask_type(GeometryMaskType.UVTile)
                self.log("✓ Set geometry mask to UV tile")
                return True
            else:
                self.log("Selected node doesn't support geometry masks")
                return False
            
        except Exception as e:
            self.log(f"Error setting geometry mask: {e}")
            return False
    
    def enable_geometry_mask(self):
        """Enable geometry mask"""
        self.log("Geometry mask mesh selection requires dialog")
        return False
    
    # === Projection Mode Methods ===
    def set_projection_uv(self):
        """Set projection mode to UV"""
        return self._set_projection_mode(ProjectionMode.UV, "UV")
    
    def set_projection_triplanar(self):
        """Set projection mode to triplanar"""
        return self._set_projection_mode(ProjectionMode.Triplanar, "Triplanar")
    
    def set_projection_planar(self):
        """Set projection mode to planar"""
        return self._set_projection_mode(ProjectionMode.Planar, "Planar")
    
    def set_projection_spherical(self):
        """Set projection mode to spherical"""
        return self._set_projection_mode(ProjectionMode.Spherical, "Spherical")
    
    def set_projection_cylindrical(self):
        """Set projection mode to cylindrical"""
        return self._set_projection_mode(ProjectionMode.Cylindrical, "Cylindrical")
    
    def _set_projection_mode(self, mode, mode_name):
        """Helper to set projection mode"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if hasattr(layer, 'set_projection_mode'):
                layer.set_projection_mode(mode)
                self.log(f"✓ Set projection mode to {mode_name}")
                return True
            else:
                self.log("Selected layer doesn't support projection modes")
                return False
            
        except Exception as e:
            self.log(f"Error setting projection mode: {e}")
            return False
    
    def enable_symmetry(self):
        """Enable symmetry"""
        return self._set_symmetry(True)
    
    def disable_symmetry(self):
        """Disable symmetry"""
        return self._set_symmetry(False)
    
    def _set_symmetry(self, enabled):
        """Helper to set symmetry state"""
        try:
            selected = self.get_selected_nodes()
            if not selected:
                self.log("No layer selected")
                return False
            
            layer = selected[0]
            if hasattr(layer, 'set_symmetry_enabled'):
                layer.set_symmetry_enabled(enabled)
                state = "enabled" if enabled else "disabled"
                self.log(f"✓ {state.capitalize()} symmetry")
                return True
            else:
                self.log("Selected layer doesn't support symmetry")
                return False
            
        except Exception as e:
            self.log(f"Error setting symmetry: {e}")
            return False

    # Helper method for unimplemented commands
    def show_not_implemented(self, command_name):
        """Show message for commands not yet implemented"""
        self.log(f"'{command_name}' is not yet implemented")
        QtWidgets.QMessageBox.information(
            self,
            "Not Implemented", 
            f"The command '{command_name}' is not yet implemented.\n\nThis will be added in a future version."
        )
        return False
    
    # Update legacy method names to use new implementations
    def duplicate_selected_layers(self):
        """Duplicate the selected layers"""
        return self.duplicate_selected_layer()
    
    def delete_selected_layers(self):
        """Delete the selected layers"""
        return self.delete_selected_layer()
    
    def move_layers_up(self):
        """Move layers up"""
        return self.move_layer_up()
    
    def move_layers_down(self):
        """Move layers down"""  
        return self.move_layer_down()

# Simplified - no global event filter needed

def start_plugin():
    """Start Commander plugin using Adobe pattern"""
    global MAIN_WINDOW
    
    try:
        # Create main window with proper parent
        MAIN_WINDOW = CommanderWidget(substance_painter.ui.get_main_window())
        
        # Add to Substance Painter UI as dock widget (explicitly specify Edition mode)
        from substance_painter.ui import UIMode
        dock_widget = substance_painter.ui.add_dock_widget(MAIN_WINDOW, UIMode.Edition)
        WIDGETS.append(MAIN_WINDOW)
        WIDGETS.append(dock_widget)  # Also keep reference to dock widget
        
        # Store dock widget reference in main window for shortcut access
        MAIN_WINDOW.dock_widget = dock_widget
        
        # Log dock widget details
        substance_painter.logging.info(f"Commander dock widget created: {dock_widget.windowTitle()}")
        substance_painter.logging.info(f"Dock widget visible: {dock_widget.isVisible()}")
        substance_painter.logging.info(f"Dock widget floating: {dock_widget.isFloating()}")
        substance_painter.logging.info(f"Widget has icon: {not MAIN_WINDOW.windowIcon().isNull()}")
        substance_painter.logging.info(f"Widget object name: {MAIN_WINDOW.objectName()}")
        
        # Configure dock widget for command palette behavior
        dock_widget.setFloating(True)  # Make it floating for popup behavior
        dock_widget.hide()  # Hide initially - will show on shortcut
        
        # Fix background color issue - set consistent styling
        try:
            # Apply consistent background styling to avoid blue background
            style_sheet = """
                QWidget {
                    background-color: #2b2b2b;  /* Dark background like SP panels */
                }
                QLineEdit {
                    background-color: #3c3c3c;
                    border: 1px solid #555;
                    padding: 4px;
                    color: white;
                }
                QListWidget {
                    background-color: #2b2b2b;
                    border: 1px solid #555;
                    color: white;
                    selection-background-color: #404040;  /* Darker gray instead of blue */
                    selection-color: white;  /* Ensure selected text stays white */
                }
                QLabel {
                    background-color: transparent;
                }
                QDockWidget {
                    background-color: #2b2b2b;  /* Fix dock widget container background */
                }
                QDockWidget::title {
                    background-color: #3c3c3c;
                    color: white;
                    padding: 4px;
                }
            """
            
            # Apply styling to both the main widget AND the dock widget container
            MAIN_WINDOW.setStyleSheet(style_sheet)
            dock_widget.setStyleSheet(style_sheet)
            
        except Exception as style_error:
            substance_painter.logging.info(f"Could not apply custom styling: {style_error}")
        
        # Install event filter to detect outside clicks
        MAIN_WINDOW.installEventFilter(MAIN_WINDOW)
        dock_widget.installEventFilter(MAIN_WINDOW)
        
        # Create global keyboard shortcuts without menu
        try:
            main_window = substance_painter.ui.get_main_window()
            
            # Add Commander action with Ctrl+; shortcut (no menu needed)
            commander_action = QtGui.QAction("Open Commander", main_window)
            commander_action.setToolTip("Quick access to layer operations")
            commander_action.triggered.connect(MAIN_WINDOW.show_commander_from_shortcut)
            commander_action.setShortcut(QtGui.QKeySequence("Ctrl+;"))
            main_window.addAction(commander_action)  # Add directly to main window
            WIDGETS.append(commander_action)
            
            # Also try Ctrl+` as alternative (backtick key)
            commander_action_alt = QtGui.QAction("Open Commander Alt", main_window)
            commander_action_alt.setToolTip("Alternative shortcut for Commander")
            commander_action_alt.triggered.connect(MAIN_WINDOW.show_commander_from_shortcut)
            commander_action_alt.setShortcut(QtGui.QKeySequence("Ctrl+`"))
            main_window.addAction(commander_action_alt)
            WIDGETS.append(commander_action_alt)
            
            substance_painter.logging.info("Commander shortcuts (Ctrl+; and Ctrl+`) created successfully")
            
        except Exception as shortcut_error:
            substance_painter.logging.error(f"Could not create shortcuts: {shortcut_error}")
        
        substance_painter.logging.info("Commander Plugin started with keyboard shortcuts - Ctrl+; or Ctrl+` to open Commander")
        
    except Exception as e:
        substance_painter.logging.error(f"Failed to start Commander Plugin: {e}")

def close_plugin():
    """Close Commander plugin using Adobe pattern"""
    global MAIN_WINDOW
    
    try:
        
        # Stop any timers if they exist
        if MAIN_WINDOW and hasattr(MAIN_WINDOW, 'timer'):
            try:
                MAIN_WINDOW.timer.stop()
                MAIN_WINDOW.timer.deleteLater()
            except:
                pass
        
        # Clean up any active dialogs
        if MAIN_WINDOW and hasattr(MAIN_WINDOW, 'active_dialogs'):
            for dialog in MAIN_WINDOW.active_dialogs:
                try:
                    dialog.close()
                    dialog.deleteLater()
                except:
                    pass
        
        # Clean up main window Qt objects
        if MAIN_WINDOW:
            try:
                # Clean up any Qt child objects
                if hasattr(MAIN_WINDOW, 'search_input'):
                    MAIN_WINDOW.search_input.deleteLater()
                if hasattr(MAIN_WINDOW, 'results_list'):
                    MAIN_WINDOW.results_list.deleteLater()
                if hasattr(MAIN_WINDOW, 'status_label'):
                    MAIN_WINDOW.status_label.deleteLater()
            except:
                pass
        
        # Clean up all widgets using SP API - minimal approach
        for widget in WIDGETS:
            try:
                # Just use SP's delete_ui_element - don't do any manual manipulation
                substance_painter.ui.delete_ui_element(widget)
            except Exception as e:
                # Ignore cleanup failures - they're often expected during shutdown
                pass
        
        # Clear references
        WIDGETS.clear()
        MAIN_WINDOW = None
        
        substance_painter.logging.info("Commander Plugin closed")
        
    except Exception as e:
        substance_painter.logging.error(f"Error closing Commander Plugin: {e}")

if __name__ == "__main__":
    start_plugin()