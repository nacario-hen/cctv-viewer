"""
Contains UI related code
"""

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.uic import loadUi
import utilities as util
import videof
import cv2

class MainUI(QMainWindow, videof.StreamMethods):
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
    
    def closeEvent(self, event):
        """Called automatically when the window is closed"""
        for thread in self.threads:
            thread.stop()
        event.accept()

