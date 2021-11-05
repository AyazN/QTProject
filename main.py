import sys
import sqlite3
from datetime import datetime
from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlRelationalTableModel, QSqlRelation
from PyQt5.QtCore import QPoint, QLine
from PyQt5.QtGui import QPainter, QPolygon, QColor, QPen
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QColorDialog

class Program(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Paint.ui', self)
        self.points = []
        self.POLYGONNUMBER = 1
        self.ELLIPSENUMBER = 2
        self.RECTANGLENUMBER = 3
        self.LINENUMBER = 4
        self.CURVENUMBER = 5
        self.ERASENUMBER = 6
        self.ERASEPEN = QPen(QColor(240, 240, 240), 20)
        self.colorbrush = QColor(240, 240, 240)
        self.colorpen = QColor(0, 0, 0)
        self.btnback.setDisabled(True)
        self.btnreturn.setDisabled(True)
        self.takemousepos = False
        self.polygondraw = False
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.buttoneraseactiv = False
        self.startpostaken = False
        self.curvelines = []
        self.allfigures = []
        self.figuresdeleted = []
        self.btnpolygon.clicked.connect(self.buttonpolygon)
        self.btnellipse.clicked.connect(self.buttonellipse)
        self.btnrectangle.clicked.connect(self.buttonrectangle)
        self.btnline.clicked.connect(self.buttonline)
        self.btncurve.clicked.connect(self.buttoncurve)
        self.btnclrbrush.clicked.connect(self.buttonclrbrush)
        self.btnclrpen.clicked.connect(self.buttonclrpen)
        self.btnerase.clicked.connect(self.buttonerase)
        self.btneraseall.clicked.connect(self.buttoneraseall)
        self.btnclearhistory.clicked.connect(self.buttonclearhistory)
        self.tab_5.currentChanged.connect(self.tabledb)
        self.btnback.clicked.connect(self.buttonback)
        self.btnreturn.clicked.connect(self.buttonreturn)
        self.con = sqlite3.connect('changelog.sqlite')
        self.cur = self.con.cursor()
        self.cur.execute("""DROP TABLE IF EXISTS changes""")
        self.cur.execute("""CREATE TABLE changes (
            id       INTEGER UNIQUE
                             NOT NULL
                             PRIMARY KEY AUTOINCREMENT,
            time     STRING NOT NULL,
            figureID INTEGER REFERENCES figures (id) 
                             NOT NULL
        );
        """)
        self.con.commit()

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
        self.buttoncurveactiv = False
        self.sides, ok_pressed = QInputDialog.getInt(
            self, "Количество углов", "Введите количество вершин",
            3, 3, 15, 1)
        if ok_pressed:
            self.buttonpolygonactiv = True
            self.points = []

    def buttonellipse(self):
        self.buttonpolygonactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.buttonellipseactiv = True
        self.buttoncurveactiv = False
        self.points = []

    def buttonrectangle(self):
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.buttonrectangleactiv = True
        self.buttoncurveactiv = False
        self.points = []

    def buttonline(self):
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttoncurveactiv = False
        self.buttonlineactiv = True
        self.buttoneraseactiv = False
        self.points = []

    def buttoncurve(self):
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = True
        self.buttoneraseactiv = False
        self.points = []

    def buttonerase(self):
        self.buttonpolygonactiv = False
        self.buttonellipseactiv = False
        self.buttonrectangleactiv = False
        self.buttonlineactiv = False
        self.buttoncurveactiv = False
        self.buttoneraseactiv = True
        self.points = []

    def buttoneraseall(self):
        self.allfigures = []
        self.repaint()

    def buttonclearhistory(self):
        self.cur.execute("""DELETE FROM changes""")
        self.con.commit()
        self.model.setTable('changes')
        self.model.select()
        self.tableview.setModel(self.model)

    def buttonback(self):
        self.figuresdeleted.insert(0, self.allfigures.pop(-1))
        self.repaint()
        self.btnreturn.setDisabled(False)
        if len(self.allfigures) == 0:
            self.btnback.setDisabled(True)

    def buttonreturn(self):
        self.allfigures.append(self.figuresdeleted.pop(0))
        self.repaint()
        self.btnback.setDisabled(False)
        if len(self.figuresdeleted) == 0:
            self.btnreturn.setDisabled(True)

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
        if self.buttonellipseactiv or self.buttonrectangleactiv or self.buttonlineactiv or\
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
                                        self.colorbrush, self.colorpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 1)""")
                self.polygondraw = False
                self.points = []
            elif self.buttonellipseactiv:
                self.allfigures.append((self.ELLIPSENUMBER, (self.x, self.y, self.xside, self.yside),
                                        self.colorbrush, self.colorpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 2)""")
            elif self.buttonrectangleactiv:
                self.allfigures.append((self.RECTANGLENUMBER, (self.x, self.y, self.xside, self.yside),
                                        self.colorbrush, self.colorpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 3)""")
            elif self.buttonlineactiv:
                self.allfigures.append((self.LINENUMBER, (self.point, QPoint(self.position[0], self.position[1])),
                                        self.colorbrush, self.colorpen))
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 4)""")
            elif self.buttoncurveactiv:
                self.allfigures.append((self.CURVENUMBER, self.curvelines, self.colorbrush, self.colorpen))
                self.curvelines = []
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 5)""")
            elif self.buttoneraseactiv:
                self.allfigures.append((self.ERASENUMBER, self.curvelines, self.colorbrush, self.ERASEPEN))
                self.curvelines = []
                self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 6)""")
            self.con.commit()
            self.btnback.setDisabled(False)

    def tabledb(self):
        if self.tab_5.currentIndex() == 3:
            db = QSqlDatabase.addDatabase('QSQLITE')
            db.setDatabaseName('changelog.sqlite')
            db.open()
            self.model = QSqlRelationalTableModel(self, db)
            self.model.setTable('changes')
            self.model.setRelation(2, QSqlRelation("figures", "id", "figure"))
            self.model.select()
            self.tableview.setModel(self.model)

    def drawfigure(self, qp):
        for i in self.allfigures:
            qp.setBrush(i[2])
            qp.setPen(i[3])
            if i[0] == self.POLYGONNUMBER:
                qp.drawPolygon(i[1])
            elif i[0] == self.ELLIPSENUMBER:
                qp.drawEllipse(i[1][0], i[1][1], i[1][2], i[1][3])
            elif i[0] == self.RECTANGLENUMBER:
                qp.drawRect(i[1][0], i[1][1], i[1][2], i[1][3])
            elif i[0] == self.LINENUMBER:
                qp.drawLine(i[1][0], i[1][1])
            elif i[0] == self.CURVENUMBER or i[0] == self.ERASENUMBER:
                for _ in i[1]:
                    qp.drawLine(_)
        qp.setBrush(self.colorbrush)
        qp.setPen(self.colorpen)
        if self.polygondraw:
            qp.drawPolygon(QPolygon(self.points))
        elif (self.buttonellipseactiv or self.buttonrectangleactiv) and self.startpostaken:
            point = self.points[-1]
            if point.x() > self.position[0]:
                self.x = point.x() + (self.position[0] - point.x())
                self.xside = (point.x() - self.position[0]) * 2
            elif point.x() < self.position[0]:
                self.x = point.x() - (self.position[0] - point.x())
                self.xside = (self.position[0] - point.x()) * 2
            else:
                self.x = self.position[0]
                self.xside = 0
            self.y = self.position[1]
            if point.y() > self.position[1]:
                self.yside = (point.y() - self.position[1]) * 2
            elif point.y() < self.position[1]:
                self.y = point.y() - (self.position[1] - point.y())
                self.yside = (self.position[1] - point.y()) * 2
            else:
                self.yside = 0
            if self.buttonellipseactiv:
                qp.drawEllipse(self.x, self.y, self.xside, self.yside)
            elif self.buttonrectangleactiv:
                qp.drawRect(self.x, self.y, self.xside, self.yside)
        elif self.buttonlineactiv and self.startpostaken:
            self.point = self.points[-1]
            qp.drawLine(self.point, QPoint(self.position[0], self.position[1]))
        elif (self.buttoncurveactiv or self.buttoneraseactiv) and self.startpostaken:
            if self.buttoneraseactiv:
                qp.setPen(self.ERASEPEN)
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
    ex = Program()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
