"""
Contains utility functions
"""

import os
import sys
import cv2
import logging
import datetime

def resource_path(relative_path):
    """ 
    Get absolute path to resource, works for dev and for PyInstaller
    """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def load_stream():
    """
    Checks and loads all streams existing in accounts.txt
    """
    accounts_path = resource_path('resources/streams/accounts.txt')
    if not os.path.exists(accounts_path):
        logging.debug("accounts.txt doesn't exist. Exiting application")
        exit()

    # rstrip removes \n from the read lines
    with open(accounts_path, 'r') as file:
        rtsp_list = [line.rstrip() for line in file.readlines()]
        file.close()

    # reversed(list(enumerate(rtsp_list))) creates reversed index and object
    # instead of checking 0, rtsp 1 at the first iteration, start at the end instead
    for i, stream in reversed(list(enumerate(rtsp_list))):
        cap = cv2.VideoCapture(stream)
        if not cap.isOpened():
            logging.info(f"Cannot open RTSP stream {i}")
            rtsp_list.pop(i)
        else:
            logging.info(f"RTSP stream {i} opened successfully")
            cap.release()

    # Check if list is empty. Empty = False. Not False = True
    if not rtsp_list:
        logging.debug("No active CCTV to stream")
        exit()

    return rtsp_list

logfname = resource_path(f'resources/log/[{datetime.datetime.now().strftime('%m-%d-%Y')}]log.log')
logging.basicConfig(level=logging.DEBUG, filename=resource_path(logfname), filemode="a",
                    format="[%(asctime)s|%(funcName)s|%(levelname)s] - %(message)s")