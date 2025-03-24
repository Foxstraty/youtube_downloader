import sys
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
from urllib.parse import urlparse, parse_qs


class StyledMessageBox(QDialog):
    """Custom PyQt6 message box with auto-close functionality."""

    def __init__(self, title, message, duration=60000):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(400, 200, 400, 150)
        self.setStyleSheet("background-color: white; color: black; border-radius: 10px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(message, self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(label)

        ok_button = QPushButton("OK", self)
        ok_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setStyleSheet("background-color: #FFA500; color: black; border-radius: 8px; padding: 8px;")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

        QTimer.singleShot(duration, self.accept)


class InputDialog(QDialog):
    """Custom input dialog for getting user input."""

    def __init__(self, title, message, default_text=""):
        super().__init__()
        self.setWindowTitle(title)
        self.setGeometry(400, 200, 400, 150)
        self.setStyleSheet("background-color: white; color: black; border-radius: 10px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(message, self)
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.textbox = QLineEdit(self)
        self.textbox.setText(default_text)
        self.textbox.setFont(QFont("Arial", 11))
        self.textbox.setStyleSheet("border: 2px solid #2A5298; border-radius: 6px; padding: 6px;")
        layout.addWidget(self.textbox)

        ok_button = QPushButton("OK", self)
        ok_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_button.setStyleSheet("background-color: #FFA500; color: black; border-radius: 8px; padding: 8px;")
        ok_button.clicked.connect(self.accept)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)

    def get_input(self):
        return self.textbox.text()


def extract_index_from_url(url):
    """Extract the playlist index (if any) from a YouTube URL."""
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return int(query_params["index"][0]) if "index" in query_params else None


def progress_hook(d):
    """Show download progress in the terminal."""
    if d["status"] == "downloading":
        print(f"Downloading... {d['_percent_str']} ({d['_speed_str']})")


def download_video(video_url, preferred_quality="2160", save_path="."):
    """Download a video or a specific indexed video from a playlist."""
    index = extract_index_from_url(video_url)  # Get index if available
    quality_options = ["2160", "1440", "1080", "720", "480"]

    if preferred_quality not in quality_options:
        QMessageBox.warning(None, "Warning", f"Invalid choice! Defaulting to best available quality.")
        preferred_quality = quality_options[0]

    ydl_opts = {
        "format": f"bestvideo[height<={preferred_quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        "outtmpl": f"{save_path}/%(title)s.%(ext)s",
        "merge_output_format": "mp4",
        "progress_hooks": [progress_hook],
        'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
        "noplaylist": True,  # Default to single video mode
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)

        if "entries" in info and index is not None:
            print(f"\n📂 Playlist detected! Downloading only video at index {index}...")
            if 1 <= index <= len(info["entries"]):
                entry = info["entries"][index - 1]  # Adjust for 0-based indexing
                print(f"\n📥 Downloading: {entry['title']} ({entry['id']})")
                ydl.download([entry["url"]])  # Download only the specific indexed video
            else:
                QMessageBox.critical(None, "Error", f"Index {index} is out of range!")
                return
        else:
            print("\n🎥 Single video detected! Downloading...")
            ydl.download([video_url])

    # Show success message
    success_box = StyledMessageBox("Success", "Download completed!", duration=60000)
    success_box.exec()


def get_video_url():
    """Prompt user for the YouTube video URL."""
    dialog = InputDialog("YouTube Downloader", "Enter the YouTube video URL:")
    if dialog.exec():
        return dialog.get_input()
    sys.exit()


def get_video_quality():
    """Prompt user to select video quality."""
    dialog = InputDialog("Select Quality", "Choose a video quality (2160, 1440, 1080, 720, 480):", "2160")
    if dialog.exec():
        return dialog.get_input()
    return "2160"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    video_url = get_video_url()
    video_quality = get_video_quality()
    download_video(video_url, preferred_quality=video_quality)
