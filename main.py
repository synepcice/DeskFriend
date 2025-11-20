"""
DeskFriend - Desktop Companion List Manager
Main application entry point.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from models import DataManager
from ui.list_window import ListWindow
from ui.settings_window import SettingsWindow
from ui.search_window import SearchWindow
from clipboard_manager import ClipboardManager
from tray_icon import TrayIcon


class DeskFriendApp:
    """Main application class."""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Initialize data manager
        self.data_manager = DataManager()
        self.data_manager.load()
        
        # Initialize components
        self.list_window = None
        self.settings_window = None
        self.search_window = None
        self.clipboard_manager = None
        self.tray_icon = None
        
        self.setup_components()
        
        # Show settings on first launch
        if not self.data_manager.lists:
            self.show_settings()
        else:
            self.show_list_window()
    
    def setup_components(self):
        """Setup all application components."""
        # List window
        self.list_window = ListWindow(self.data_manager)
        self.list_window.settings_requested.connect(self.show_settings)
        self.list_window.search_requested.connect(self.show_search)
        
        # Clipboard manager
        self.clipboard_manager = ClipboardManager(self.data_manager)
        self.clipboard_manager.clipboard_changed.connect(self.on_clipboard_changed)
        
        # Tray icon
        self.tray_icon = TrayIcon()
        self.tray_icon.show_hide_requested.connect(self.toggle_window_visibility)
        self.tray_icon.settings_requested.connect(self.show_settings)
        self.tray_icon.quit_requested.connect(self.quit_app)
        
        # Update tray icon state
        self.tray_icon.set_window_visible(self.data_manager.settings.window_visible)
    
    def show_list_window(self):
        """Show the list window."""
        if self.data_manager.settings.window_visible:
            self.list_window.show()
            self.list_window.raise_()
            self.list_window.activateWindow()
        else:
            self.list_window.hide()
    
    def toggle_window_visibility(self):
        """Toggle list window visibility."""
        if self.list_window.isVisible():
            self.list_window.hide()
            self.data_manager.settings.window_visible = False
            self.tray_icon.set_window_visible(False)
        else:
            self.list_window.show()
            self.list_window.raise_()
            self.list_window.activateWindow()
            self.data_manager.settings.window_visible = True
            self.tray_icon.set_window_visible(True)
        
        self.data_manager.save()
    
    def show_settings(self):
        """Show settings window."""
        if not self.settings_window:
            self.settings_window = SettingsWindow(self.data_manager)
            self.settings_window.settings_changed.connect(self.on_settings_changed)
        
        self.settings_window.load_settings()
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
    
    def show_search(self):
        """Show search window."""
        if not self.search_window:
            self.search_window = SearchWindow(self.data_manager)
            self.search_window.item_selected.connect(self.on_search_result_selected)
        
        self.search_window.show()
        self.search_window.raise_()
        self.search_window.activateWindow()
    
    def on_settings_changed(self):
        """Handle settings changes."""
        # Refresh list window
        self.list_window.refresh_list_selector()
        
        # If current list was deleted, load first available list
        if self.list_window.current_list:
            current_list = self.data_manager.get_list(self.list_window.current_list.id)
            if not current_list:
                all_lists = self.data_manager.get_all_lists()
                if all_lists:
                    self.list_window.set_current_list(all_lists[0])
            else:
                # Refresh style in case color changed
                self.list_window.update_style()
        else:
            # No list selected, try to load one
            all_lists = self.data_manager.get_all_lists()
            if all_lists:
                self.list_window.set_current_list(all_lists[0])
                self.show_list_window()
    
    def on_clipboard_changed(self, text):
        """Handle clipboard change."""
        # Refresh list window if showing clipboard list
        if (self.list_window.current_list and 
            self.list_window.current_list.id == self.data_manager.CLIPBOARD_LIST_ID):
            self.list_window.refresh_items()
    
    def on_search_result_selected(self, list_id, item_id):
        """Handle search result selection."""
        # Switch to the list containing the item
        todo_list = self.data_manager.get_list(list_id)
        if todo_list:
            self.list_window.set_current_list(todo_list)
            self.show_list_window()
    
    def quit_app(self):
        """Quit the application."""
        self.data_manager.save()
        self.app.quit()
    
    def run(self):
        """Run the application."""
        return self.app.exec()


def main():
    """Main entry point."""
    app = DeskFriendApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
