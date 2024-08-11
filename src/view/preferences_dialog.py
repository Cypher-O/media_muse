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
