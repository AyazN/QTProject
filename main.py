import sys
import sqlite3
from datetime import datetime
from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from PyQt5.QtCore import QPoint, QLine
from PyQt5.QtGui import QPainter, QPolygon, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QColorDialog

class Progr(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Paint.ui', self)
        self.points = []
        self.POLYGONNUMBER = 1
        self.ELLIPSENUMBER = 2
        self.RECTANGLENUMBER = 3
        self.LINENUMBER = 4
        self.CURVENUMBER = 5
        self.colorbrush = QColor(240, 240, 240)
        self.colorpen = QColor(0, 0, 0)
        self.takemousepos = False
        self.polygondraw = False
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.startpostaken = False
        self.curvelines = []
        self.allfigures = []
        self.btnpolygon.clicked.connect(self.buttonpolygon)
        self.btnellipse.clicked.connect(self.buttonellipse)
        self.btnrectangle.clicked.connect(self.buttonrectangle)
        self.btnline.clicked.connect(self.buttonline)
        self.btncurve.clicked.connect(self.buttoncurve)
        self.btnclrbrush.clicked.connect(self.buttonclrbrush)
        self.btnclrpen.clicked.connect(self.buttonclrpen)
        self.tab_5.currentChanged.connect(self.tabledb)
        con = sqlite3.connect('changelog.sqlite')
        cur = con.cursor()
        cur.execute("""DROP TABLE IF EXISTS changes""")
        cur.execute("""CREATE TABLE changes (
            id       INTEGER UNIQUE
                             NOT NULL
                             PRIMARY KEY AUTOINCREMENT,
            time     INTEGER NOT NULL,
            figureID INTEGER REFERENCES figures (id) 
                             NOT NULL
        );
        """)
        con.commit()

    def buttonclrbrush(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colorbrush = QColor(color.getRgb()[0], color.getRgb()[1], color.getRgb()[2])

    def buttonclrpen(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.colorpen = QColor(color.getRgb()[0], color.getRgb()[1], color.getRgb()[2])

    def buttonpolygon(self):
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.sides, ok_pressed = QInputDialog.getInt(
            self, "Количество углов", "Введите количество вершин",
            3, 3, 15, 1)
        if ok_pressed:
            self.buttonpolygonactiv = True
            self.buttonpolygonerase = True
            self.points = []

    def buttonellipse(self):
        self.buttonpolygonactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.buttonellipseactiv = True
        self.points = []

    def buttonrectangle(self):
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.buttonrectangleactiv = True
        self.points = []

    def buttonline(self):
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttoncurveactiv = False
        self.buttonlineactiv = True
        self.points = []

    def buttoncurve(self):
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = True
        self.points = []

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
        if self.startpostaken:
            self.startpostaken = False
            self.takemousepos = False
        if self.polygondraw:
            self.allfigures.append((self.POLYGONNUMBER, QPolygon(self.points),
                                    self.colorbrush, self.colorpen))
        elif self.buttonellipseactiv:
            self.allfigures.append((self.ELLIPSENUMBER, (self.x, self.y, self.xside, self.yside),
                                    self.colorbrush, self.colorpen))
        elif self.buttonrectangleactiv:
            self.allfigures.append((self.RECTANGLENUMBER, (self.x, self.y, self.xside, self.yside),
                                    self.colorbrush, self.colorpen))
        elif self.buttonlineactiv:
            self.allfigures.append((self.LINENUMBER, (self.point, QPoint(self.position[0], self.position[1])),
                                                           self.colorbrush, self.colorpen))
        elif self.buttoncurveactiv:
            self.allfigures.append((self.CURVENUMBER, self.curvelines, self.colorbrush, self.colorpen))
            self.curvelines = []

    def tabledb(self):
        if self.tab_5.currentIndex() == 3:
            db = QSqlDatabase.addDatabase('QSQLITE')
            db.setDatabaseName('changelog.sqlite')
            db.open()
            model = QSqlTableModel(self, db)
            model.setTable('changes')
            model.select()
            self.tableview.setModel(model)

    def drawfigure(self, qp):
        for i in self.allfigures:
            qp.setBrush(i[2])
            qp.setPen(i[3])
            if i[0] == self.POLYGONNUMBER:
                qp.drawPolygon([1])
            elif i[0] == self.ELLIPSENUMBER:
                qp.drawEllipse(i[1][0], i[1][1], i[1][2], i[1][3])
            elif i[0] == self.RECTANGLENUMBER:
                qp.drawRect(i[1][0], i[1][1], i[1][2], i[1][3])
            elif i[0] == self.LINENUMBER:
                qp.drawLine(i[1][0], i[1][1])
            elif i[0] == self.CURVENUMBER:
                for _ in i[1]:
                    qp.drawLine(_)
        qp.setBrush(self.colorbrush)
        qp.setPen(self.colorpen)
        if self.polygondraw:
            qp.drawPolygon(QPolygon(self.points))
        elif self.buttonellipseactiv and self.startpostaken:
            point = self.points[-1]
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
            self.x = x
            self.y = y
            self.xside = xside
            self.yside = yside
        elif self.buttonrectangleactiv and self.startpostaken:
            point = self.points[-1]
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
            self.x = x
            self.y = y
            self.xside = xside
            self.yside = yside
        elif self.buttonlineactiv and self.startpostaken:
            self.point = self.points[-1]
            qp.drawLine(self.point, QPoint(self.position[0], self.position[1]))
        elif self.buttoncurveactiv and self.startpostaken:
            if self.buttoncurveactivfirst:
                self.curvelines.append(QLine(self.points[-1], QPoint(self.position[0], self.position[1])))
                self.pointstart = QPoint(self.position[0], self.position[1])
                self.buttoncurveactivfirst = False
            else:
                self.curvelines.append(QLine(self.pointstart, QPoint(self.position[0], self.position[1])))
                self.pointstart = QPoint(self.position[0], self.position[1])
            for _ in self.curvelines:
                qp.drawLine(_)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Progr()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
