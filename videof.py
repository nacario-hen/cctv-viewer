"""
Contains functions related to video streaming, video modifications, image detections
"""

from PyQt5.QtCore import QThread, pyqtSignal, Qt
import numpy as np
import cv2
import time

class VideoThread(QThread):
    # Signal emitted when a new image or a new frame is ready
    change_pixmap_signal = pyqtSignal(np.ndarray, int)

    # Receive RTSP and QLabel it is assigned to
    # main_stream QLabel is assigned to display RTSP at index 1
    def __init__(self, rtsp, stream_label):
        super().__init__()
        self.rtsp = rtsp
        self.label = stream_label
        self._run_flag = True

    def run(self):
        cap = cv2.VideoCapture(self.rtsp)
        while self._run_flag and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                # Emit the frame data as a signal
                self.change_pixmap_signal.emit(frame, self.label)
            
            time.sleep(0.03)
        cap.release()
    
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait() # Waits for the run() method to actually finish