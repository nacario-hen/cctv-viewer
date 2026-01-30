"""
Contains functions related to video streaming, video modifications, image detections
"""

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import utilities as util
import cv2
import time

class VideoThread(QThread):
    # Signal emitted when a new image or a new frame is ready
    change_pixmap_signal = pyqtSignal(np.ndarray, list)

    # Receive RTSP and QLabel it is assigned to
    # main_stream QLabel is assigned to display RTSP at index 1
    def __init__(self, rcvDict = dict):
        super().__init__()
        self.rtsp = rcvDict
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(self.rtsp['rtsp'])
        while self._run_flag and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Emit the frame data as a signal
                self.change_pixmap_signal.emit(frame, self.rtsp['label_id'])
            
            time.sleep(0.03)
        cap.release()
    
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        util.logging.debug(f"Stopping stream {self.rtsp['id']}")
        self._run_flag = False
        self.wait() # Waits for the run() method to actually finish

class StreamMethods():
    # To-do: Apply variable arguments to cater both the mainui implementation and the new ui
    def update_image(self, cv_img, labels):
        """
        Updates the image_label with a new opencv image
        """
        for id in labels:
            label = self.labels[id]
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
        p = convert_to_qt_format.scaled(stream_label.width(), stream_label.height(), Qt.IgnoreAspectRatio)
        return QPixmap.fromImage(p)