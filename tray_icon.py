"""
System tray icon for DeskFriend.
Provides menu for showing/hiding lists, settings, and quitting.
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path


class TrayIcon(QObject):
    """System tray icon with menu."""
    
    show_hide_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_tray()
    
    def setup_tray(self):
        """Setup the system tray icon and menu."""
        # Create tray icon
        icons_path = Path(__file__).parent / "Icons"
        
        # Use Develop.png as the tray icon
        icon_path = icons_path / "Develop.png"
        self.tray_icon = QSystemTrayIcon(QIcon(str(icon_path)))
        
        # Create menu
        menu = QMenu()
        
        # Show/Hide action
        self.show_hide_action = QAction("✓ Afficher les Listes", menu)
        self.show_hide_action.setCheckable(True)
        self.show_hide_action.setChecked(True)
        self.show_hide_action.triggered.connect(self.on_show_hide)
        menu.addAction(self.show_hide_action)
        
        menu.addSeparator()
        
        # Settings action
        settings_icon = QIcon(str(icons_path / "Params.png"))
        settings_action = QAction(settings_icon, "Paramètres", menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_icon = QIcon(str(icons_path / "Exit.png"))
        quit_action = QAction(quit_icon, "Quitter", menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)
        
        # Set menu and show tray icon
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.setToolTip("DeskFriend")
        self.tray_icon.show()
    
    def on_show_hide(self):
        """Handle show/hide toggle."""
        self.show_hide_requested.emit()
    
    def set_window_visible(self, visible):
        """Update the checkmark based on window visibility."""
        self.show_hide_action.setChecked(visible)
        if visible:
            self.show_hide_action.setText("✓ Afficher les Listes")
        else:
            self.show_hide_action.setText("  Afficher les Listes")
