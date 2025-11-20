"""
Clipboard manager for DeskFriend.
Monitors system clipboard and adds entries to clipboard list.
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QObject, pyqtSignal


class ClipboardManager(QObject):
    """Manages clipboard monitoring and storage."""
    
    clipboard_changed = pyqtSignal(str)  # New clipboard text
    
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.last_text = ""
        
        # Connect to clipboard
        clipboard = QApplication.clipboard()
        clipboard.dataChanged.connect(self.on_clipboard_changed)
    
    def on_clipboard_changed(self):
        """Handle clipboard change event."""
        if not self.data_manager.settings.clipboard_enabled:
            return
        
        if not self.data_manager.clipboard_list:
            return
        
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        
        # Ignore empty or duplicate text
        if not text or text == self.last_text:
            return
        
        # Ignore if it's just whitespace
        if not text.strip():
            return
        
        self.last_text = text
        
        # Check if item already exists in the list
        for item in self.data_manager.clipboard_list.items:
            if item.text == text:
                return

        # Add to clipboard list
        self.data_manager.clipboard_list.add_item(text)
        self.data_manager.save()
        
        self.clipboard_changed.emit(text)
