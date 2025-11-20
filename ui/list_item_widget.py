"""
List item widget for DeskFriend.
Displays a single item in a todo list with validation, editing, and tooltip features.
"""

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QToolTip)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QFont, QCursor, QIcon
from datetime import datetime
from pathlib import Path


class ListItemWidget(QWidget):
    """Widget representing a single list item."""
    
    item_updated = pyqtSignal(str, str)  # item_id, new_text
    item_validated = pyqtSignal(str)  # item_id
    item_deleted = pyqtSignal(str)  # item_id
    
    def __init__(self, item, is_clipboard_list=False, parent=None):
        super().__init__(parent)
        self.item = item
        self.is_clipboard_list = is_clipboard_list
        self.is_editing = False
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        """Setup the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(5)
        
        # Text label
        self.text_label = QLabel()
        self.text_label.setWordWrap(False)
        self.text_label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.text_label.mouseDoubleClickEvent = self.start_editing
        self.text_label.enterEvent = self.show_tooltip
        
        # Text edit (hidden by default)
        self.text_edit = QLineEdit()
        self.text_edit.hide()
        self.text_edit.returnPressed.connect(self.finish_editing)
        self.text_edit.editingFinished.connect(self.finish_editing)
        
        # Action button (validate or delete)
        self.action_button = QPushButton()
        self.action_button.setFixedSize(24, 24)
        self.action_button.setIconSize(self.action_button.size())
        self.action_button.clicked.connect(self.on_action_clicked)
        
        layout.addWidget(self.text_label, 1)
        layout.addWidget(self.text_edit, 1)
        layout.addWidget(self.action_button)
        
        # Style - NO BORDERS, allow background to be set
        self.setStyleSheet("""
            QLabel {
                color: white;
                padding: 6px 8px;
                font-size: 12px;
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
    
    def update_display(self):
        """Update the display based on item state."""
        # Truncate text if too long
        display_text = self.item.text
        if len(display_text) > 50:
            display_text = display_text[:47] + "..."
        
        # Apply strikethrough if validated
        if self.item.is_validated:
            self.text_label.setText(f"<s>{display_text}</s>")
        else:
            self.text_label.setText(display_text)
        
        # Update action button icon
        icons_path = Path(__file__).parent.parent / "Icons"
        
        if self.is_clipboard_list or self.item.is_validated:
            # Show delete icon
            icon_path = icons_path / "Delete.png"
            self.action_button.setIcon(QIcon(str(icon_path)))
        else:
            # Show validate icon
            icon_path = icons_path / "Valider.png"
            self.action_button.setIcon(QIcon(str(icon_path)))
    
    def show_tooltip(self, event):
        """Show tooltip with full text and timestamps."""
        tooltip_text = f"<b>Contenu:</b><br>{self.item.text}<br><br>"
        
        # Format timestamps
        created = datetime.fromisoformat(self.item.created_at)
        tooltip_text += f"<b>Créé:</b> {created.strftime('%d/%m/%Y %H:%M:%S')}<br>"
        
        if self.item.modified_at != self.item.created_at:
            modified = datetime.fromisoformat(self.item.modified_at)
            tooltip_text += f"<b>Modifié:</b> {modified.strftime('%d/%m/%Y %H:%M:%S')}<br>"
        
        if self.item.validated_at:
            validated = datetime.fromisoformat(self.item.validated_at)
            tooltip_text += f"<b>Validé:</b> {validated.strftime('%d/%m/%Y %H:%M:%S')}"
        
        QToolTip.showText(QCursor.pos(), tooltip_text, self)
    
    def start_editing(self, event):
        """Start editing the item text."""
        if self.is_editing:
            return
        
        self.is_editing = True
        self.text_label.hide()
        self.text_edit.setText(self.item.text)
        self.text_edit.show()
        self.text_edit.setFocus()
        self.text_edit.selectAll()
    
    def finish_editing(self):
        """Finish editing and save changes."""
        if not self.is_editing:
            return
        
        new_text = self.text_edit.text().strip()
        if new_text and new_text != self.item.text:
            self.item.update_text(new_text)
            self.item_updated.emit(self.item.id, new_text)
        
        # If item was validated, unvalidate it
        if self.item.is_validated:
            self.item.unvalidate()
        
        self.is_editing = False
        self.text_edit.hide()
        self.text_label.show()
        self.update_display()
    
    def on_action_clicked(self):
        """Handle action button click (validate or delete)."""
        if self.is_clipboard_list or self.item.is_validated:
            # Delete item
            self.item_deleted.emit(self.item.id)
        else:
            # Validate item
            self.item.validate()
            self.item_validated.emit(self.item.id)
            self.update_display()

    def contextMenuEvent(self, event):
        """Show context menu."""
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        
        # Copy action
        copy_action = QAction("Copier vers le Presse-Papier", self)
        copy_action.triggered.connect(self.copy_to_clipboard)
        menu.addAction(copy_action)
        
        # Style the menu
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(60, 60, 60, 0.95);
                color: white;
                border: 1px solid rgba(0, 0, 0, 0.5);
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: rgba(100, 100, 100, 0.8);
            }
        """)
        
        menu.exec(event.globalPos())
    
    def copy_to_clipboard(self):
        """Copy item text to clipboard."""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(self.item.text)
