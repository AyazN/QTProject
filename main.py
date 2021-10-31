import sys
from PyQt5 import uic
from PyQt5.QtCore import QPoint, QLine
from PyQt5.QtGui import QPainter, QPolygon
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog


class Progr(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Paint.ui', self)
        self.points = []
        self.takemousepos = False
        self.polygondraw = False
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.startpostaken = False
        self.curvelines = []
        self.btnpolygon.clicked.connect(self.buttonpolygon)
        self.btnellipse.clicked.connect(self.buttonellipse)
        self.btnrectangle.clicked.connect(self.buttonrectangle)
        self.btnline.clicked.connect(self.buttonline)
        self.btncurve.clicked.connect(self.buttoncurve)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawfigure(qp)
        qp.end()

    def mousePressEvent(self, event):
        self.points.append(QPoint(event.x(), event.y()))
        if self.buttonpolygonactiv:
            self.buttonpolygonerase = False
            if len(self.points) == self.sides:
                self.polygondraw = True
                self.repaint()
                self.polygondraw = False
                self.buttonpolygonactiv = False
        if self.buttonellipseactiv or self.buttonrectangleactiv or self.buttonlineactiv or\
                self.buttoncurveactiv:
            if self.buttoncurveactiv:
                self.buttoncurveactivfirst = True
            self.position = [event.x(), event.y()]
            self.takemousepos = True
            self.startpostaken = True
            self.repaint()

    def mouseMoveEvent(self, event):
        if self.takemousepos and self.startpostaken:
            self.position = [event.x(), event.y()]
            self.repaint()

    def mouseReleaseEvent(self, event):
        if self.buttonellipseactiv:
            self.buttonellipseactiv = False
        if self.buttonrectangleactiv:
            self.buttonrectangleactiv = False
        if self.buttonlineactiv:
            self.buttonlineactiv = False
        if self.buttoncurveactiv:
            self.buttoncurveactiv = False
        if self.startpostaken:
            self.startpostaken = False
            self.startpostaken = False
            self.takemousepos = False

    def buttonpolygon(self):
        self.sides, ok_pressed = QInputDialog.getInt(
            self, "Количество углов", "Введите количество вершин",
            3, 3, 15, 1)
        if ok_pressed:
            self.buttonpolygonactiv = True
            self.buttonpolygonerase = True
            self.points = []

    def buttonellipse(self):
        self.buttonellipseactiv = True
        self.points = []

    def buttonrectangle(self):
        self.buttonrectangleactiv = True
        self.points = []

    def buttonline(self):
        self.buttonlineactiv = True
        self.points = []

    def buttoncurve(self):
        self.buttoncurveactiv = True
        self.points = []

    def drawfigure(self, qp):
        if self.polygondraw:
            qp.drawPolygon(QPolygon(self.points))
        if self.buttonellipseactiv and self.startpostaken:
            point = self.points[0]
            if point.x() > self.position[0]:
                x = point.x() + (self.position[0] - point.x())
                xside = (point.x() - self.position[0]) * 2
            elif point.x() < self.position[0]:
                x = point.x() - (self.position[0] - point.x())
                xside = (self.position[0] - point.x()) * 2
            else:
                x = self.position[0]
                xside = 0
            y = self.position[1]
            if point.y() > self.position[1]:
                yside = (point.y() - self.position[1]) * 2
            elif point.y() < self.position[1]:
                y = point.y() - (self.position[1] - point.y())
                yside = (self.position[1] - point.y()) * 2
            else:
                yside = 0
            qp.drawEllipse(x, y, xside, yside)
        if self.buttonrectangleactiv and self.startpostaken:
            point = self.points[0]
            if point.x() > self.position[0]:
                x = point.x() + (self.position[0] - point.x())
                xside = (point.x() - self.position[0]) * 2
            elif point.x() < self.position[0]:
                x = point.x() - (self.position[0] - point.x())
                xside = (self.position[0] - point.x()) * 2
            else:
                x = self.position[0]
                xside = 0
            y = self.position[1]
            if point.y() > self.position[1]:
                yside = (point.y() - self.position[1]) * 2
            elif point.y() < self.position[1]:
                y = point.y() - (self.position[1] - point.y())
                yside = (self.position[1] - point.y()) * 2
            else:
                yside = 0
            qp.drawRect(x, y, xside, yside)
        if self.buttonlineactiv and self.startpostaken:
            point = self.points[0]
            qp.drawLine(point, QPoint(self.position[0], self.position[1]))


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Progr()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
