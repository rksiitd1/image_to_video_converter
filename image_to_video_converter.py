import sys
import os
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QProgressBar
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class VideoCreatorThread(QThread):
    progress_update = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, input_folder):
        super().__init__()
        self.input_folder = input_folder

    def run(self):
        images = [img for img in os.listdir(self.input_folder) if img.endswith((".png", ".jpg", ".jpeg"))]
        images.sort()

        if not images:
            self.finished.emit("No images found in the selected folder.")
            return

        frame = cv2.imread(os.path.join(self.input_folder, images[0]))
        height, width, layers = frame.shape

        output_path = os.path.join(self.input_folder, 'output_video.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, 10, (width, height))

        total_images = len(images)
        for i, image in enumerate(images):
            img_path = os.path.join(self.input_folder, image)
            frame = cv2.imread(img_path)
            video.write(frame)
            self.progress_update.emit(int((i + 1) / total_images * 100))

        video.release()
        self.finished.emit("Video created successfully!")

class ImageToVideoConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image to Video Converter')
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                font-family: Arial, sans-serif;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                font-size: 16px;
                margin: 4px 2px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
        """)

        layout = QVBoxLayout()

        self.folder_label = QLabel('No folder selected', self)
        self.folder_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.folder_label)

        select_button = QPushButton('Select Folder', self)
        select_button.clicked.connect(self.select_folder)
        layout.addWidget(select_button)

        self.convert_button = QPushButton('Convert to Video', self)
        self.convert_button.clicked.connect(self.convert_to_video)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('', self)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_label.setText(f'Selected folder: {folder}')
            self.convert_button.setEnabled(True)
            self.input_folder = folder

    def convert_to_video(self):
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText('Converting...')

        self.thread = VideoCreatorThread(self.input_folder)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.finished.connect(self.conversion_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def conversion_finished(self, message):
        self.status_label.setText(message)
        self.convert_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageToVideoConverter()
    ex.show()
    sys.exit(app.exec_())