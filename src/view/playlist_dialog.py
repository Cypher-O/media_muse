from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem
import os
from controller.video_controller import VideoController

class PlaylistDialog(QDialog):
    def __init__(self, parent, playlist):
        super().__init__(parent)
        self.setWindowTitle("Playlist")
        self.setGeometry(100, 100, 300, 400)
        
        self.parent = parent
        self.playlist = playlist
        
        self.layout = QVBoxLayout(self)
        
        self.playlist_widget = QListWidget(self)
        self.update_playlist(playlist)
        self.layout.addWidget(self.playlist_widget)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_media)
        self.button_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Remove")
        self.remove_button.clicked.connect(self.remove_media)
        self.button_layout.addWidget(self.remove_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_playlist)
        self.button_layout.addWidget(self.clear_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        self.button_layout.addWidget(self.close_button)
        
         # Connect the itemClicked signal to the slot method
        self.playlist_widget.itemClicked.connect(self.handle_playlist_item_click)
    
    def update_playlist(self, playlist=None):
        if playlist is not None:
            self.playlist = playlist
        
        self.playlist_widget.clear()
        if not self.playlist:
            self.playlist_widget.addItem("No queue added to the playlist")
        else:
            for file in self.playlist:
                try:
                    if isinstance(file, tuple):
                        # If file is a tuple, assume the first element is the file path
                        file_path = file[0]
                    elif isinstance(file, str):
                        file_path = file
                    else:
                        # If file is neither tuple nor string, use str() representation
                        file_path = str(file)
                    
                    item_name = os.path.basename(file_path)
                    item = QListWidgetItem(item_name)
                    self.playlist_widget.addItem(item)
                except Exception as e:
                    print(f"Error processing playlist item: {file}")
                    print(f"Error details: {str(e)}")
                    # Add the problematic item as is
                    self.playlist_widget.addItem(QListWidgetItem(str(file)))
                    
    def add_media(self):
        initial_count = len(self.playlist)
        self.parent.controller.open_multiple_files()
        new_files = self.parent.controller.playlist[initial_count:]
        
        for file in new_files:
            self.playlist.append(file)
            try:
                item_name = os.path.basename(file) if isinstance(file, str) else str(file)
                list_item = QListWidgetItem(item_name)
                self.playlist_widget.addItem(list_item)
            except Exception as e:
                print(f"Error adding new file to playlist: {file}")
                print(f"Error details: {str(e)}")
                self.playlist_widget.addItem(QListWidgetItem(str(file)))
    
    def remove_media(self):
        selected_items = self.playlist_widget.selectedItems()
        if not selected_items:
            return
        
        # Create a list of items to remove
        items_to_remove = []
        for item in selected_items:
            index = self.playlist_widget.row(item)
            if 0 <= index < len(self.playlist):
                items_to_remove.append((index, item))
        
        # Sort in reverse order to remove from end first
        items_to_remove.sort(key=lambda x: x[0], reverse=True)
        
        # Remove items
        for index, item in items_to_remove:
            del self.playlist[index]
            self.playlist_widget.takeItem(self.playlist_widget.row(item))
        
        self.parent.controller.playlist = self.playlist
        
        # If playlist is empty after removal, add the "No queue" message
        if not self.playlist:
            self.playlist_widget.addItem("No queue added to the playlist")
    
    def clear_playlist(self):
        self.playlist.clear()
        self.playlist_widget.clear()
        self.update_playlist(self.playlist)
        self.playlist_widget.addItem("No queue added to the playlist")
        self.parent.controller.playlist = self.playlist

    # def clear_playlist(self):
    #     self.playlist_widget.clear()
    
    def handle_playlist_item_click(self, item):
        item_text = item.text()
        for i, file in enumerate(self.playlist):
            if os.path.basename(file) == item_text:
                self.parent.controller.playlist_index = i
                self.parent.controller.play_media()
                break