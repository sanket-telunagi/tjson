from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Label, Button
from textual.containers import Vertical, Horizontal
from textual import on

# import os
from pathlib import Path

from tjson.services.config_store import ConfigStore


class FilePickerScreen(ModalScreen[str]):
    """A visual file picker that remembers where you left off."""

    CSS = """
    FilePickerScreen {
        align: center middle;
        background: rgba(0,0,0,0.7);
    }
    
    #picker-dialog {
        width: 85;
        height: 26;
        background: #282a36;
        border: round #bd93f9;
        padding: 0 1;
        layout: vertical;
    }
    
    /* Title Bar */
    #title {
        width: 100%;
        text-align: center;
        background: #44475a;
        color: #f8f8f2;
        text-style: bold;
        padding: 1;
        margin-bottom: 1;
    }

    /* The Tree View */
    DirectoryTree {
        height: 1fr;
        border: solid #6272a4;
        background: #282a36;
        padding: 0 1;
    }
    
    DirectoryTree > .directory-tree--folder { color: #8be9fd; text-style: bold; }
    DirectoryTree > .directory-tree--file { color: #f8f8f2; }
    DirectoryTree:focus .directory-tree--cursor {
        background: #44475a;
        color: #50fa7b;
        text-style: bold;
    }

    /* Navigation Bar (Bottom) */
    #nav-bar {
        height: 3;
        align: left middle;
        margin-top: 1;
    }

    Button {
        width: auto;
        min-width: 12;
        margin-right: 1; 
        height: 1;
        border: none;
        background: #44475a;
        color: #f8f8f2;
    }

    #btn-up:hover { background: #ffb86c; color: #282a36; } /* Orange */
    #btn-home:hover { background: #8be9fd; color: #282a36; } /* Cyan */
    #btn-cancel { background: #ff5555; color: #282a36; margin-left: 2; } /* Red */
    """

    def compose(self):
        with Vertical(id="picker-dialog"):
            yield Label("Select JSON File", id="title")

            # Initial path will be set in on_mount
            yield DirectoryTree("./", id="tree")

            with Horizontal(id="nav-bar"):
                # Navigation Controls
                yield Button("⬆️ Up Level", id="btn-up")
                yield Button("🏠 Home", id="btn-home")

                # Spacer using standard CSS alignment in parent
                yield Button("Cancel", id="btn-cancel")

    def on_mount(self):
        """Runs when the modal opens."""
        tree = self.query_one(DirectoryTree)

        # 1. Load the last used path from Config
        start_path = ConfigStore.get_last_path()

        # 2. Update the tree
        tree.path = start_path

        # 3. Update Title to show where we are
        self.update_title(start_path)

        # 4. Focus tree for keyboard support
        tree.focus()

    def update_title(self, path: str):
        self.query_one("#title").update(f"📂 {path}")

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        selected_path = str(event.path)

        # SAVE STATE: Remember this folder for next time
        ConfigStore.save_last_path(selected_path)

        self.dismiss(selected_path)

    @on(Button.Pressed, "#btn-up")
    def on_go_up(self) -> None:
        """Navigate to the parent directory."""
        tree = self.query_one(DirectoryTree)
        current_path = Path(tree.path)

        # Go to parent
        parent_path = str(current_path.parent.resolve())

        # Update Tree and Title
        tree.path = parent_path
        self.update_title(parent_path)
        tree.focus()

    @on(Button.Pressed, "#btn-home")
    def on_go_home(self) -> None:
        """Jump to User Home."""
        home_path = str(Path.home())
        tree = self.query_one(DirectoryTree)

        tree.path = home_path
        self.update_title(home_path)
        tree.focus()

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(DirectoryTree.DirectorySelected)
    def on_dir_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Optional: Update title when user dives deeper into folders"""
        self.update_title(str(event.path))
