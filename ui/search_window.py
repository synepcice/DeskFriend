"""
Search window for DeskFriend.
Search across all lists and timestamps.
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QListWidget, QListWidgetItem, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from pathlib import Path
from datetime import datetime


class SearchWindow(QDialog):
    """Search window for finding items across all lists."""
    
    item_selected = pyqtSignal(str, str)  # list_id, item_id
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components."""
        self.setWindowTitle("Recherche - DeskFriend")
        self.setModal(False)
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Search input
        search_layout = QHBoxLayout()
        
        icons_path = Path(__file__).parent.parent / "Icons"
        
        search_label = QLabel()
        search_label.setPixmap(QIcon(str(icons_path / "Search.png")).pixmap(24, 24))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher dans les listes...")
        self.search_input.textChanged.connect(self.perform_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_result_selected)
        self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.results_list)
        
        # Dark theme style
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(50, 50, 50, 0.95);
            }
            QLabel {
                color: white;
            }
            QLineEdit {
                padding: 8px;
                background-color: rgba(70, 70, 70, 0.9);
                color: white;
                border: 2px solid rgba(100, 100, 100, 0.8);
                border-radius: 4px;
                font-size: 14px;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.5);
            }
            QListWidget {
                background-color: rgba(40, 40, 40, 0.9);
                color: white;
                border: 1px solid rgba(0, 0, 0, 0.6);
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:hover {
                background-color: rgba(80, 80, 80, 0.6);
            }
            QListWidget::item:selected {
                background-color: rgba(100, 100, 100, 0.8);
                color: white;
            }
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
    
    def perform_search(self, query):
        """Perform search across all lists."""
        self.results_list.clear()
        
        if not query.strip():
            return
        
        query_lower = query.lower()
        
        # Search in all lists
        for todo_list in self.data_manager.get_all_lists():
            for item in todo_list.items:
                # Search in text
                if query_lower in item.text.lower():
                    self.add_result(todo_list, item, "Texte")
                    continue
                
                # Search in timestamps
                if self.search_in_timestamp(query_lower, item.created_at):
                    self.add_result(todo_list, item, "Date de création")
                    continue
                
                if item.modified_at != item.created_at:
                    if self.search_in_timestamp(query_lower, item.modified_at):
                        self.add_result(todo_list, item, "Date de modification")
                        continue
                
                if item.validated_at:
                    if self.search_in_timestamp(query_lower, item.validated_at):
                        self.add_result(todo_list, item, "Date de validation")
                        continue
    
    def search_in_timestamp(self, query, timestamp_str):
        """Check if query matches timestamp."""
        try:
            dt = datetime.fromisoformat(timestamp_str)
            formatted = dt.strftime('%d/%m/%Y %H:%M:%S')
            return query in formatted.lower()
        except:
            return False
    
    def add_result(self, todo_list, item, match_type):
        """Add a search result to the list."""
        # Truncate text if too long
        text = item.text
        if len(text) > 60:
            text = text[:57] + "..."
        
        result_text = f"[{todo_list.name}] {text}\n({match_type})"
        
        result_item = QListWidgetItem(result_text)
        result_item.setData(Qt.ItemDataRole.UserRole, (todo_list.id, item.id))
        
        self.results_list.addItem(result_item)
    
    def on_result_selected(self, item):
        """Handle result selection."""
        list_id, item_id = item.data(Qt.ItemDataRole.UserRole)
        self.item_selected.emit(list_id, item_id)
        self.close()
    
    def show_context_menu(self, pos):
        """Show context menu for search results."""
        item = self.results_list.itemAt(pos)
        if not item:
            return
        
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        copy_action = QAction("Copier vers le Presse-Papier", self)
        copy_action.triggered.connect(lambda: self.copy_to_clipboard(item))
        menu.addAction(copy_action)
        
        menu.exec(self.results_list.mapToGlobal(pos))
        
    def copy_to_clipboard(self, item):
        """Copy selected item text to clipboard."""
        list_id, item_id = item.data(Qt.ItemDataRole.UserRole)
        todo_list = self.data_manager.get_list(list_id)
        if not todo_list:
            return
            
        # Find item
        found_item = next((i for i in todo_list.items if i.id == item_id), None)
        if found_item:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(found_item.text)

    def showEvent(self, event):
        """Focus search input when window is shown."""
        super().showEvent(event)
        self.search_input.setFocus()
        self.search_input.selectAll()
