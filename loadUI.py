"""
Contains UI related code
"""

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
import utilities as util
import videof
import cv2

class MainUI(QMainWindow):
    def __init__(self, rtsp_list):
        super(MainUI, self).__init__()

        # Load the UI created from designer
        loadUi(util.resource_path("resources/ui/mainui.ui"), self)
        
        self.setWindowIcon(QIcon(util.resource_path('resources/images/eye_icon.png')))
        self.setWindowTitle("Watchmen")

        self.labels = [self.main_stream, self.stream_2, self.stream_3]
        self.threads = []

        for i, rtsp in enumerate(rtsp_list):
            # Create and start the video capture thread
            thread = videof.VideoThread(rtsp, i)
            # Connect the signal to the update_image slot
            thread.change_pixmap_signal.connect(self.update_image)
            self.threads.append(thread)
            thread.start()

    def update_image(self, cv_img, stream_label):
        """Updates the image_label with a new opencv image"""
        label = self.labels[stream_label]
        qt_img = self.convert_cv_qt(cv_img, label)
        label.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img, stream_label):
        # Convert image from BGR (cv2 default color format) to RGB (Qt default color format)
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        # Convert numpy array to QImage
        convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        # Scale the image for display
        p = convert_to_qt_format.scaled(stream_label.width(), stream_label.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    def closeEvent(self, event):
        """Called automatically when the window is closed"""
        for thread in self.threads:
            thread.stop()
        event.accept()

