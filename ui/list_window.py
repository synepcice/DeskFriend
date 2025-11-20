"""
Main list window for DeskFriend.
Semi-transparent, draggable window displaying a todo list.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QScrollArea, QComboBox, QLineEdit, QSizeGrip)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QPalette, QColor
from pathlib import Path
from .list_item_widget import ListItemWidget


class ListWindow(QWidget):
    """Main window displaying a todo list."""
    
    list_changed = pyqtSignal(str)  # list_id
    settings_requested = pyqtSignal()
    search_requested = pyqtSignal()
    data_changed = pyqtSignal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_list = None
        self.drag_position = None
        
        self.setup_ui()
        self.load_last_list()
    
    def setup_ui(self):
        """Setup the UI components."""
        # Window flags for frameless, always on top, semi-transparent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)  # Required for hover events without mouse press
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        self.header = self.create_header()
        main_layout.addWidget(self.header)
        
        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        # Items container
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(1)
        self.items_layout.addStretch()
        
        self.scroll_area.setWidget(self.items_widget)
        self.container = QWidget() # Container for scroll area to apply styles cleanly if needed
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.addWidget(self.scroll_area)
        
        main_layout.addWidget(self.container, 1) # Give it stretch factor
        
        # Footer
        self.footer = self.create_footer()
        main_layout.addWidget(self.footer)

        # Apply initial style
        self.update_style()
        
        # Resize state
        self.resizing = False
        self.resize_edge = None
        self.RESIZE_MARGIN = 5

    def create_header(self) -> QWidget:
        """Create the header with title and list selector."""
        header = QWidget()
        header.setFixedHeight(40)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)
        
        # List selector dropdown
        self.list_selector = QComboBox()
        self.list_selector.currentIndexChanged.connect(self.on_list_selected)
        layout.addWidget(self.list_selector, 1)
        
        # Get icon path for stylesheet
        icons_path = Path(__file__).parent.parent / "Icons"
        develop_icon_path = (icons_path / "Develop.png").as_posix()
        
        header.setStyleSheet(f"""
            QWidget {{
                background-color: rgba(50, 50, 50, 0.95);
                border-bottom: 2px solid rgba(0, 0, 0, 0.5);
            }}
            QComboBox {{
                color: white;
                background-color: rgba(70, 70, 70, 0.9);
                border: 1px solid rgba(0, 0, 0, 0.6);
                border-radius: 3px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 25px;
                border-left: 1px solid rgba(0, 0, 0, 0.3);
            }}
            QComboBox::down-arrow {{
                image: url({develop_icon_path});
                width: 16px;
                height: 16px;
                margin-right: 2px;
            }}
            QComboBox QAbstractItemView {{
                background-color: rgba(60, 60, 60, 0.98);
                color: white;
                selection-background-color: rgba(100, 100, 100, 0.95);
                border: 2px solid rgba(0, 0, 0, 0.8);
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 6px;
                min-height: 25px;
            }}
        """)
        
        return header
    
    def create_footer(self) -> QWidget:
        """Create the footer with action buttons."""
        footer = QWidget()
        footer.setFixedHeight(40)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(10, 5, 10, 5)
        
        icons_path = Path(__file__).parent.parent / "Icons"
        
        # Search button
        self.search_button = QPushButton()
        self.search_button.setIcon(QIcon(str(icons_path / "Search.png")))
        self.search_button.setFixedSize(28, 28)
        self.search_button.setIconSize(self.search_button.size())
        self.search_button.clicked.connect(self.search_requested.emit)
        
        # Settings button
        self.settings_button = QPushButton()
        self.settings_button.setIcon(QIcon(str(icons_path / "Params.png")))
        self.settings_button.setFixedSize(28, 28)
        self.settings_button.setIconSize(self.settings_button.size())
        self.settings_button.clicked.connect(self.settings_requested.emit)
        
        layout.addStretch()
        layout.addWidget(self.search_button)
        layout.addWidget(self.settings_button)
        
        footer.setStyleSheet("""
            QWidget {
                background-color: rgba(50, 50, 50, 0.95);
                border-top: 2px solid rgba(0, 0, 0, 0.5);
            }
            QPushButton {
                background-color: rgba(70, 70, 70, 0.8);
                border: 1px solid rgba(0, 0, 0, 0.6);
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 0.95);
                border: 1px solid rgba(0, 0, 0, 0.8);
            }
            QPushButton:pressed {
                background-color: rgba(60, 60, 60, 0.95);
            }
        """)
        
        return footer
    
    def update_style(self):
        """Update the style based on current list color."""
        if not self.current_list:
            return
        
        color = QColor(self.current_list.color)
        
        # Extract RGB values
        r, g, b = color.red(), color.green(), color.blue()
        
        # Container style - Transparent, sans bordure
        self.container.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }}
        """)
        
        # Scroll area - fond coloré semi-transparent
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: rgba({r}, {g}, {b}, 0.3);
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: rgba(0, 0, 0, 0.2);
                width: 8px;
                border-radius: 4px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(0, 0, 0, 0.4);
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: rgba(0, 0, 0, 0.6);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
    
    def load_last_list(self):
        """Load the last viewed list or first available list."""
        all_lists = self.data_manager.get_all_lists()
        
        if not all_lists:
            return
        
        # Try to load last list
        if self.data_manager.settings.last_list_id:
            last_list = self.data_manager.get_list(self.data_manager.settings.last_list_id)
            if last_list:
                self.set_current_list(last_list)
                return
        
        # Load first list
        self.set_current_list(all_lists[0])
    
    def refresh_list_selector(self):
        """Refresh the list selector dropdown."""
        self.list_selector.blockSignals(True)
        self.list_selector.clear()
        
        all_lists = self.data_manager.get_all_lists()
        for lst in all_lists:
            self.list_selector.addItem(lst.name, lst.id)
        
        # Select current list
        if self.current_list:
            index = self.list_selector.findData(self.current_list.id)
            if index >= 0:
                self.list_selector.setCurrentIndex(index)
        
        self.list_selector.blockSignals(False)
    
    def set_current_list(self, todo_list):
        """Set the current list to display."""
        self.current_list = todo_list
        self.data_manager.settings.last_list_id = todo_list.id
        self.data_manager.save()
        
        self.refresh_list_selector()
        self.refresh_items()
        self.update_style()
        self.list_changed.emit(todo_list.id)
    
    def refresh_items(self):
        """Refresh the items display."""
        # Clear existing items
        while self.items_layout.count() > 1:  # Keep the stretch
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not self.current_list:
            return
        
        is_clipboard = self.current_list.id == self.data_manager.CLIPBOARD_LIST_ID
        
        # Add all items
        for i, item in enumerate(self.current_list.items):
            item_widget = ListItemWidget(item, is_clipboard)
            item_widget.item_updated.connect(self.on_item_updated)
            item_widget.item_validated.connect(self.on_item_validated)
            item_widget.item_deleted.connect(self.on_item_deleted)
            
            # Wrap in a frame for alternating background
            from PyQt6.QtWidgets import QFrame
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setContentsMargins(0, 0, 0, 0)
            frame_layout.setSpacing(0)
            frame_layout.addWidget(item_widget)
            
            # Set alternating background on FRAME
            if i % 2 == 1:
                frame.setStyleSheet("QFrame { background-color: rgba(0, 0, 0, 65); }")
            else:
                frame.setStyleSheet("QFrame { background-color: transparent; }")
            
            self.items_layout.insertWidget(i, frame)
        
        # Add "Add item" button at the END if not clipboard list
        if not is_clipboard:
            add_widget = self.create_add_item_widget()
            self.items_layout.insertWidget(len(self.current_list.items), add_widget)
    
    def create_add_item_widget(self) -> QWidget:
        """Create the 'Add item' widget."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(5)
        
        icons_path = Path(__file__).parent.parent / "Icons"
        
        # Label
        label = QLabel("Ajouter un élément...")
        
        # Line edit (hidden)
        self.add_line_edit = QLineEdit()
        self.add_line_edit.setPlaceholderText("Entrez le texte...")
        self.add_line_edit.hide()
        self.add_line_edit.returnPressed.connect(self.finish_adding_item)
        
        # Add button (à droite, comme les autres icônes)
        add_button = QPushButton()
        add_button.setIcon(QIcon(str(icons_path / "Add.png")))
        add_button.setFixedSize(24, 24)
        add_button.setIconSize(add_button.size())
        add_button.clicked.connect(self.start_adding_item)
        
        layout.addWidget(label, 1)
        layout.addWidget(self.add_line_edit, 1)
        layout.addWidget(add_button)
        
        widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
            QLabel {
                color: rgba(255, 255, 255, 0.7);
                padding: 6px 8px;
                font-size: 12px;
                font-style: italic;
                border: none;
                background: transparent;
            }
            QLineEdit {
                background-color: white;
                color: black;
                border: none;
                padding: 6px 8px;
                font-size: 12px;
            }
            QPushButton {
                background-color: rgba(0, 0, 0, 0.25);
                border: 1px solid rgba(0, 0, 0, 0.4);
                border-radius: 3px;
                padding: 2px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.4);
            }
        """)
        
        return widget
    
    def start_adding_item(self):
        """Start adding a new item."""
        # Find the add widget
        add_widget = self.items_layout.itemAt(0).widget()
        label = add_widget.findChild(QLabel)
        
        label.hide()
        self.add_line_edit.show()
        self.add_line_edit.setFocus()
    
    def finish_adding_item(self):
        """Finish adding a new item."""
        text = self.add_line_edit.text().strip()
        if text and self.current_list:
            self.current_list.add_item(text)
            self.data_manager.save()
            self.refresh_items()
            self.data_changed.emit()
        
        self.add_line_edit.clear()
        self.add_line_edit.hide()
        
        # Show label again
        add_widget = self.items_layout.itemAt(0).widget()
        label = add_widget.findChild(QLabel)
        label.show()
    
    def on_list_selected(self, index):
        """Handle list selection from dropdown."""
        if index < 0:
            return
        
        list_id = self.list_selector.itemData(index)
        todo_list = self.data_manager.get_list(list_id)
        if todo_list:
            self.set_current_list(todo_list)
    
    def on_item_updated(self, item_id, new_text):
        """Handle item text update."""
        self.data_manager.save()
        self.refresh_items()
        self.data_changed.emit()
    
    def on_item_validated(self, item_id):
        """Handle item validation."""
        self.data_manager.save()
        self.data_changed.emit()
    
    def on_item_deleted(self, item_id):
        """Handle item deletion."""
        if self.current_list:
            self.current_list.remove_item(item_id)
            self.data_manager.save()
            self.refresh_items()
            self.data_changed.emit()
    
    # Drag and drop for window movement and resizing
    def mousePressEvent(self, event):
        """Handle mouse press for dragging or resizing."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.pos()
            rect = self.rect()
            
            # Check for resize zones
            left = pos.x() < self.RESIZE_MARGIN
            right = pos.x() > rect.width() - self.RESIZE_MARGIN
            top = pos.y() < self.RESIZE_MARGIN
            bottom = pos.y() > rect.height() - self.RESIZE_MARGIN
            
            if left or right or top or bottom:
                self.resizing = True
                self.resize_edge = (left, top, right, bottom)
                self.drag_position = event.globalPosition().toPoint()
                event.accept()
                return

            # Allow dragging from header or footer
            if self.header.geometry().contains(pos) or self.footer.geometry().contains(pos):
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging or resizing."""
        pos = event.pos()
        rect = self.rect()
        
        if self.resizing:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.drag_position = event.globalPosition().toPoint()
            
            left, top, right, bottom = self.resize_edge
            new_geo = self.geometry()
            
            if right:
                new_geo.setWidth(max(200, new_geo.width() + delta.x()))
            if bottom:
                new_geo.setHeight(max(150, new_geo.height() + delta.y()))
            if left:
                new_width = max(200, new_geo.width() - delta.x())
                new_geo.setLeft(new_geo.left() + (new_geo.width() - new_width))
            if top:
                new_height = max(150, new_geo.height() - delta.y())
                new_geo.setTop(new_geo.top() + (new_geo.height() - new_height))
                
            self.setGeometry(new_geo)
            event.accept()
            return

        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            return
            
        # Update cursor shape
        left = pos.x() < self.RESIZE_MARGIN
        right = pos.x() > rect.width() - self.RESIZE_MARGIN
        top = pos.y() < self.RESIZE_MARGIN
        bottom = pos.y() > rect.height() - self.RESIZE_MARGIN
        
        if (left and top) or (right and bottom):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif (left and bottom) or (right and top):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        elif left or right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif top or bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release after dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.resizing:
                self.resizing = False
                self.resize_edge = None
                # Save size? Maybe later
            else:
                self.drag_position = None
                # Save position
                self.data_manager.settings.window_position = (self.x(), self.y())
                self.data_manager.save()
