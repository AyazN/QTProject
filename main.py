import sys
from PyQt5 import uic
from PyQt5.QtCore import QPoint
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
        self.startpostaken = False
        self.btnpolygon.clicked.connect(self.buttonpolygon)
        self.btnellipse.clicked.connect(self.buttoncircle)
        self.buttoncircleactiv = False

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
        if self.buttoncircleactiv:
            self.position = [event.x(), event.y()]
            self.takemousepos = True
            self.startpostaken = True
            self.repaint()

    def mouseMoveEvent(self, event):
        if self.takemousepos and self.startpostaken:
            self.position = [event.x(), event.y()]
            self.repaint()

    def mouseReleaseEvent(self, event):
        if self.startpostaken:
            self.startpostaken = False
            self.buttoncircleactiv = False
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

    def buttoncircle(self):
        self.buttoncircleactiv = True
        self.points = []

    def drawfigure(self, qp):
        if self.polygondraw:
            qp.drawPolygon(QPolygon(self.points))
        if self.buttoncircleactiv and self.startpostaken:
            point = self.points[0]
            qp.drawEllipse(point.x(), point.y(),
                           self.position[0] - point.x(), self.position[1] - point.y())




def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Progr()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
