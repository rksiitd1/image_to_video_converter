# Image to Video Converter

## Overview
This application allows users to convert a series of images into a video file, with optional background music. Built using PyQt5 and OpenCV, it provides a user-friendly interface for selecting images, setting video parameters, and monitoring the conversion process.

## Features
- Select a folder containing images.
- Specify the output video name.
- Set frames per second (FPS) for the video.
- Choose background music from predefined options or upload a custom audio file.
- Visual progress indicator during the conversion process.

## Requirements
- Python 3.x
- PyQt5
- OpenCV
- pydub
- ffmpeg (for audio-video merging)

## Installation
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install PyQt5 opencv-python pydub
   ```

3. Ensure `ffmpeg` is installed and accessible in your system's PATH.

## Usage
1. Run the application:
   ```bash
   python image_to_video_converter.py
   ```

2. Click on "Select Folder" to choose the directory containing your images.

3. Enter the desired output name for the video.

4. Set the frames per second (FPS) for the video.

5. Select background music from the dropdown menu or choose a custom file.

6. Click "Convert to Video" to start the conversion process. The progress will be displayed on the circular progress bar.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [OpenCV Documentation](https://opencv.org/)
- [pydub Documentation](https://github.com/jiaaro/pydub)
