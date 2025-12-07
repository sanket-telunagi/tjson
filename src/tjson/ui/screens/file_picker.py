from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Button, Static
from textual.containers import Vertical, Horizontal
from textual import on
import os
from pathlib import Path

from tjson.services.config_store import ConfigStore


class FilePickerScreen(ModalScreen[str]):
    """A polished, Dracula-themed file picker dialog."""

    CSS = """
    /* --- OVERLAY --- */
    FilePickerScreen {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }
    
    /* --- MAIN DIALOG BOX --- */
    #picker-dialog {
        width: 80;
        height: 80%;
        background: #282a36;
        
        /* The Main Rounded Frame */
        border: round #bd93f9; 
        
        layout: vertical;
        padding: 0; 
    }
    
    /* --- HEADER (Title) --- */
    #dialog-title {
        width: 100%;
        padding: 1 0;
        text-align: center;
        /* CRITICAL: Centers text vertically and horizontally */
        content-align: center middle; 
        
        /*background: #44475a;*/
        color: #f8f8f2;
        text-style: bold;
        
        /* A subtle line to separate header from tree */
        border-bottom: solid #6272a4; 
    }

    /* --- BODY (The Tree) --- */
    DirectoryTree {
        width: 100%;
        height: 1fr;
        background: #282a36;
        border: none;
        padding: 0 1;
    }

    DirectoryTree > .directory-tree--folder { color: #8be9fd; text-style: bold; }
    DirectoryTree > .directory-tree--file { color: #f8f8f2; }
    DirectoryTree:focus .directory-tree--cursor {
        background: #44475a;
        color: #50fa7b;
        text-style: bold;
    }

    /* --- FOOTER (Action Bar) --- */
    #dialog-footer {
        width: 100%;
        height: 4; /* Taller footer to let buttons float */
        /*background: #44475a;*/
        border-top: solid #6272a4;
        
        /* Centers the button groups vertically in the footer */
        align: center middle; 
        padding: 0 1;
    }

    /* --- BUTTON STYLING (The "Rounded B" Look) --- */
    Button {
        height: 3; /* Standard height */
        min-width: 14;
        
        /* Rounded Corners for the buttons themselves */
        border: round; 
        
        /* Center text inside the button */
        content-align: center middle; 
        
        margin-left: 1;
        margin-right: 1;
        text-style: bold;
    }

    /* --- Navigation Buttons (Left) --- */
    #nav-group {
        width: auto;
        height: auto;
        align: left middle;
    }

    #btn-up {
        background: #282a36; /* Dark inside */
        color: #ffb86c;      /* Orange Text */
        border: round #ffb86c; /* Orange Border */
    }
    #btn-up:hover {
        background: #ffb86c;
        color: #282a36;
    }

    #btn-home {
        background: #282a36;
        color: #8be9fd;      /* Cyan Text */
        border: round #8be9fd; /* Cyan Border */
    }
    #btn-home:hover {
        background: #8be9fd;
        color: #282a36;
    }

    /* --- Action Buttons (Right) --- */
    #action-group {
        width: 1fr;
        height: auto;
        align: right middle;
    }

    #btn-cancel {
        background: #282a36;
        color: #ff5555;      /* Red Text */
        border: round #ff5555; /* Red Border */
    }
    #btn-cancel:hover {
        background: #ff5555;
        color: #f8f8f2;
    }


    ScrollBar {
        background: #282a36;
    }
    ScrollBar > .thumb {
        background: #44475a;
    }
    ScrollBar > .thumb:hover {
        background: #bd93f9;
    }
    """

    def compose(self):
        with Vertical(id="picker-dialog"):
            # 1. Header (Static Title)
            yield Static("📂 Open File", id="dialog-title")

            # 2. Body (Tree)
            yield DirectoryTree("./", id="tree")

            # 3. Footer (Action Bar)
            with Horizontal(id="dialog-footer"):
                # Navigation Group
                with Horizontal(id="nav-group"):
                    yield Button("⬆ Up Level", id="btn-up")
                    yield Button("🏠 Home", id="btn-home")

                # Action Group
                with Horizontal(id="action-group"):
                    yield Button("Cancel", id="btn-cancel")

    def on_mount(self):
        """Runs when the modal opens."""
        tree = self.query_one(DirectoryTree)
        start_path = ConfigStore.get_last_path()
        tree.path = start_path
        self.update_title(start_path)
        tree.focus()

    def update_title(self, path: str):
        self.query_one("#dialog-title").update(f"📂 {path}")

    @on(DirectoryTree.FileSelected)
    def on_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        selected_path = str(event.path)
        ConfigStore.save_last_path(selected_path)
        self.dismiss(selected_path)

    @on(DirectoryTree.DirectorySelected)
    def on_dir_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        self.update_title(str(event.path))

    @on(Button.Pressed, "#btn-up")
    def on_go_up(self) -> None:
        tree = self.query_one(DirectoryTree)
        current_path = Path(tree.path)
        parent_path = str(current_path.parent.resolve())
        tree.path = parent_path
        self.update_title(parent_path)
        tree.focus()

    @on(Button.Pressed, "#btn-home")
    def on_go_home(self) -> None:
        home_path = str(Path.home())
        tree = self.query_one(DirectoryTree)
        tree.path = home_path
        self.update_title(home_path)
        tree.focus()

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)
