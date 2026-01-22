"""
Contains UI related code
"""
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
import utilities as util
import videof
import cv2
import math

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

class UIversion2(QMainWindow, videof.StreamMethods):
    def __init__(self, rtsp_list):
        super(UIversion2, self).__init__()

        self.rtsp_list = rtsp_list
        rtsp_count = len(rtsp_list)
        self.column_count = math.ceil(rtsp_count/3)
        self.move(0, 0)
        self.setWindowIcon(QIcon(util.resource_path('resources/images/eye_icon.png')))
        self.setWindowTitle("Watchmen V2")
        self.initUI()

    def initUI(self):
        # Declare variables
        self.vBoxes = []
        self.labels = []
        self.threads = []
        count = 0
        rtsp_count = 0
        limit = len(self.rtsp_list)

        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        self.setBaseSize(150, 150)
        
        self.hLayout = QHBoxLayout()
        self.gLayout = QGridLayout()
        centralWidget.setLayout(self.hLayout)

        # Create VBoxLayout that houses 3 labels
        while count < self.column_count:
            vBoxLayout = QVBoxLayout()
            self.vBoxes.append(vBoxLayout)
            self.hLayout.addLayout(self.vBoxes[count])

            # Inner loop fills VBoxLayout with 3 labels each
            while rtsp_count < limit:
                label = QLabel()
                label.setFixedSize(360, 240)
                self.labels.append(label)
                vBoxLayout.addWidget(self.labels[rtsp_count])

                thread = videof.VideoThread(self.rtsp_list[rtsp_count], rtsp_count)
                # Connect the signal to the update_image slot
                thread.change_pixmap_signal.connect(self.update_image)
                self.threads.append(thread)
                thread.start()

                rtsp_count += 1
                
                if (rtsp_count % 3) == 0:
                    break
            
            count += 1

        # Refer to the last column/VBoxLayout
        count -= 1

        # Fill last column/VBoxLayout with dummy QLabels
        while (rtsp_count % 3) != 0:
            self.vBoxes[count].addWidget(QLabel("Dummy"))
            rtsp_count += 1

        # Create another column for the main stream
        vBoxLayout = QVBoxLayout()
        label = QLabel()
        label.setFixedSize(720, 720)
        self.labels.append(label)
        vBoxLayout.addWidget(label)

        # Set DEFAULT main stream to display rtsp #1 (rtsp_list[0])
        self.setMainStream(2)

        self.vBoxes.append(vBoxLayout)
        self.hLayout.addLayout(vBoxLayout)

    def setMainStream(self, rtsp_id):
        if len(self.threads) != len(self.rtsp_list):
            self.threads[-1].stop()
        self.main_stream = self.rtsp_list[rtsp_id]
        thread = videof.VideoThread(self.main_stream, -1)
        # Connect the signal to the update_image slot
        thread.change_pixmap_signal.connect(self.update_image)
        self.threads.append(thread)
        thread.start()

    def closeEvent(self, event):
        """Called automatically when the window is closed"""
        for thread in self.threads:
            thread.stop()
        event.accept()