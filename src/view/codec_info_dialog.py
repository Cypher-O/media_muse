from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget
from PyQt5.QtCore import Qt

class CodecInfoDialog(QDialog):
    def __init__(self, codec_info, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Codec Information")
        self.setFixedSize(400, 300)  # Set fixed size
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Content widget
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        for info in codec_info:
            label = QLabel(info)
            label.setTextInteractionFlags(Qt.TextSelectableByMouse) 
            content_layout.addWidget(label)
        
        # Add stretch to push content to the top
        content_layout.addStretch()
        
        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to the main layout
        main_layout.addWidget(scroll_area)