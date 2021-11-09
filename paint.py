import sqlite3
from datetime import datetime
from PyQt5.QtCore import QPoint, QLine, pyqtSignal
from PyQt5.QtGui import QPainter, QPolygon, QColor, QPen
from PyQt5.QtWidgets import QLabel
from ellipserectanglefigure import ellipseorrectangle


class Paint(QLabel):
    figureDrawn = pyqtSignal()


    def __init__(self, parent):
        super(Paint, self).__init__(parent)
        self.points = []
        self.curvelines = []
        self.allfigures = []
        self.figuresdeleted = []
        self.POLYGONNUMBER = 1
        self.ELLIPSENUMBER = 2
        self.RECTANGLENUMBER = 3
        self.LINENUMBER = 4
        self.CURVENUMBER = 5
        self.ERASENUMBER = 6
        self.PICTURENUMBER = 7
        self.ERASEPEN = QColor(240, 240, 240)
        self.colorbrush = QColor(240, 240, 240)
        self.colorpen = QColor(0, 0, 0)
        self.thickpen = 1
        self.takemousepos = False
        self.polygondraw = False
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.buttoneraseactiv = False
        self.startpostaken = False
        self.con = sqlite3.connect('changelog.sqlite')
        self.cur = self.con.cursor()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.drawfigure(qp)
        qp.end()

    def mousePressEvent(self, event):
        self.points.append(QPoint(event.x(), event.y()))
        if self.buttonpolygonactiv:
            if len(self.points) == self.sides:
                self.polygondraw = True
                self.repaint()
        if self.buttonellipseactiv or self.buttonrectangleactiv or self.buttonlineactiv or \
                self.buttoncurveactiv or self.buttoneraseactiv:
            if self.buttoncurveactiv or self.buttoneraseactiv:
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
        currenttime = f'{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}'
        if (self.polygondraw or self.buttonellipseactiv or self.buttonrectangleactiv or
                self.buttonlineactiv or self.buttoncurveactiv or self.buttoneraseactiv):
            if self.polygondraw:
                self.allfigures.append((self.POLYGONNUMBER, QPolygon(self.points),
                                        self.colorbrush, self.colorpen, self.thickpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 1)""")
                self.polygondraw = False
                self.points = []
            elif self.buttonellipseactiv:
                self.allfigures.append((self.ELLIPSENUMBER, self.figure,
                                        self.colorbrush, self.colorpen, self.thickpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 2)""")
            elif self.buttonrectangleactiv:
                self.allfigures.append((self.RECTANGLENUMBER, self.figure,
                                        self.colorbrush, self.colorpen, self.thickpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 3)""")
            elif self.buttonlineactiv:
                self.allfigures.append((self.LINENUMBER, (self.point, QPoint(self.position[0], self.position[1])),
                                        self.colorbrush, self.colorpen, self.thickpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 4)""")
            elif self.buttoncurveactiv:
                self.allfigures.append((self.CURVENUMBER, self.curvelines, self.colorbrush, self.colorpen,
                                        self.thickpen))
                self.curvelines = []
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 5)""")
            elif self.buttoneraseactiv:
                self.allfigures.append((self.ERASENUMBER, self.curvelines, self.colorbrush, self.ERASEPEN,
                                        self.thickpen))
                self.curvelines = []
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 6)""")
            self.con.commit()
            self.figureDrawn.emit()
            self.figuresdeleted = []

    def drawfigure(self, qp):
        for i in self.allfigures:
            qp.setBrush(i[2])
            qp.setPen(QPen(i[3], i[4]))
            if i[0] == self.POLYGONNUMBER:
                qp.drawPolygon(*i[1].drawing())
            elif i[0] == self.ELLIPSENUMBER:
                qp.drawEllipse(*i[1].drawing())
            elif i[0] == self.RECTANGLENUMBER:
                qp.drawRect(i[1][0], i[1][1], i[1][2], i[1][3])
            elif i[0] == self.LINENUMBER:
                qp.drawLine(i[1][0], i[1][1])
            elif i[0] == self.CURVENUMBER or i[0] == self.ERASENUMBER:
                for _ in i[1]:
                    qp.drawLine(_)
            elif i[0] == self.PICTURENUMBER:
                qp.drawPixmap(0, 0, i[1])
        qp.setBrush(self.colorbrush)
        qp.setPen(QPen(self.colorpen, self.thickpen))
        if self.polygondraw:
            qp.drawPolygon(QPolygon(self.points))
        elif (self.buttonellipseactiv or self.buttonrectangleactiv) and self.startpostaken:
            point = self.points[-1]
            self.figure = ellipseorrectangle(point.x(), point.y(), self.position[0], self.position[1])
            if self.buttonellipseactiv:
                qp.drawEllipse(*self.figure.drawing())
            elif self.buttonrectangleactiv:
                qp.drawRect(*self.figure.drawing())
        elif self.buttonlineactiv and self.startpostaken:
            self.point = self.points[-1]
            qp.drawLine(self.point, QPoint(self.position[0], self.position[1]))
        elif (self.buttoncurveactiv or self.buttoneraseactiv) and self.startpostaken:
            if self.buttoneraseactiv:
                qp.setPen(QPen(self.ERASEPEN, self.thickpen))
            if self.buttoncurveactivfirst:
                self.curvelines.append(QLine(self.points[-1], QPoint(self.position[0], self.position[1])))
                self.pointstart = QPoint(self.position[0], self.position[1])
                self.buttoncurveactivfirst = False
            else:
                self.curvelines.append(QLine(self.pointstart, QPoint(self.position[0], self.position[1])))
                self.pointstart = QPoint(self.position[0], self.position[1])
            for _ in self.curvelines:
                qp.drawLine(_)
