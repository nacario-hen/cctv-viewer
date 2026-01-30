"""
Contains UI related code
"""
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QWidget
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.uic import loadUi
import utilities as util
import videof
import cv2
import math

class ClickableVideoLabel(QLabel):
    # Create a custom signal that we can connect to a function
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def mousePressEvent(self, event):
        # This function runs automatically when the label is clicked
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
    
    # To-do: Modify cursor on mouse hover over labels

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
            tmp = {'id': i, 'rtsp' : rtsp, 'label_id' : [i]}
            thread = videof.VideoThread(tmp)
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
        
        self.rtsp_list = []
        for i, item in enumerate(rtsp_list):
            tmp_dict =  {
                        'id' : i,
                        'rtsp' : item,
                        'label_id' : [i]
                        }
            self.rtsp_list.append(tmp_dict)

        rtsp_count = len(rtsp_list)
        self.column_count = math.ceil(rtsp_count/3)
        self.move(0, 0)
        self.setWindowIcon(QIcon(util.resource_path('resources/images/eye_icon.png')))
        self.setWindowTitle("Watchmen V2")
        self.initUI()

    def initUI(self):
        """
            Initialize UI
        """
        # Variable declaration
        self.labels = []
        self.threads = []
        self.current_main = None
        iter_column = 0
        iter_rtsp = 0
        vBox = None
        limit = len(self.rtsp_list)
        
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        
        self.hLayout = QHBoxLayout()
        self.hLayout.setSpacing(2)
        centralWidget.setLayout(self.hLayout)

        # Create VBoxLayout that houses 3 labels 
        while iter_column < self.column_count:
            vBox = QVBoxLayout()
            self.hLayout.addLayout(vBox)

            # Inner loop fills VBoxLayout with 3 labels each
            while iter_rtsp < limit:
                # Create a clickable label per RTSP stream in the RTSP List
                label = ClickableVideoLabel()
                label.setFixedSize(360, 240)
                self.labels.append(label)
                # lambda val = iter_rtsp prevents the problem where the value passed to setMainStream
                # is the final value of iter_rtsp
                self.labels[iter_rtsp].clicked.connect(lambda val = iter_rtsp: self.setMainStream(val))
                vBox.addWidget(self.labels[iter_rtsp])
                
                # Create the VideoThread where the streaming is handled
                thread = videof.VideoThread(self.rtsp_list[iter_rtsp])
                # Connect the signal to the update_image slot
                # Emitted values from the thread are caught by update_image function
                thread.change_pixmap_signal.connect(self.update_image)
                self.threads.append(thread)
                thread.start()

                iter_rtsp += 1
                # Check if 3 labes are already added in this vBox
                # iter_rtsp += 1, if divisible by 3, will be processed in the next loop
                if (iter_rtsp % 3) == 0:
                    break
            
            iter_column += 1

        # Fill last column/VBoxLayout with dummy QLabels
        while (iter_rtsp % 3) != 0:
            vBox.addWidget(QLabel("Dummy"))
            iter_rtsp += 1

        # Create another column for the main stream
        vBox = QVBoxLayout()
        label = QLabel()
        label.setFixedSize(800, 724)
        self.labels.append(label)
        vBox.addWidget(label)

        # Set DEFAULT main stream to display rtsp #1 (rtsp_list[0])
        self.setMainStream(0)

        self.hLayout.addLayout(vBox)

    def setMainStream(self, rtsp_id = int):
        """
            View rtsp_id at the main stream label
        """
        if self.current_main == rtsp_id:
            util.logging.info(f"Main stream already set to stream #{rtsp_id}")
            return
        if self.current_main != rtsp_id:
            # Only pop() label_id item at the 2nd setMainStream call and so on
            if self.current_main != None:
                self.rtsp_list[self.current_main]['label_id'].pop()
            self.current_main = rtsp_id
        util.logging.info(f"Setting main stream to {rtsp_id}")
        self.rtsp_list[rtsp_id]['label_id'].append(len(self.labels) - 1)

    def closeEvent(self, event):
        """Called automatically when the window is closed"""
        for thread in self.threads:
            thread.stop()
        event.accept()