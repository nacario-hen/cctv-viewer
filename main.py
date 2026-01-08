from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.uic import loadUi
import cv2
import numpy as np
import os
import sys
import time

def load_stream():
    """
    Checks and loads all streams existing in accounts.txt
    """
    if not os.path.exists('accounts.txt'):
        print("accounts.txt doesn't exist. Exiting application")
        exit()

    # rstrip removes \n from the read lines
    with open('accounts.txt', 'r') as file:
        rtsp_list = [line.rstrip() for line in file.readlines()]
        file.close()

    # reversed(list(enumerate(rtsp_list))) creates reversed index and object
    # instead of checking 0, rtsp 1 at the first iteration, start at the end instead
    for i, stream in reversed(list(enumerate(rtsp_list))):
        cap = cv2.VideoCapture(stream)
        if not cap.isOpened():
            print(f"Error: Cannot open the RTSP stream {stream}")
            rtsp_list.pop(i)
        else:
            print(f"RTSP stream {i} opened successfully")
            cap.release()

    # Check if list is empty. Empty = False. Not False = True
    if not rtsp_list:
        print("No active CCTV to stream")
        exit()

    return rtsp_list

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

class MainUI(QMainWindow):
    def __init__(self, rtsp_list):
        super(MainUI, self).__init__()

        # Load the UI created from designer
        loadUi("mainui.ui", self)

        self.labels = [self.main_stream, self.stream_2, self.stream_3]
        self.threads = []

        for i, rtsp in enumerate(rtsp_list):
            # Create and start the video capture thread
            thread = VideoThread(rtsp, i)
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

if __name__ == "__main__":
    rtsp_list = load_stream()
    app = QApplication(sys.argv)
    ui = MainUI(rtsp_list)
    ui.show()
    app.exec_()