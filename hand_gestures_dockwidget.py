# -*- coding: utf-8 -*-
"""
/***************************************************************************
 HandGesturesDockWidget
                                 A QGIS plugin
 Zoom and pan using hand gestures
                             -------------------
        begin                : 2016-10-29
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Sebastian Roll
        email                : sebastianroll84@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic
from collections import OrderedDict
from functools import partial

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import cv2
import sys
import sys
from time import sleep, time

import cv2
import numpy as np
import math
from PyQt4 import QtGui, QtCore
from enum import Enum

from PyQt4.QtCore import QObject, pyqtSlot
from PyQt4.QtCore import pyqtSignal
from PyQt4.QtCore import QThread
from PyQt4.QtGui import QWidget
from qgis._core import QgsRectangle, QgsVector

from utils import do_zoom, pan_left, pan_right, pan_up, pan_down, do_nothing
from videogesturewidget import find_gesture, Gestures

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'hand_gestures_dockwidget_base.ui'))


class HandGesturesDockWidget(QtGui.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()
    progress = pyqtSignal(int)
    gesture = QtCore.pyqtSignal(Gestures)

    def __init__(self, canv, parent=None):
        """Constructor."""
        super(HandGesturesDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.video_size = QSize(640, 480)

        # set hand rectangle dimensions
        self.handrect_x = 200
        self.handrect_y = 200
        self.handrect_width = 200
        self.handrect_height = 200

        # start progress timer
        self.maxdt = 1.
        self.gesture_time = time()

        # set hand rectangle position sliders
        self.slider_vert.setRange(0, 640)
        self.slider_hor.setRange(0, 480)
        self.slider_vert.setValue(self.handrect_x)
        self.slider_vert.valueChanged.connect(self.on_vertslider_changed)
        self.slider_hor.setValue(self.handrect_y)
        self.slider_hor.valueChanged.connect(self.on_horslider_changed)

        self.canv = canv

        funcs = OrderedDict()
        funcs['do nothing'] =  do_nothing
        funcs['pan left'] = partial(pan_left, self.canv)
        funcs['pan right'] = partial(pan_right, self.canv)
        funcs['pan up'] = partial(pan_up, self.canv)
        funcs['pan down'] = partial(pan_down, self.canv)
        funcs['zoom in'] = partial(self.canv.zoomByFactor, 2)
        funcs['zoom out'] = partial(self.canv.zoomByFactor, 0.5)

        self.comboboxes = [self.comboBox_2, self.comboBox_3, self.comboBox_4, self.comboBox_5]
        for idx, combobox in enumerate(self.comboboxes):
            for funcname, func in funcs.items():
                combobox.addItem(funcname, func)
            combobox.setCurrentIndex(0)


        self.setup_camera()

        self.progress.connect(self.progressBar.setValue)

        self.current_gesture = None

    def on_vertslider_changed(self, value):
        self.handrect_y = value

    def on_horslider_changed(self, value):
        self.handrect_x = value


    def setup_camera(self):
        """Initialize camera.
        """
        self.capture = cv2.VideoCapture(0)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.video_size.width())
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.video_size.height())

        self.timer = QTimer()
        self.timer.timeout.connect(self.display_video_stream)
        self.timer.start(30)

    def display_video_stream(self):
        """Read frame from camera and repaint QLabel widget.
        """
        _, frame = self.capture.read()

        if frame is None:
            return

        # hand rectangle dimensions
        x0 = self.video_size.height() - int(self.handrect_y + self.handrect_height / 2.)
        x1 = self.video_size.height() - int(self.handrect_y - self.handrect_height / 2.)
        y0 = int(self.handrect_x - self.handrect_width / 2.)
        y1 = int(self.handrect_x + self.handrect_width / 2.)
        cv2_p0 = (y0, x0)
        cv2_p1 = (y1, x1)
        self.video_size.width()

        frame, count_defects = find_gesture(frame, hand_p0=cv2_p1, hand_p1=cv2_p0,
                                            invert=self.checkBox_invert.isChecked())

        if count_defects == Gestures.ONE.value:
            cv2.putText(frame, "closed fist", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        elif count_defects == 2:
            cv2.putText(frame, "Two fingers", (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)

        elif count_defects == 3:
            cv2.putText(frame, "three fingers", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        elif count_defects == 4:
            cv2.putText(frame, "four fingers", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
        else:
            cv2.putText(frame, "five fingers", (50, 50), \
                        cv2.FONT_HERSHEY_SIMPLEX, 2, 2)

        if count_defects != self.current_gesture or count_defects == Gestures.ONE.value:
            # update progress time
            self.gesture_time = time()
            self.progressBar.setValue(0)
        else:
            self.current_gesture = count_defects

            dt = time() - self.gesture_time

            if dt < self.maxdt:
                # update progress bar
                self.progressBar.setValue(int(100*dt/self.maxdt))
            else:
                # trigger action
                cbox = self.comboboxes[max(min(4, count_defects-2), 0)]
                func_idx = cbox.currentIndex()
                callfunc = cbox.itemData(func_idx)
                callfunc()
                self.labelStatus.setText("{}, {}".format(count_defects, cbox.itemText(func_idx)))

                # reset progress time
                self.gesture_time = time()

        self.current_gesture = count_defects
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0],
                       frame.strides[0], QImage.Format_RGB888)
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.timer.stop()
        self.closingPlugin.emit()
        self.capture.release()
        event.accept()

