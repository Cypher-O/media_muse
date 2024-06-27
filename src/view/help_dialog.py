from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

class HelpDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Help")
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout(self)
        label = QLabel("This is a video player application. Use the controls below to play, pause, stop, and navigate through your videos. Use the menu to open files and select subtitles.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)
