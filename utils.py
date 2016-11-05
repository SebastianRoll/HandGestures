#!/usr/bin/env python
# -*- coding: <encoding name> -*-

"""Insert module docstring here."""

#imports

__author__ = "Sebastian Roll"

#!/usr/bin/env python
# -*- coding: <encoding name> -*-

"""Insert module docstring here."""

from qgis._core import QgsRectangle, QgsVector
from PyQt4.QtCore import qAbs
__author__ = "Sebastian Roll"


def do_zoom(canv, delta=0.5):
    #canv = self.iface.mapCanvas()
    # extent = canv.extent()
    # self.dockwidget.lineEdit_2.setText(extent.toString())
    # new_extent = extent.scale(delta)
    # rect = QgsRectangle(0, 0, 100, 100)
    # canv.setExtent(extent)

    currentExtent = canv.mapSettings().visibleExtent()
    dx = qAbs(currentExtent.width() / 4)
    dy = qAbs(currentExtent.height() / 4)
    M_PI = 3.14159265358979323846

    # canv.keyPressed(key_event)
    # TypeError: native Qt signal is not callable
    # canv.keyPressEvent(key_event)
    #  RuntimeError: no access to protected functions or signals for objects not created from Python
    # key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Left, Qt.NoModifier)

    canv.setCenter(canv.center() - QgsVector(dx, 0).rotateBy(canv.rotation() * M_PI / 180.0))
    # canv.zoomIn()
    canv.refresh()

    # self.dockwidget.lineEdit.setText(extent.toString())


def pan_left(canv):
    currentExtent = canv.mapSettings().visibleExtent()
    dx = qAbs(currentExtent.width() / 4)
    dy = qAbs(currentExtent.height() / 4)
    M_PI = 3.14159265358979323846
    canv.setCenter(canv.center() - QgsVector(dx, 0).rotateBy(canv.rotation() * M_PI / 180.0))
    canv.refresh()

def pan_right(canv):
    currentExtent = canv.mapSettings().visibleExtent()
    dx = qAbs(currentExtent.width() / 4)
    dy = qAbs(currentExtent.height() / 4)
    M_PI = 3.14159265358979323846
    canv.setCenter(canv.center() - QgsVector(-dx, 0).rotateBy(canv.rotation() * M_PI / 180.0))
    canv.refresh()

def pan_up(canv):
    currentExtent = canv.mapSettings().visibleExtent()
    dx = qAbs(currentExtent.width() / 4)
    dy = qAbs(currentExtent.height() / 4)
    M_PI = 3.14159265358979323846
    canv.setCenter(canv.center() - QgsVector(0, dy).rotateBy(canv.rotation() * M_PI / 180.0))
    canv.refresh()

def pan_down(canv):
    currentExtent = canv.mapSettings().visibleExtent()
    dx = qAbs(currentExtent.width() / 4)
    dy = qAbs(currentExtent.height() / 4)
    M_PI = 3.14159265358979323846
    canv.setCenter(canv.center() - QgsVector(0, -dy).rotateBy(canv.rotation() * M_PI / 180.0))
    canv.refresh()


def do_nothing():
    pass