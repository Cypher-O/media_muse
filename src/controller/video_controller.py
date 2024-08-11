import os, sys, vlc, ctypes, logging, random, configparser
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QComboBox, QLabel, QSlider, QProgressBar, QPushButton, QVBoxLayout, QHBoxLayout, QAction, QMenuBar
from PyQt5.QtCore import QTimer, QDir, Qt
from view.codec_info_dialog import CodecInfoDialog
from view.preferences_dialog import PreferencesDialog
from utils.config import *

class VideoController:
    def __init__(self, view):
        self.view = view
        self.instance = vlc.Instance(['--no-xlib', '--avcodec-hw=none', '--verbose=2', '--file-logging', '--logfile=vlc-log.txt'])
        self.media_player = self.instance.media_player_new()
        self.playlist = []
        self.playlist_index = 0
        self.repeat = False
        self.shuffle = False
        self.event_manager = self.media_player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.handle_end_of_media)
        self.recent_media_file = RECENT_MEDIA_FILE_NAME
        self.recent_media = self.load_recent_media()
        self.duration_display_mode = 0
        self.preferences = self.load_preferences() 
        
    def open_file(self):
        default_dir = QDir.homePath() 
        videos_dir = os.path.join(default_dir, "Videos")
        filename, _ = QFileDialog.getOpenFileName(self.view, OPEN_VIDEO_FILE, videos_dir)
        if filename:
            self.add_to_recent_media(filename)
            self.playlist = [filename]
            self.playlist_index = 0
            self.play_media()

    def open_multiple_files(self):
        default_dir = QDir.homePath() 
        videos_dir = os.path.join(default_dir, "Videos")
        files, _ = QFileDialog.getOpenFileNames(self.view, OPEN_VIDEO_FILE+"s", videos_dir)
        if files:
            for file in files:
                self.add_to_recent_media(file)
            self.playlist = files
            self.playlist_index = 0
            self.play_media()

    def play_media(self):
        if self.playlist:
            self.current_video_file = self.playlist[self.playlist_index]
            media = self.instance.media_new(self.current_video_file)
            self.media_player.set_media(media)
            if sys.platform == LINUX:
                self.media_player.set_xwindow(int(self.view.video_frame.winId()))
            elif sys.platform == WINDOWS:
                self.media_player.set_hwnd(int(self.view.video_frame.winId()))
            elif sys.platform == MACOS:
                self.media_player.set_nsobject(int(self.view.video_frame.winId()))
            self.media_player.play()
            self.view.update_window_title(self.current_video_file)
            self.view.update_play_button(True) 
            # Set slider maximum to video duration
            while self.media_player.get_state() != vlc.State.Playing:
                continue
            duration = self.media_player.get_length()
            self.view.slider.setMaximum(duration)
            QTimer.singleShot(500, self.update_subtitle_tracks)
        else:
            QMessageBox.information(self.view, INFO, EMPTY_PLAYLIST)
    
    def update_play_button(self, is_playing):
        if is_playing:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            
    def toggle_fullscreen(self):
        self.view.toggle_fullscreen()

    def play_next(self, event=None):
        self.playlist_index += 1
        if self.playlist_index >= len(self.playlist):
            if self.repeat:
                self.playlist_index = 0
            else:
                return
        self.play_media()

    def play_previous(self):
        self.playlist_index -= 1
        if self.playlist_index < 0:
            self.playlist_index = len(self.playlist) - 1 if self.repeat else 0
        self.play_media()

    def play_video(self):
        if self.media_player.is_playing():
            self.media_player.pause()
            self.view.update_play_button(False)
        else:
            self.media_player.play()
            self.view.update_play_button(True)

    def stop_video(self):
        self.media_player.stop()
        self.view.update_play_button(False)

    def toggle_fullscreen(self):
        if self.view.isFullScreen():
            self.view.showNormal()
        else:
            self.view.showFullScreen()
    
    def show_playlist(self):
        self.view.show_playlist(self.playlist)

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self.view.update_repeat_button(self.repeat)

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            random.shuffle(self.playlist)
        else:
            self.playlist.sort()
        self.view.update_shuffle_button(self.shuffle)
    
    def set_position(self, position):
        self.media_player.set_time(position)
    
    def load_recent_media(self):
        config = configparser.ConfigParser()
        if not os.path.exists(self.recent_media_file):
            return []
        config.read(self.recent_media_file)
        if 'Recent' in config:
            return config['Recent'].get('files', '').split('|')
        return []

    def play_media_from_recent(self, filename):
        if not os.path.exists(filename):
            QMessageBox.warning(self.view, FILE_NOT_FOUND, f"The file '{filename}' does not exist.")
            return
        
        self.add_to_recent_media(filename)
        self.playlist = [filename]
        self.playlist_index = 0
        self.play_media()

    def save_recent_media(self):
        config = configparser.ConfigParser()
        config['Recent'] = {'files': '|'.join(self.recent_media)}
        with open(self.recent_media_file, 'w') as configfile:
            config.write(configfile)

    def add_to_recent_media(self, filename):
        if filename in self.recent_media:
            self.recent_media.remove(filename)
        self.recent_media.insert(0, filename)
        if len(self.recent_media) > 10:
            self.recent_media.pop()
        self.save_recent_media()
        self.view.update_recent_media_menu(self.recent_media)
    
    def update_ui(self):
        if self.media_player.is_playing():
            media_pos = self.media_player.get_time()
            self.view.slider.setValue(media_pos)
            
            current_time = media_pos // 1000  # Convert to seconds
            total_time = self.media_player.get_length() // 1000  # Convert to seconds
            
            def format_time(seconds, include_hours=True):
                hours, remainder = divmod(seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                if include_hours or hours > 0:
                    return f"{hours:02}:{minutes:02}:{seconds:02}"
                else:
                    return f"{minutes:02}:{seconds:02}"
            
            if self.duration_display_mode == 0:
                current_time_str = format_time(current_time)
                total_time_str = format_time(total_time)
                duration_text = f"{current_time_str} / {total_time_str}"
            else:
                elapsed_time_str = format_time(current_time, include_hours=False)
                remaining_time = total_time - current_time
                remaining_time_str = format_time(remaining_time)
                duration_text = f"{elapsed_time_str} / -{remaining_time_str}"
            
            self.view.duration_label.setText(duration_text)
        elif self.media_player.get_state() == vlc.State.Ended:
            self.handle_end_of_media()

    def toggle_duration_display(self):
        self.duration_display_mode = 1 - self.duration_display_mode  # Toggle between 0 and 1
        self.update_ui()
    
    def handle_end_of_media(self, event=None):
        # Handle end of media playback
        self.stop_video()
        self.view.reset_video_frame()
        if not self.repeat and self.playlist_index == len(self.playlist) - 1:
            # Only show the message if we reached the end naturally, not on recent media selection
            if self.current_video_file:
                QMessageBox.information(self.view, "End of Playlist", "End of playlist reached.")
        else:
            self.play_next()


    def select_subtitle(self):
        if not self.current_video_file:
            QMessageBox.warning(self.view, "Warning", "Please open a video file first.")
            return
        parent_dir = os.path.dirname(self.current_video_file)
        subtitle_files = [os.path.join(root, file) for root, dirs, files in os.walk(parent_dir) for file in files if file.endswith('.srt')]
        if not subtitle_files:
            QMessageBox.warning(self.view, "Warning", "No subtitle files found in the parent directory.")
            return
        subtitle_file, _ = QFileDialog.getOpenFileName(self.view, "Select Subtitle File", parent_dir, "Subtitle Files (*.srt)")
        if subtitle_file:
            self.media_player.video_set_subtitle_file(subtitle_file)
            self.update_subtitle_tracks()

    def select_subtrack(self, index):
        print(f"select_subtrack called with index: {index}, type: {type(index)}")
        
        if isinstance(index, bool):
            print("Boolean value received, ignoring.")
            return
        
        if index == 0: # This is the "No subtitles" option
            print("Disabling subtitles")
            self.media_player.video_set_spu(-1)
        elif isinstance(index, int) and 0 < index < len(self.subtitle_tracks):
            track_id = self.subtitle_tracks[index]
            print(f"Setting subtitle track to ID: {track_id}")
            self.media_player.video_set_spu(track_id)
        else:
            print(f"Invalid subtitle track index: {index}")
    
    def update_subtitle_tracks(self):
        print("Updating subtitle tracks")
        media = self.media_player.get_media()
        if not media:
            print("No media loaded")
            return
        
        self.view.subtitle_combo.clear()
        self.subtitle_tracks = []

        # Add "No subtitles" option
        self.view.subtitle_combo.addItem("No subtitles")
        self.subtitle_tracks.append(-1)

        # Fetch subtitle tracks
        track_count = self.media_player.video_get_spu_count()
        print(f"Number of subtitle tracks: {track_count}")
        
        # Get all subtitle descriptions at once
        subtitle_descriptions = self.media_player.video_get_spu_description()
        
        if subtitle_descriptions:
            for track_id, desc in subtitle_descriptions:
                self.subtitle_tracks.append(track_id)
                self.view.subtitle_combo.addItem(desc.decode())  # Ensure to decode byte strings to regular strings
                print(f"Added subtitle track: {desc.decode()}")

        print(f"Total subtitle options (including 'No subtitles'): {len(self.subtitle_tracks)}")
        self.view.subtitle_combo.setEnabled(len(self.subtitle_tracks) > 1)
    
    def get_codec_info(self):
        if self.media_player.is_playing() or self.media_player.get_state() == vlc.State.Paused:
            media = self.media_player.get_media()
            media.parse()

            codec_info = []

            # General Media Information
            codec_info.append("General Media Information:")
            codec_info.append(f"  Duration: {media.get_duration()} ms")
            codec_info.append(f"  State: {media.get_state()}")
            codec_info.append(f"  MRL: {media.get_mrl()}")
            codec_info.append(f"  Type: {media.get_type()}")
            codec_info.append(f"  Parsed Status: {media.get_parsed_status()}")
            codec_info.append(f"  Is Parsed: {media.is_parsed()}")

            # Statistics
            codec_info.append("\nStatistics:")
            try:
                stats = vlc.MediaStats()
                media.get_stats(stats)
                for key, value in vars(stats).items():
                    if value is not None and not key.startswith('_'):
                        codec_info.append(f" {key.capitalize()}: {value}")
            except vlc.VlcException as e:
                # Log specific VLC exceptions related to statistics
                logging.error(f"Error retrieving media statistics: {str(e)}")
                codec_info.append("Failed to retrieve statistics.")
            except Exception as e:
                # Log other exceptions
                logging.error(f"Unexpected error: {str(e)}")
                codec_info.append("Error retrieving media statistics.")

            # Tracks Information
            try:
                tracks = media.tracks_get()
                codec_info.append("\nTracks Information:")
                for i, track in enumerate(tracks):
                    codec_info.append(f"Track {i}:")
                    codec_info.append(f"  Type: {track.type}")
                    
                    # Get all available attributes
                    track_info = track.__dict__
                    for key, value in track_info.items():
                        if value is not None and key not in ['_as_parameter_', 'contents']:
                            codec_info.append(f"  {key.capitalize()}: {value}")
                    
                    codec_info.append("")
            except Exception as e:
                codec_info.append(f"Error retrieving track information: {str(e)}")

            # Slaves Information
            codec_info.append("\nSlaves Information:")
            try:
                slave_count = ctypes.c_uint(0)
                slaves = ctypes.POINTER(ctypes.POINTER(vlc.MediaSlave))()
                media.slaves_get(ctypes.byref(slave_count), ctypes.byref(slaves))
                for i in range(slave_count.value):
                    slave = slaves[i].contents
                    codec_info.append(f"Slave {i}:")
                    for key, value in vars(slave).items():
                        if value is not None and not key.startswith('_'):
                            codec_info.append(f"  {key.capitalize()}: {value}")
            except Exception as e:
                codec_info.append(f"Error retrieving slaves information: {str(e)}")

            return codec_info
        else:
            return ["No media playing"]

    def show_codec_info(self):
        codec_info = self.get_codec_info()
        dialog = CodecInfoDialog(codec_info, self.view)
        dialog.exec_()
            
    
    def load_preferences(self):
        # Load preferences from a file or database
        # For now, we'll just return a default dictionary
        return {'default_video_dir': QDir.homePath()}

    def save_preferences(self, new_preferences):
        self.preferences = new_preferences
        # Save preferences to a file or database

    def show_preferences(self):
        dialog = PreferencesDialog(self.view)
        dialog.exec_()

