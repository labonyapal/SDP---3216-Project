from abc import ABC, abstractmethod
from typing import List, Optional, Any
import uuid

# Composite Design Pattern:
# MaterialComponent acts as the Component participant in the Composite pattern,
# defining the common interface for both leaf nodes (files) and composite nodes (folders).
class MaterialComponent(ABC):
    """
    Abstract base class for all nodes in the composite study materials tree.
    Defines the interface for get_size(), render(depth), and get_path().
    """

    def __init__(self, component_id: str, name: str, parent_id: Optional[str] = None):
        self.id = component_id
        self.name = name
        self.parent_id = parent_id
        self.parent: Optional[MaterialComponent] = None

    @abstractmethod
    def get_size(self) -> int:
        """Return the size of this component in bytes."""
        pass

    @abstractmethod
    def render(self, depth: int = 0) -> dict:
        """Render the component and its children (if any) as a nested JSON/dictionary structure."""
        pass

    @abstractmethod
    def get_path(self) -> str:
        """Get the logical file-system path to this component."""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Backward compatibility: converts the component to a dict representation."""
        return self.render(depth=0)

    def get_details(self) -> dict[str, Any]:
        """Backward compatibility: returns the detail dictionary."""
        return self.render(depth=0)


class MaterialFile(MaterialComponent):
    """
    Leaf component representing a single study file in the materials structure.
    Does not contain any children.
    """

    def __init__(self, component_id: str, name: str, size: int, file_url: str, parent_id: Optional[str] = None):
        super().__init__(component_id, name, parent_id)
        self.size = size
        self.file_url = file_url

    def get_size(self) -> int:
        return self.size

    def render(self, depth: int = 0) -> dict:
        return {
            "id": self.id,
            "type": "file",
            "name": self.name,
            "size": self.get_size(),
            "file_url": self.file_url,
            "download_url": self.file_url,
            "path": self.get_path(),
            "depth": depth
        }

    def get_path(self) -> str:
        if self.parent:
            return f"{self.parent.get_path()}/{self.name}"
        return f"/Materials/{self.name}"


class MaterialFolder(MaterialComponent):
    """
    Composite component representing a folder which can contain subfolders and files.
    """

    def __init__(self, component_id: str, name: str, parent_id: Optional[str] = None):
        super().__init__(component_id, name, parent_id)
        self.children: List[MaterialComponent] = []

    def add(self, component: MaterialComponent) -> None:
        """Add a child component to the folder and set its parent pointer."""
        component.parent = self
        self.children.append(component)

    def remove(self, component: MaterialComponent) -> None:
        """Remove a child component from the folder and clear its parent pointer."""
        if component in self.children:
            self.children.remove(component)
            component.parent = None

    def get_child(self, name: str) -> Optional[MaterialComponent]:
        """Retrieve a direct child component by its name."""
        for child in self.children:
            if child.name == name:
                return child
        return None

    def get_size(self) -> int:
        """Recursively calculate the total size of all files in this folder and subfolders."""
        return sum(child.get_size() for child in self.children)

    def render(self, depth: int = 0) -> dict:
        return {
            "id": self.id,
            "type": "folder",
            "name": self.name,
            "total_size": self.get_size(),
            "children": [child.render(depth + 1) for child in self.children],
            "path": self.get_path(),
            "depth": depth
        }

    def get_path(self) -> str:
        if self.parent:
            return f"{self.parent.get_path()}/{self.name}"
        return f"/Materials/{self.name}" if self.name != "Materials" else "/Materials"


# Legacy class mappings to maintain complete backward compatibility with existing tests and codebase imports
class Folder(MaterialFolder):
    """Backward-compatible wrapper for MaterialFolder."""
    def __init__(self, name: str, component_id: Optional[str] = None):
        super().__init__(component_id or str(uuid.uuid4()), name)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Folder":
        folder = cls(data.get("name", "root"), component_id=data.get("id"))
        for child_data in data.get("children", []):
            if child_data.get("type") == "folder":
                folder.add(cls.from_dict(child_data))
            else:
                folder.add(
                    StudyFile(
                        name=child_data.get("name", "untitled"),
                        size=child_data.get("size", 0),
                        file_url=child_data.get("file_url", ""),
                        component_id=child_data.get("id"),
                    )
                )
        return folder


class StudyFile(MaterialFile):
    """Backward-compatible wrapper for MaterialFile."""
    def __init__(self, name: str, size: int, file_url: str, component_id: Optional[str] = None):
        super().__init__(component_id or str(uuid.uuid4()), name, size, file_url)


# Alias for backward compatibility with existing imports
FileSystemComponent = MaterialComponent



# Composite Helper function to convert flat DB rows into the composite object tree
def build_tree(rows: List[dict], parent_id: Optional[str] = None) -> MaterialFolder:
    """
    Recursively builds a MaterialFolder (Composite) tree from flat database rows.
    """
    def build_node(node_id: Optional[str], node_name: str) -> MaterialFolder:
        folder = MaterialFolder(component_id=node_id or "root", name=node_name)
        
        # If node_id is root or None, match rows with parent_id as None, "", or "root"
        if node_id is None or node_id == "root":
            children_rows = [row for row in rows if row.get("parent_id") in (None, "", "root")]
        else:
            children_rows = [row for row in rows if row.get("parent_id") == node_id]
            
        for row in children_rows:
            if row.get("type") == "folder":
                child_folder = build_node(row.get("id"), row.get("name", "Untitled Folder"))
                folder.add(child_folder)
            else:
                child_file = MaterialFile(
                    component_id=row.get("id"),
                    name=row.get("name") or row.get("title") or "Untitled File",
                    size=row.get("size") or 0,
                    file_url=row.get("file_url") or "",
                    parent_id=row.get("parent_id")
                )
                folder.add(child_file)
        return folder

    # Build starting from root Materials folder
    return build_node(parent_id, "Materials")
