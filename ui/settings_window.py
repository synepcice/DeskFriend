"""
Settings window for DeskFriend.
Manage lists, colors, and clipboard settings.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem,
                             QColorDialog, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon
from pathlib import Path


class SettingsWindow(QDialog):
    """Settings window for managing lists and application settings."""
    
    settings_changed = pyqtSignal()
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()
        self.load_settings()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Paramètres - DeskFriend")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Paramètres")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Lists section
        lists_label = QLabel("Listes:")
        lists_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(lists_label)
        
        # List widget
        self.lists_widget = QListWidget()
        self.lists_widget.setMinimumHeight(200)
        layout.addWidget(self.lists_widget)
        
        # List buttons
        list_buttons = QHBoxLayout()
        
        icons_path = Path(__file__).parent.parent / "Icons"
        
        self.add_list_button = QPushButton(" Ajouter une Liste...")
        self.add_list_button.setIcon(QIcon(str(icons_path / "Add.png")))
        self.add_list_button.clicked.connect(self.add_list)
        
        self.rename_list_button = QPushButton(" Renommer")
        # self.rename_list_button.setIcon(QIcon(str(icons_path / "Edit.png"))) # Icon not guaranteed to exist
        self.rename_list_button.clicked.connect(self.rename_list)

        self.remove_list_button = QPushButton(" Supprimer")
        self.remove_list_button.setIcon(QIcon(str(icons_path / "Delete.png")))
        self.remove_list_button.clicked.connect(self.remove_list)
        
        self.change_color_button = QPushButton("Changer la Couleur")
        self.change_color_button.clicked.connect(self.change_list_color)
        
        list_buttons.addWidget(self.add_list_button)
        list_buttons.addWidget(self.rename_list_button)
        list_buttons.addWidget(self.remove_list_button)
        list_buttons.addWidget(self.change_color_button)
        list_buttons.addStretch()
        
        layout.addLayout(list_buttons)
        
        # Clipboard section
        clipboard_label = QLabel("Gestionnaire de Presse-Papier:")
        clipboard_label.setStyleSheet("font-weight: bold; padding: 5px; margin-top: 10px;")
        layout.addWidget(clipboard_label)
        
        clipboard_layout = QHBoxLayout()
        
        self.clipboard_group = QButtonGroup()
        
        self.clipboard_inactive = QRadioButton("Liste ClipBoard Inactive")
        self.clipboard_active = QRadioButton("Liste ClipBoard Active")
        
        self.clipboard_group.addButton(self.clipboard_inactive)
        self.clipboard_group.addButton(self.clipboard_active)
        
        clipboard_layout.addWidget(self.clipboard_inactive)
        clipboard_layout.addWidget(self.clipboard_active)
        clipboard_layout.addStretch()
        
        layout.addLayout(clipboard_layout)
        
        # Bottom buttons
        layout.addStretch()
        
        bottom_buttons = QHBoxLayout()
        
        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.cancel_button = QPushButton("Annuler")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.save_button)
        bottom_buttons.addWidget(self.cancel_button)
        
        layout.addLayout(bottom_buttons)
        
        # Overall dark theme style
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(50, 50, 50, 0.95);
            }
            QLabel {
                color: white;
            }
            QListWidget {
                background-color: rgba(40, 40, 40, 0.9);
                color: white;
                border: 1px solid rgba(0, 0, 0, 0.6);
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(100, 100, 100, 0.8);
                color: white;
            }
            QListWidget::item:hover {
                background-color: rgba(80, 80, 80, 0.6);
            }
            QPushButton {
                padding: 6px 12px;
                background-color: rgba(70, 70, 70, 0.9);
                color: white;
                border: 1px solid rgba(0, 0, 0, 0.6);
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: rgba(90, 90, 90, 0.95);
            }
            QRadioButton {
                color: white;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
        """)
    
    def load_settings(self):
        """Load current settings."""
        # Load lists
        self.lists_widget.clear()
        for lst in self.data_manager.lists:
            item = QListWidgetItem(f"● {lst.name}")
            item.setData(Qt.ItemDataRole.UserRole, lst.id)
            item.setForeground(QColor(lst.color))
            self.lists_widget.addItem(item)
        
        # Load clipboard setting
        if self.data_manager.settings.clipboard_enabled:
            self.clipboard_active.setChecked(True)
        else:
            self.clipboard_inactive.setChecked(True)
    
    def add_list(self):
        """Add a new list."""
        # Choose color
        color = QColorDialog.getColor(QColor("#FF5733"), self, "Choisir une couleur")
        if not color.isValid():
            return
        
        # Create list with default name
        list_count = len(self.data_manager.lists) + 1
        name = f"Liste {list_count}"
        
        new_list = self.data_manager.add_list(name, color.name())
        
        # Add to widget
        item = QListWidgetItem(f"● {name}")
        item.setData(Qt.ItemDataRole.UserRole, new_list.id)
        item.setForeground(color)
        self.lists_widget.addItem(item)
    
    def rename_list(self):
        """Rename selected list."""
        current_item = self.lists_widget.currentItem()
        if not current_item:
            return
        
        list_id = current_item.data(Qt.ItemDataRole.UserRole)
        todo_list = self.data_manager.get_list(list_id)
        if not todo_list:
            return

        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "Renommer la liste", "Nouveau nom:", text=todo_list.name)
        
        if ok and new_name.strip():
            todo_list.name = new_name.strip()
            current_item.setText(f"● {todo_list.name}")
            self.data_manager.save()

    def remove_list(self):
        """Remove selected list."""
        current_item = self.lists_widget.currentItem()
        if not current_item:
            return
        
        list_id = current_item.data(Qt.ItemDataRole.UserRole)
        self.data_manager.remove_list(list_id)
        
        self.lists_widget.takeItem(self.lists_widget.row(current_item))
    
    def change_list_color(self):
        """Change color of selected list."""
        current_item = self.lists_widget.currentItem()
        if not current_item:
            return
        
        list_id = current_item.data(Qt.ItemDataRole.UserRole)
        todo_list = self.data_manager.get_list(list_id)
        if not todo_list:
            return
        
        # Choose new color
        current_color = QColor(todo_list.color)
        color = QColorDialog.getColor(current_color, self, "Choisir une couleur")
        if not color.isValid():
            return
        
        # Update list color
        todo_list.color = color.name()
        current_item.setForeground(color)
        self.data_manager.save()
    
    def save_settings(self):
        """Save settings and close."""
        # Update clipboard setting
        if self.clipboard_active.isChecked():
            if not self.data_manager.settings.clipboard_enabled:
                self.data_manager.enable_clipboard()
        else:
            if self.data_manager.settings.clipboard_enabled:
                self.data_manager.disable_clipboard()
        
        self.data_manager.save()
        self.settings_changed.emit()
        self.accept()
