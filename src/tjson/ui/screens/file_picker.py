from textual.screen import ModalScreen
from textual.widgets import DirectoryTree, Button, Static
from textual.containers import Vertical, Horizontal
from textual import on
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
        /* Vertical Centering Strategy */
        padding: 1 0;
        text-align: center;
        
        background: #44475a;
        color: #f8f8f2;
        text-style: bold;
        
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
        height: 4; 
        
        border-top: solid #6272a4;
        
        align: center middle; 
        padding: 0 1;
    }

    /* --- BUTTON STYLING (Global for this screen) --- */
    Button {
        height: 3; 
        /*min-width: 14;*/
        
        /* Capsule Look */
        border: round; 
        
        content-align: center middle; 
        margin-left: 1;
        margin-right: 1;
        text-style: bold;
    }

    /* --- Navigation Group (Left) --- */
    #nav-group {
        width: auto;
        height: 100%;
        align: left middle;
    }

    /* Up Level: Orange Theme */
    #btn-up {
        background: #282a36; 
        color: #ffb86c;      
        border: round #ffb86c; 
    }
    #btn-up:hover {
        background: #ffb86c;
        color: #282a36;
        border: round #ffb86c;
    }

    /* Home: Cyan Theme */
    #btn-home {
        background: #282a36;
        color: #8be9fd;      
        border: round #8be9fd; 
    }
    #btn-home:hover {
        background: #8be9fd;
        color: #282a36;
    }

    /* --- Action Group (Right) --- */
    #action-group {
        width: 1fr;
        height: 100%;
        align: right middle;
    }

    /* Cancel: Red Theme (UPDATED) */
    #btn-cancel {
        background: #282a36;   /* Dark Inside */
        color: #ff5555;        /* Red Text */
        border: round #ff5555; /* Red Border */
    }
    #btn-cancel:hover {
        background: #ff5555;   /* Fill Red */
        color: #282a36;        /* Dark Text for Contrast */
    }

    /* --- SCROLLBARS --- */
    ScrollBar { background: #282a36; }
    ScrollBar > .thumb { background: #44475a; }
    ScrollBar > .thumb:hover { background: #bd93f9; }
    """

    def compose(self):
        with Vertical(id="picker-dialog"):
            # Header
            yield Static("📂 Open File", id="dialog-title")

            # Body
            yield DirectoryTree("./", id="tree")

            # Footer
            with Horizontal(id="dialog-footer"):
                with Horizontal(id="nav-group"):
                    yield Button("⬆ Up Level", id="btn-up")
                    yield Button("🏠 Home", id="btn-home")
                    yield Button("Cancel", id="btn-cancel")

                # with Horizontal(id="action-group"):

    def on_mount(self):
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
