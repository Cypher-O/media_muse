import sys
from PyQt5.QtWidgets import QApplication
from view.video_player import VideoPlayer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
