import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLineEdit, QComboBox, 
                            QProgressBar, QLabel, QFileDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView
import yt_dlp
import darkdetect

# AdSense HTML template
ADSENSE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-YOUR_PUBLISHER_ID"
     crossorigin="anonymous"></script>
    <!-- PiTube Ad Unit -->
    <ins class="adsbygoogle"
         style="display:block"
         data-ad-client="ca-pub-YOUR_PUBLISHER_ID"
         data-ad-slot="YOUR_AD_SLOT_ID"
         data-ad-format="auto"
         data-full-width-responsive="true"></ins>
    <script>
         (adsbygoogle = window.adsbygoogle || []).push({});
    </script>
</head>
<body style="margin: 0; padding: 0;">
</body>
</html>
"""

class DownloaderThread(QThread):
    progress = pyqtSignal(float)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, url, output_path, quality):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%')
            try:
                percentage = float(p.replace('%', ''))
                self.progress.emit(percentage)
            except:
                pass

    def run(self):
        try:
            ydl_opts = {
                'format': 'best' if self.quality == 'Highest' else 'worst',
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.output_path, '%(title)s.%(ext)s')
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PiTube Downloader")
        self.setMinimumSize(600, 400)
        
        # Initialize UI
        self.init_ui()
        
        # Set initial theme based on system
        self.set_theme('dark' if darkdetect.isDark() else 'light')

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("PiTube")
        title.setObjectName("title")
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)

        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL")
        self.url_input.setObjectName("urlInput")
        layout.addWidget(self.url_input)

        # Quality selector
        quality_layout = QHBoxLayout()
        quality_label = QLabel("Quality:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Highest", "Lowest"])
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        layout.addLayout(quality_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("progressBar")
        layout.addWidget(self.progress_bar)

        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setObjectName("downloadBtn")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Theme toggle
        theme_btn = QPushButton("Toggle Theme")
        theme_btn.setObjectName("themeBtn")
        theme_btn.clicked.connect(self.toggle_theme)
        layout.addWidget(theme_btn)

        # AdSense WebView
        self.ad_view = QWebEngineView()
        self.ad_view.setMinimumHeight(90)
        self.ad_view.setHtml(ADSENSE_HTML)
        layout.addWidget(self.ad_view)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

    def set_theme(self, theme):
        self.current_theme = theme
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1a1a1a;
                }
                QLabel {
                    color: #ffffff;
                }
                #title {
                    font-size: 24px;
                    font-weight: bold;
                    color: #ff0000;
                    margin-bottom: 20px;
                }
                QLineEdit {
                    padding: 10px;
                    border: 2px solid #333333;
                    border-radius: 5px;
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
                QPushButton {
                    padding: 10px 20px;
                    border-radius: 5px;
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                #downloadBtn {
                    background-color: #ff0000;
                    font-weight: bold;
                }
                #downloadBtn:hover {
                    background-color: #cc0000;
                }
                QProgressBar {
                    border: 2px solid #333333;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #ff0000;
                }
                QComboBox {
                    padding: 5px;
                    border: 2px solid #333333;
                    border-radius: 5px;
                    background-color: #2a2a2a;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                }
                QLabel {
                    color: #000000;
                }
                #title {
                    font-size: 24px;
                    font-weight: bold;
                    color: #ff0000;
                    margin-bottom: 20px;
                }
                QLineEdit {
                    padding: 10px;
                    border: 2px solid #dddddd;
                    border-radius: 5px;
                    background-color: #ffffff;
                    color: #000000;
                }
                QPushButton {
                    padding: 10px 20px;
                    border-radius: 5px;
                    background-color: #f0f0f0;
                    color: #000000;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                #downloadBtn {
                    background-color: #ff0000;
                    color: #ffffff;
                    font-weight: bold;
                }
                #downloadBtn:hover {
                    background-color: #cc0000;
                }
                QProgressBar {
                    border: 2px solid #dddddd;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #ff0000;
                }
                QComboBox {
                    padding: 5px;
                    border: 2px solid #dddddd;
                    border-radius: 5px;
                    background-color: #ffffff;
                    color: #000000;
                }
            """)

    def toggle_theme(self):
        self.set_theme('light' if self.current_theme == 'dark' else 'dark')

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Please enter a valid URL")
            return

        # Get download location from user
        output_path = QFileDialog.getExistingDirectory(self, "Select Download Location")
        if not output_path:
            return

        self.download_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Downloading...")

        # Create and start download thread
        self.downloader = DownloaderThread(url, output_path, self.quality_combo.currentText())
        self.downloader.progress.connect(self.update_progress)
        self.downloader.finished.connect(self.download_finished)
        self.downloader.error.connect(self.download_error)
        self.downloader.start()

    def update_progress(self, percentage):
        self.progress_bar.setValue(int(percentage))

    def download_finished(self):
        self.download_btn.setEnabled(True)
        self.status_label.setText("Download completed successfully!")
        self.progress_bar.setValue(100)

    def download_error(self, error_msg):
        self.download_btn.setEnabled(True)
        self.status_label.setText(f"Error: {error_msg}")
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
