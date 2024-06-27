# from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog

# class PreferencesDialog(QDialog):
#     def __init__(self, parent, current_preferences):
#         super().__init__(parent)
#         self.setWindowTitle("Preferences")
#         self.current_preferences = current_preferences
#         self.layout = QVBoxLayout()

#         # Default video directory
#         self.video_dir_layout = QHBoxLayout()
#         self.video_dir_label = QLabel("Default Video Directory:")
#         self.video_dir_edit = QLineEdit(self.current_preferences.get('default_video_dir', ''))
#         self.video_dir_button = QPushButton("Browse")
#         self.video_dir_button.clicked.connect(self.browse_video_dir)
#         self.video_dir_layout.addWidget(self.video_dir_label)
#         self.video_dir_layout.addWidget(self.video_dir_edit)
#         self.video_dir_layout.addWidget(self.video_dir_button)
#         self.layout.addLayout(self.video_dir_layout)

#         # Add more preference options here

#         # Save button
#         self.save_button = QPushButton("Save")
#         self.save_button.clicked.connect(self.save_preferences)
#         self.layout.addWidget(self.save_button)

#         self.setLayout(self.layout)

#     def browse_video_dir(self):
#         dir_name = QFileDialog.getExistingDirectory(self, "Select Default Video Directory")
#         if dir_name:
#             self.video_dir_edit.setText(dir_name)

#     def save_preferences(self):
#         self.current_preferences['default_video_dir'] = self.video_dir_edit.text()
#         # Save more preferences here
#         self.accept()

# preferences_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QPushButton

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()

        self.auto_play_checkbox = QCheckBox("Auto Play")
        self.auto_play_checkbox.setChecked(True)  # Example preference
        layout.addWidget(self.auto_play_checkbox)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_preferences)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_preferences(self):
        # Logic to save preferences goes here
        self.accept()
