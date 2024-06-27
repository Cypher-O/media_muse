import os
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QStyle, QPushButton, QSlider, QProgressBar, QComboBox, QMessageBox, QHBoxLayout, QAction, QMenuBar, QSizePolicy, QDesktopWidget, QDialog
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QIcon, QCursor
from controller.video_controller import VideoController
from view.about_dialog import AboutDialog
from view.help_dialog import HelpDialog
from view.playlist_dialog import PlaylistDialog
import vlc
from utils.config import *
from datetime import datetime

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(APPLICATION_NAME)
        self.setGeometry(100, 100, 800, 600)

        # Create central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Initialize controller
        self.controller = VideoController(self)
        
        self.media_player = vlc.MediaPlayer()


        # Main layout
        self.layout = QVBoxLayout(self.central_widget)

        # Video frame
        self.video_frame = QLabel()
        self.video_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_frame.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.video_frame)

        # # Controls layout
        # self.controls_layout = QHBoxLayout()
        # self.layout.addLayout(self.controls_layout)
        
        # Create a widget to hold all controls
        self.controls_widget = QWidget(self)
        self.controls_layout = QHBoxLayout(self.controls_widget)

        # Add control buttons with icons
        self.play_button = QPushButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.controller.play_video)
        self.controls_layout.addWidget(self.play_button)

        self.prev_button = QPushButton()
        self.prev_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipBackward))
        self.prev_button.clicked.connect(self.controller.play_previous)
        self.controls_layout.addWidget(self.prev_button)

        self.stop_button = QPushButton()
        self.stop_button.setIcon(self.style().standardIcon(QStyle.SP_MediaStop))
        self.stop_button.clicked.connect(self.controller.stop_video)
        self.controls_layout.addWidget(self.stop_button)

        self.next_button = QPushButton()
        self.next_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSkipForward))
        self.next_button.clicked.connect(self.controller.play_next)
        self.controls_layout.addWidget(self.next_button)

        self.fullscreen_button = QPushButton()
        self.fullscreen_button.setIcon(self.style().standardIcon(QStyle.SP_TitleBarMaxButton))
        self.fullscreen_button.clicked.connect(self.controller.toggle_fullscreen)
        self.controls_layout.addWidget(self.fullscreen_button)

        # Playlist button
        self.playlist_button = QPushButton()
        self.playlist_button.setIcon(QIcon.fromTheme("playlist", QIcon("icons/playlist.png")))
        self.playlist_button.clicked.connect(self.show_playlist)
        self.controls_layout.addWidget(self.playlist_button)

        self.repeat_button = QPushButton()
        self.repeat_button.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
        self.repeat_button.clicked.connect(self.controller.toggle_repeat)
        self.controls_layout.addWidget(self.repeat_button)

        self.shuffle_button = QPushButton()
        self.shuffle_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))
        self.shuffle_button.clicked.connect(self.controller.toggle_shuffle)
        self.controls_layout.addWidget(self.shuffle_button)

        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.slider_moved)
        # self.slider.sliderMoved.connect(self.controller.set_position)
        self.controls_layout.addWidget(self.slider)

        # Volume control
        self.volume_slider = QProgressBar()
        self.volume_slider.setValue(75)
        self.volume_slider.setFixedHeight(18)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setStyleSheet("QProgressBar::chunk { background-color: #0078d7; }")
        self.volume_slider.mousePressEvent = self.volume_mousePressEvent
        self.volume_slider.mouseMoveEvent = self.volume_mouseMoveEvent
        self.volume_slider.mouseReleaseEvent = self.volume_mouseReleaseEvent
        self.controls_layout.addWidget(self.volume_slider)

        # Duration label
        self.duration_label = QLabel(NAN_DURATION)
        self.duration_label.mousePressEvent = self.toggle_duration_display
        self.controls_layout.addWidget(self.duration_label)
        
        # Subtitle ComboBox
        self.subtitle_combo = QComboBox()
        self.subtitle_combo.currentIndexChanged[int].connect(self.controller.select_subtrack)
        self.controls_layout.addWidget(self.subtitle_combo)
        
        # Add the controls widget to the main layout
        self.layout.addWidget(self.controls_widget)
        
        self.center()
        
        # Menu bar
        self.create_menu()
        
        # Recent media
        self.recent_media = self.controller.load_recent_media()
        self.update_recent_media_menu(self.controller.recent_media)        

        # Timer for updating the slider and duration
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.controller.update_ui)
        self.timer.start()
        
         # Current video file and playlist
        self.current_video_file = None
        self.playlist = []
        self.playlist_index = 0
        self.repeat = False
        self.shuffle = False
        
        # # Flags for fullscreen and mouse tracking
        self.fullscreen = False
        # self.mouse_timer = QTimer(self)
        # self.mouse_timer.setSingleShot(True)
        # self.mouse_timer.timeout.connect(self.hide_controls)
        # self.last_mouse_position = QPoint()
        # Timer for hiding controls on mouse inactivity
        self.mouse_timer = QTimer(self)
        self.mouse_timer.setSingleShot(True)
        self.mouse_timer.timeout.connect(self.hide_controls)
        self.last_mouse_position = QPoint()
        self.controls_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        # Attributes for media and recording
        # self.media_player = None
        self.recording = False
        self.recorder = None
        
        # Connect mouseMoveEvent to track mouse movement
        self.setMouseTracking(True)
        

        # Connect to end of media event
        self.event_manager = self.controller.media_player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.controller.handle_end_of_media)
        self.show()

    def create_menu(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu(MEDIA_MENU_BAR)

        open_action = QAction(MEDIA_ACTION_OPEN, self)
        open_action.triggered.connect(self.controller.open_file)
        file_menu.addAction(open_action)

        open_multiple_action = QAction(MEDIA_ACTION_OPEN_MULTIPLE, self)
        open_multiple_action.triggered.connect(self.controller.open_multiple_files)
        file_menu.addAction(open_multiple_action)
        
        # recent_media_action = QAction('Recent Media', self)
        # recent_media_action.triggered.connect(self.show_recent_media)
        # file_menu.addAction(recent_media_action)
        self.recent_media_menu = file_menu.addMenu(RECENT_MEDIA_ACTION)

        exit_action = QAction(MEDIA_EXIT_ACTION, self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        playback_menu = menu_bar.addMenu(PLAYBACK_MENU_BAR)
        
        play_action = QAction(PLAYBACK_PLAY_ACTION, self)
        play_action.triggered.connect(self.controller.play_media)
        playback_menu.addAction(play_action)
        
        stop_action = QAction(PLAYBACK_STOP_ACTION, self)
        stop_action.triggered.connect(self.controller.stop_video)
        playback_menu.addAction(stop_action)
        
        play_previous_action = QAction(PLAYBACK_PREVIOUS_ACTION, self)
        play_previous_action.triggered.connect(self.controller.play_previous)
        playback_menu.addAction(play_previous_action)
        
        next_previous_action = QAction(PLAYBACK_NEXT_ACTION, self)
        next_previous_action.triggered.connect(self.controller.play_next)
        playback_menu.addAction(next_previous_action)

        record_action = QAction(PLAYBACK_RECORD_ACTION, self)
        record_action.triggered.connect(self.record)
        playback_menu.addAction(record_action)
        
        subtitle_menu = menu_bar.addMenu(SUBTITLE_MENU_BAR)
        
        subtitle_action = QAction(SUBTITLE_ADD_ACTION, self)
        subtitle_action.triggered.connect(self.controller.select_subtitle)
        subtitle_menu.addAction(subtitle_action)

        subtitle_track_action = QAction(SUBTITLE_SUB_TRACK_ACTION, self)
        subtitle_track_action.triggered.connect(self.controller.select_subtrack)
        subtitle_menu.addAction(subtitle_track_action)
        
        
        tools_menu = menu_bar.addMenu(TOOLS_MENU_BAR)
        
        codec_info_action = QAction(TOOLS_CODEC_ACTION, self)
        codec_info_action.triggered.connect(self.controller.show_codec_info)
        tools_menu.addAction(codec_info_action)
        
        preferences_action = QAction(TOOLS_PREFERENCES, self)
        preferences_action.triggered.connect(self.controller.show_preferences)
        tools_menu.addAction(preferences_action)

        help_menu = menu_bar.addMenu(HELP)

        help_action = QAction(HELP, self)
        help_action.triggered.connect(self.show_help_dialog)
        help_menu.addAction(help_action)

        about_action = QAction(ABOUT, self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)       
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def update_window_title(self, title):
        self.setWindowTitle(APPLICATION_NAME + f" - {os.path.basename(title)}")

    def set_volume(self, volume):
        self.controller.media_player.audio_set_volume(volume)
        
    def update_play_button(self, is_playing):
        if is_playing:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def update_repeat_button(self, repeat):
        icon = QStyle.SP_BrowserReload if repeat else QStyle.SP_BrowserStop
        self.repeat_button.setIcon(self.style().standardIcon(icon))

    def update_shuffle_button(self, shuffle):
        icon = QStyle.SP_ArrowUp if shuffle else QStyle.SP_ArrowDown
        self.shuffle_button.setIcon(self.style().standardIcon(icon))
        
    def slider_moved(self):
        position = self.slider.value()
        self.controller.set_position(position)

    def volume_mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            value = (pos.x() / self.volume_slider.width()) * self.volume_slider.maximum()
            self.volume_slider.setValue(int(value))
            self.set_volume(int(value))

    def volume_mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            pos = event.pos()
            value = (pos.x() / self.volume_slider.width()) * self.volume_slider.maximum()
            self.volume_slider.setValue(int(value))
            self.set_volume(int(value))

    def volume_mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            value = (pos.x() / self.volume_slider.width()) * self.volume_slider.maximum()
            self.volume_slider.setValue(int(value))
            self.set_volume(int(value))

    def show_help_dialog(self):
        dialog = HelpDialog()
        dialog.exec_()
        
    def show_playlist(self):
        try:
            playlist_dialog = PlaylistDialog(self, self.controller.playlist)
            playlist_dialog.exec_()
        except TypeError as e:
            print(f"Error creating PlaylistDialog: {e}")
            print(f"self: {self}")
            print(f"self.controller: {self.controller}")
            print(f"self.controller.playlist: {self.controller.playlist}")

    def show_about_dialog(self):
        dialog = AboutDialog()
        dialog.exec_()
    
    def update_recent_media_menu(self, recent_media):
        if hasattr(self, 'recent_media_menu'):
            self.recent_media_menu.clear()
            for filepath in recent_media:
                filename = os.path.basename(filepath)
                action = QAction(filename, self)
                action.triggered.connect(lambda _, f=filepath: self.controller.play_media_from_recent(f))
                self.recent_media_menu.addAction(action)
        else:
            print("recent_media_menu not initialized")
    
    def toggle_fullscreen(self):
        if not self.fullscreen:
            self.showFullScreen()
            self.fullscreen = True
            self.controls_widget.hide()
            self.setMouseTracking(True)
        else:
            self.showNormal()
            self.fullscreen = False
            self.controls_widget.show()
            self.setMouseTracking(False)
            
    def mouseDoubleClickEvent(self, event):
        self.controller.toggle_fullscreen()

    def mouseMoveEvent(self, event):
        if self.fullscreen:
            if event.pos() != self.last_mouse_position:
                self.last_mouse_position = event.pos()
                self.show_controls()

    def show_controls(self):
        if not self.fullscreen:
            return
        self.controls_widget.show()
        self.mouse_timer.start(2000)


    def hide_controls(self):
        if self.fullscreen:
            self.controls_widget.hide()
            
    def resizeEvent(self, event):
        if self.fullscreen:
            self.controller.update_video_geometry(self.video_frame.geometry())

    def closeEvent(self, event):
        self.controller.save_recent_media()
         
    def reset_video_frame(self):
        self.video_frame.clear()
        # self.video_frame.setStyleSheet("background-color: black;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.controller.play_video()
        elif event.key() == Qt.Key_Escape and self.fullscreen:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Right:
            self.controller.media_player.set_time(self.media_player.get_time() + 10000)  # 10 seconds forward
        elif event.key() == Qt.Key_Left:
            self.controller.media_player.set_time(self.media_player.get_time() - 10000)  # 10 seconds backward
        elif event.key() == Qt.Key_Up:
            self.controller.media_player.audio_set_volume(self.media_player.audio_get_volume() + 5)  # Volume up
        elif event.key() == Qt.Key_Down:
            self.controller.media_player.audio_set_volume(self.media_player.audio_get_volume() - 5)  # Volume down
        elif event.key() == Qt.Key_F:
            self.controller.toggle_fullscreen()
        elif event.key() == Qt.Key_Q:
            self.controller.close()
        else:
            super().keyPressEvent(event)
            
    def toggle_duration_display(self, event):
        self.controller.toggle_duration_display()
        
    def record(self):
        if not self.media_player or not self.media_player.get_media():
            print("No media loaded or media player not initialized.")
            return

        if not self.recording:
            file_name = self.generate_filename()
            file_path = os.path.join(self.get_recording_directory(), file_name)

            if self.setup_recorder(file_path):
                try:
                    self.recorder.play()
                    self.recording = True
                    self.update_ui_for_recording(True)
                except Exception as e:
                    print(f"Error starting recorder: {str(e)}")
                    self.recording = False
                    self.update_ui_for_recording(False)
        else:
            try:
                self.recorder.stop()
                self.recording = False
                self.update_ui_for_recording(False)
            except Exception as e:
                print(f"Error stopping recorder: {str(e)}")


    def setup_recorder(self, file_path):
        if not self.media_player:
            print("No media player available.")
            return False

        try:
            self.recorder = vlc.MediaRecorder(self.media_player)
            self.recorder.set_output(file_path)
            return True
        except Exception as e:
            print(f"Error setting up recorder: {str(e)}")
            return False
    
    def generate_filename(self):
        current_time = datetime.now().strftime("%Y-%m-%d-%Hh%Mm%Ss")
        media_name = self.media_player.get_media().get_meta(vlc.Meta.Title)
        if not media_name:
            media_name = "Untitled"
        filename = f"video-player-recording-{current_time}-{media_name}.mp4"
        return filename

    def get_recording_directory(self):
        videos_dir = os.path.join(os.getcwd(), "videos")
        recordings_dir = os.path.join(videos_dir, "video-player-recordings")
        if not os.path.exists(recordings_dir):
            os.makedirs(recordings_dir)
        return recordings_dir

    def update_ui_for_recording(self, recording):
        if recording:
            self.record_button.setIcon(QIcon.fromTheme("media-playback-stop"))
            self.record_button.setToolTip("Stop Recording")
        else:
            self.record_button.setIcon(QIcon.fromTheme("media-record"))
            self.record_button.setToolTip("Record")
            
    def closeEvent(self, event):
        if self.recording:
            self.recorder.stop()
        event.accept()
