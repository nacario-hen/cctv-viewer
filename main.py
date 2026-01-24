from PyQt5.QtWidgets import QApplication
import sys
import utilities as util
import loadUI as UI

if __name__ == "__main__":

    rtsp_list = util.load_stream()
    app = QApplication(sys.argv)
    ui = UI.UIversion2(rtsp_list)
    ui.show()
    app.exec_()