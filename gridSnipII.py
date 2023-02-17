

from PIL.ImageQt import ImageQt

import tkinter
from tkinter import filedialog

import time
from PIL import ImageGrab

import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QPixmap
from PyQt5.QtCore import Qt


#painting in pyQt5
#convert this for use on a screen
class clearWindow(QMainWindow):
    #snipping tool, driver class with main function
    #This class is used to generate a transparent window
    #the user then drags a rectangular area that they wish to snip, from which we extract the upper left and bottom right coordinate points
    #using cropIt.py, a screenshot is taken of the entire window
    #the coordinate data is then used to crop the screenshot
    #giving the illusion the user has taken a snip of the screen

    def __init__(self):
        super().__init__()

        #after showFullScreen(), make transparent
        self.setStyleSheet("background:transparent")
        self.setAttribute(Qt.WA_TranslucentBackground)

        #init instance variables self.begin and self.end as qpoints
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        self.rectangle = None
        self.Hline = None
        self.Vline = None
        

    def paintEvent(self, event): #drawing process, runs whenever mouse is clicked, ends when mouse released.
        
        qp = QPainter(self)
        qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))

        #define the rectangle
        #normalized() prevents negative coordinates
        self.rectangle = QtCore.QRectF(self.begin, self.end).normalized()
        qp.drawRect(self.rectangle)  #Qrect draws a rectangle using two points as reference

        #draw the horizontal line----------------------
        x = self.begin.x() + ((self.end.x() - self.begin.x())//2)
        yi = self.begin.y()
        yf = self.end.y()

        self.Hline = QtCore.QLine(x, yi, x, yf)

        qp.drawLine(self.Hline)
        
        #draw the vertical line----------------------
        y = self.begin.y() + ((self.end.y() - self.begin.y())//2)
        xi = self.begin.x()
        xf = self.end.x()

        self.Vline = QtCore.QLine(xi, y, xf, y)

        qp.drawLine(self.Vline)

        #---make the area outside the selected rectangle transparent---
        transparentColor = QColor(128,128,128) #takes RGB
        transparentColor.setAlphaF(0.2) #controls transparency, qreal alpha specified in the range 0.0-1.0.
        qp.setBrush(transparentColor)

        outer = QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect())) #self.rect() builtin function of pyqt5 library
        #PyQt5 – rect() method, used to get the geometry of the window or any widget
        #addRect takes floats, so must use QRectF() around self.rect()

        inner = QPainterPath()
        inner.addRect(self.rectangle) #this is the rectangle the user has drawn

        #subtract the select area from the area of the whole screen
        difference_path = outer - inner #can subtract QPainterpaths
        qp.drawPath(difference_path)

    #the code below changes location of the qpoints according to your mouse press and release.
    #Reimplement QWidget event handlers, mousePressEvent(), mouseReleaseEvent(), mouseMoveEvent() to receive mouse events in your own widgets.
    #self.update() allows widgets to refresh.
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.end = event.pos()
        self.update()

        self.close() #hide fullscreenwindow, hdiing the grid before taking screenshot

        time.sleep(0.5) #need to wait for close() operation

        img=ImageGrab.grab(bbox = self.rectangle.getCoords()) #bbox = bounding box

        #Qpixmap_img = self.convert_PIL_to_Qpixmap(img)

        #a Qgraphicsview is required to attach widgets
        #myrotateWidget will create a new window with a Qgraphicsview
        # self.myrotateWidget = rotateWidget(Qpixmap_img) #this only works if you use 'self'
        # self.myrotateWidget.show()

        img.show()
        self.save_img(img)
        
    def convert_PIL_to_Qpixmap(self, img):
        #https://stackoverflow.com/questions/34697559/pil-image-to-qpixmap-conversion-issue
        qim = ImageQt(img)
        pix = QPixmap.fromImage(qim)
        return pix

    def save_img(self, img):
        #bring up the save dialogue
        #try to save
        try:
            file_types = [('jpeg', '.jpeg'), ('png', '.png'), ('All files', '*')]
            file_path = filedialog.asksaveasfilename(filetypes = file_types, defaultextension = '.png')
            img.save(file_path)
        except ValueError:
            print('Pls save as png or jpeg')
            #even if you press cancel on filedialog, it will trigger this message.

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = clearWindow()
    window.showFullScreen() #Shows the widget in full-screen mode, allowing accurate coordinate data.

    sys.exit(app.exec_())