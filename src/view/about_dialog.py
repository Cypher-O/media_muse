from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from utils.config import *

class AboutDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(ABOUT)
        self.setGeometry(100, 100, 400, 300)
        layout = QVBoxLayout()
        label = QLabel(ABOUT_VIDEO_PLAYER)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.setLayout(layout)
