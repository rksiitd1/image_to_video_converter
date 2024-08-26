import sys
import os
import cv2
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, 
                             QLabel, QProgressBar, QLineEdit, QSpinBox, QComboBox, QFrame)
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QLinearGradient
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint
from PyQt5.QtSvg import QSvgRenderer
from pydub import AudioSegment

class CircularProgressBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.value = 0

    def setValue(self, value):
        self.value = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = min(self.width(), self.height())
        rect = QRect(0, 0, width, width)
        rect.moveCenter(self.rect().center())

        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0, QColor(52, 152, 219))
        gradient.setColorAt(1, QColor(41, 128, 185))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(200, 200, 200))
        painter.drawEllipse(rect)

        painter.setBrush(gradient)
        painter.drawPie(rect, int(90 * 16), int(-self.value * 3.6 * 16))

        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, f"{self.value}%")

class VideoCreatorThread(QThread):
    progress_update = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, input_folder, output_name, fps, music_file):
        super().__init__()
        self.input_folder = input_folder
        self.output_name = output_name
        self.fps = fps
        self.music_file = music_file

    def run(self):
        images = [img for img in os.listdir(self.input_folder) if img.endswith((".png", ".jpg", ".jpeg"))]
        images.sort()

        if not images:
            self.finished.emit("No images found in the selected folder.")
            return

        frame = cv2.imread(os.path.join(self.input_folder, images[0]))
        height, width, layers = frame.shape

        output_path = os.path.join(self.input_folder, f'{self.output_name}.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(output_path, fourcc, self.fps, (width, height))

        total_images = len(images)
        for i, image in enumerate(images):
            img_path = os.path.join(self.input_folder, image)
            frame = cv2.imread(img_path)
            video.write(frame)
            self.progress_update.emit(int((i + 1) / total_images * 100))

        video.release()

        if self.music_file:
            temp_output = output_path.replace('.mp4', '_temp.mp4')
            os.rename(output_path, temp_output)
            
            audio = AudioSegment.from_file(self.music_file)
            video_length = total_images / self.fps * 1000  # in milliseconds
            audio = audio[:video_length]  # trim audio to video length
            audio.export("temp_audio.mp3", format="mp3")

            os.system(f'ffmpeg -i {temp_output} -i temp_audio.mp3 -c:v copy -c:a aac {output_path}')
            os.remove(temp_output)
            os.remove("temp_audio.mp3")

        self.finished.emit("Video created successfully!")

class ImageToVideoConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Enhanced Image to Video Converter')
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #3498db;
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
                background-color: #2980b9;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QSpinBox, QComboBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 3px;
                padding: 5px;
            }
        """)

        layout = QVBoxLayout()

        self.folder_label = QLabel('No folder selected', self)
        self.folder_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.folder_label)

        select_button = QPushButton('Select Folder', self)
        select_button.clicked.connect(self.select_folder)
        layout.addWidget(select_button)

        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel('Output Name:'))
        self.output_name = QLineEdit('output', self)
        output_layout.addWidget(self.output_name)
        layout.addLayout(output_layout)

        fps_layout = QHBoxLayout()
        fps_layout.addWidget(QLabel('Images per second:'))
        self.fps_input = QSpinBox(self)
        self.fps_input.setRange(1, 60)
        self.fps_input.setValue(10)
        fps_layout.addWidget(self.fps_input)
        layout.addLayout(fps_layout)

        music_layout = QHBoxLayout()
        music_layout.addWidget(QLabel('Background Music:'))
        self.music_combo = QComboBox(self)
        self.music_combo.addItems(['None', 'Upbeat', 'Relaxing', 'Energetic', 'Custom...'])
        self.music_combo.currentIndexChanged.connect(self.music_selection_changed)
        music_layout.addWidget(self.music_combo)
        layout.addLayout(music_layout)

        self.convert_button = QPushButton('Convert to Video', self)
        self.convert_button.clicked.connect(self.convert_to_video)
        self.convert_button.setEnabled(False)
        layout.addWidget(self.convert_button)

        self.progress_bar = CircularProgressBar(self)
        self.progress_bar.setFixedSize(150, 150)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

        self.status_label = QLabel('', self)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # SVG Background
        self.svg_renderer = QSvgRenderer(self.get_background_svg().encode('utf-8'))
        self.update()

    def get_background_svg(self):
        return '''
        <svg width="500" height="400" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#3498db;stop-opacity:0.2" />
                    <stop offset="100%" style="stop-color:#2c3e50;stop-opacity:0.2" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#grad)"/>
            <circle cx="50" cy="50" r="40" fill="#3498db" fill-opacity="0.1"/>
            <circle cx="450" cy="350" r="60" fill="#2980b9" fill-opacity="0.1"/>
            <path d="M0,400 Q250,300 500,400" stroke="#ecf0f1" stroke-width="2" fill="none" opacity="0.1"/>
        </svg>
        '''

    def paintEvent(self, event):
        painter = QPainter(self)
        self.svg_renderer.render(painter)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_label.setText(f'Selected folder: {folder}')
            self.convert_button.setEnabled(True)
            self.input_folder = folder

    def music_selection_changed(self, index):
        if self.music_combo.currentText() == 'Custom...':
            music_file, _ = QFileDialog.getOpenFileName(self, "Select Music File", "", "Audio Files (*.mp3 *.wav)")
            if music_file:
                self.music_combo.setItemText(index, os.path.basename(music_file))
                self.custom_music_file = music_file
            else:
                self.music_combo.setCurrentIndex(0)

    def convert_to_video(self):
        self.convert_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText('Converting...')

        output_name = self.output_name.text()
        fps = self.fps_input.value()

        music_selection = self.music_combo.currentText()
        music_file = None
        if music_selection == 'Upbeat':
            music_file = 'path/to/upbeat.mp3'
        elif music_selection == 'Relaxing':
            music_file = 'path/to/relaxing.mp3'
        elif music_selection == 'Energetic':
            music_file = 'path/to/energetic.mp3'
        elif music_selection != 'None':
            music_file = self.custom_music_file

        self.thread = VideoCreatorThread(self.input_folder, output_name, fps, music_file)
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