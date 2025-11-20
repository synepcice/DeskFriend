"""
Data models for DeskFriend application.
Handles list items, todo lists, settings, and data persistence.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any


class ListItem:
    """Represents a single item in a todo list."""
    
    def __init__(
        self,
        text: str,
        item_id: Optional[str] = None,
        created_at: Optional[str] = None,
        modified_at: Optional[str] = None,
        validated_at: Optional[str] = None,
        is_validated: bool = False
    ):
        self.id = item_id or str(uuid.uuid4())
        self.text = text
        self.created_at = created_at or datetime.now().isoformat()
        self.modified_at = modified_at or self.created_at
        self.validated_at = validated_at
        self.is_validated = is_validated
    
    def validate(self):
        """Mark item as validated."""
        self.is_validated = True
        self.validated_at = datetime.now().isoformat()
    
    def unvalidate(self):
        """Mark item as not validated."""
        self.is_validated = False
        self.validated_at = None
    
    def update_text(self, new_text: str):
        """Update item text and modification timestamp."""
        self.text = new_text
        self.modified_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at,
            "modified_at": self.modified_at,
            "validated_at": self.validated_at,
            "is_validated": self.is_validated
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListItem':
        """Create ListItem from dictionary."""
        return cls(
            text=data["text"],
            item_id=data.get("id"),
            created_at=data.get("created_at"),
            modified_at=data.get("modified_at"),
            validated_at=data.get("validated_at"),
            is_validated=data.get("is_validated", False)
        )


class TodoList:
    """Represents a todo list with items."""
    
    def __init__(
        self,
        name: str,
        color: str,
        list_id: Optional[str] = None,
        items: Optional[List[ListItem]] = None
    ):
        self.id = list_id or str(uuid.uuid4())
        self.name = name
        self.color = color
        self.items = items or []
    
    def add_item(self, text: str) -> ListItem:
        """Add a new item to the list."""
        item = ListItem(text)
        self.items.append(item)
        return item
    
    def remove_item(self, item_id: str):
        """Remove an item by ID."""
        self.items = [item for item in self.items if item.id != item_id]
    
    def get_item(self, item_id: str) -> Optional[ListItem]:
        """Get an item by ID."""
        for item in self.items:
            if item.id == item_id:
                return item
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "items": [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TodoList':
        """Create TodoList from dictionary."""
        items = [ListItem.from_dict(item_data) for item_data in data.get("items", [])]
        return cls(
            name=data["name"],
            color=data["color"],
            list_id=data.get("id"),
            items=items
        )


class AppSettings:
    """Application settings."""
    
    def __init__(
        self,
        clipboard_enabled: bool = False,
        window_position: Optional[tuple] = None,
        last_list_id: Optional[str] = None,
        window_visible: bool = True
    ):
        self.clipboard_enabled = clipboard_enabled
        self.window_position = window_position or (100, 100)
        self.last_list_id = last_list_id
        self.window_visible = window_visible
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "clipboard_enabled": self.clipboard_enabled,
            "window_position": list(self.window_position),
            "last_list_id": self.last_list_id,
            "window_visible": self.window_visible
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppSettings':
        """Create AppSettings from dictionary."""
        return cls(
            clipboard_enabled=data.get("clipboard_enabled", False),
            window_position=tuple(data.get("window_position", [100, 100])),
            last_list_id=data.get("last_list_id"),
            window_visible=data.get("window_visible", True)
        )


class DataManager:
    """Manages data persistence for the application."""
    
    CLIPBOARD_LIST_ID = "clipboard_list"
    
    def __init__(self, data_file: str = "data.json"):
        self.data_file = Path(data_file)
        self.settings = AppSettings()
        self.lists: List[TodoList] = []
        self.clipboard_list: Optional[TodoList] = None
    
    def load(self):
        """Load data from JSON file."""
        if not self.data_file.exists():
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load settings
            self.settings = AppSettings.from_dict(data.get("settings", {}))
            
            # Load regular lists
            self.lists = []
            for list_data in data.get("lists", []):
                if list_data["id"] != self.CLIPBOARD_LIST_ID:
                    self.lists.append(TodoList.from_dict(list_data))
            
            # Load clipboard list if enabled
            if self.settings.clipboard_enabled:
                clipboard_data = next(
                    (l for l in data.get("lists", []) if l["id"] == self.CLIPBOARD_LIST_ID),
                    None
                )
                if clipboard_data:
                    self.clipboard_list = TodoList.from_dict(clipboard_data)
                else:
                    self.clipboard_list = TodoList(
                        name="ClipBoard",
                        color="#808080",
                        list_id=self.CLIPBOARD_LIST_ID
                    )
        
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def save(self):
        """Save data to JSON file."""
        try:
            all_lists = self.lists.copy()
            if self.clipboard_list and self.settings.clipboard_enabled:
                all_lists.append(self.clipboard_list)
            
            data = {
                "settings": self.settings.to_dict(),
                "lists": [lst.to_dict() for lst in all_lists]
            }
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_list(self, name: str, color: str) -> TodoList:
        """Add a new list."""
        new_list = TodoList(name, color)
        self.lists.append(new_list)
        self.save()
        return new_list
    
    def remove_list(self, list_id: str):
        """Remove a list by ID."""
        self.lists = [lst for lst in self.lists if lst.id != list_id]
        self.save()
    
    def get_list(self, list_id: str) -> Optional[TodoList]:
        """Get a list by ID."""
        if list_id == self.CLIPBOARD_LIST_ID:
            return self.clipboard_list
        
        for lst in self.lists:
            if lst.id == list_id:
                return lst
        return None
    
    def get_all_lists(self) -> List[TodoList]:
        """Get all lists including clipboard if enabled."""
        all_lists = self.lists.copy()
        if self.clipboard_list and self.settings.clipboard_enabled:
            all_lists.append(self.clipboard_list)
        return all_lists
    
    def enable_clipboard(self):
        """Enable clipboard list."""
        self.settings.clipboard_enabled = True
        if not self.clipboard_list:
            self.clipboard_list = TodoList(
                name="ClipBoard",
                color="#808080",
                list_id=self.CLIPBOARD_LIST_ID
            )
        self.save()
    
    def disable_clipboard(self):
        """Disable clipboard list."""
        self.settings.clipboard_enabled = False
        self.save()
