import sys
import sqlite3
from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlRelationalTableModel, QSqlRelation
from PyQt5.QtGui import QColor, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QColorDialog, QFileDialog
from datetime import datetime


class Program(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('designer.ui', self)
        self.move(0, 0)
        self.btnback.setDisabled(True)
        self.btnreturn.setDisabled(True)
        self.paint.figureDrawn.connect(self.figuredrawn)
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
        self.btnload.clicked.connect(self.buttonload)
        self.btnthckpen.clicked.connect(self.buttonthickpen)
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
        self.tableview.hide()
        self.image = QImage('picture.jpg')
        imag = QPixmap.fromImage(self.image)
        self.paint.setPixmap(imag)

    def buttonclrbrush(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.paint.colorbrush = QColor(color.getRgb()[0], color.getRgb()[1], color.getRgb()[2])

    def buttonclrpen(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.paint.colorpen = QColor(color.getRgb()[0], color.getRgb()[1], color.getRgb()[2])

    def buttonpolygon(self):
        self.paint.buttonellipseactiv = False
        self.paint.buttonrectangleactiv = False
        self.paint.buttonlineactiv = False
        self.paint.buttoncurveactiv = False
        self.paint.buttoneraseactiv = False
        self.paint.sides, ok_pressed = QInputDialog.getInt(
            self, "Количество углов", "Введите количество вершин",
            3, 3, 20, 1)
        if ok_pressed:
            self.paint.buttonpolygonactiv = True
            self.paint.points = []

    def buttonellipse(self):
        self.paint.buttonpolygonactiv = False
        self.paint.buttonrectangleactiv = False
        self.paint.buttonlineactiv = False
        self.paint.buttoncurveactiv = False
        self.paint.buttonellipseactiv = True
        self.paint.buttoneraseactiv = False
        self.paint.points = []

    def buttonrectangle(self):
        self.paint.buttonpolygonactiv = False
        self.paint.buttonellipseactiv = False
        self.paint.buttonlineactiv = False
        self.paint.buttoncurveactiv = False
        self.paint.buttonrectangleactiv = True
        self.paint.buttoneraseactiv = False
        self.paint.points = []

    def buttonline(self):
        self.paint.buttonpolygonactiv = False
        self.paint.buttonellipseactiv = False
        self.paint.buttonrectangleactiv = False
        self.paint.buttoncurveactiv = False
        self.paint.buttonlineactiv = True
        self.paint.buttoneraseactiv = False
        self.paint.points = []

    def buttoncurve(self):
        self.paint.buttonpolygonactiv = False
        self.paint.buttonellipseactiv = False
        self.paint.buttonrectangleactiv = False
        self.paint.buttonlineactiv = False
        self.paint.buttoncurveactiv = True
        self.paint.buttoneraseactiv = False
        self.paint.points = []

    def buttonerase(self):
        self.paint.buttonpolygonactiv = False
        self.paint.buttonellipseactiv = False
        self.paint.buttonrectangleactiv = False
        self.paint.buttonlineactiv = False
        self.paint.buttoncurveactiv = False
        self.paint.buttoneraseactiv = True
        self.paint.points = []

    def buttoneraseall(self):
        self.paint.figuresdeleted = []
        self.paint.figuresdeleted.extend(self.paint.allfigures)
        self.paint.allfigures = []
        self.paint.repaint()
        self.btnreturn.setDisabled(True)
        self.paint.figureDrawn.emit()

    def buttonclearhistory(self):
        self.cur.execute("""DELETE FROM changes""")
        self.con.commit()
        self.model.setTable('changes')
        self.model.select()
        self.tableview.setModel(self.model)

    def buttonback(self):
        if len(self.paint.allfigures) == 0:
            self.paint.allfigures = self.paint.figuresdeleted
            self.paint.figuresdeleted = []
            self.paint.repaint()
            self.btnreturn.setDisabled(False)
        else:
            self.paint.figuresdeleted.insert(0, self.paint.allfigures.pop(-1))
            self.paint.repaint()
            self.btnreturn.setDisabled(False)
            if len(self.paint.allfigures) == 0:
                self.btnback.setDisabled(True)

    def buttonreturn(self):
        if len(self.paint.figuresdeleted) == 0:
            self.buttoneraseall()
        else:
            self.paint.allfigures.append(self.paint.figuresdeleted.pop(0))
            self.paint.repaint()
            self.btnback.setDisabled(False)
            if len(self.paint.figuresdeleted) == 0:
                self.btnreturn.setDisabled(True)

    def buttonload(self):
        currenttime = f'{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}'
        filename = QFileDialog.getOpenFileName(self, 'Выбрать картинку', '',
                                            'Image Files (*.png *.jpg *.jpeg *.bmp)')[0]
        picture = QPixmap(filename)
        if picture.size().height() > self.paint.height():
            picture = picture.scaled(picture.size().width(), self.paint.height())
        if picture.size().width() > self.paint.width():
            picture = picture.scaled(self.paint.width(), picture.size().height())
        self.paint.allfigures.append([self.paint.PICTURENUMBER, picture, self.paint.colorbrush,
                                      self.paint.colorpen, self.paint.thickpen])
        self.cur.execute(f"""INSERT INTO changes (time, figureID) VALUES ('{currenttime}', 7)""")
        self.con.commit()
        self.paint.repaint()
        self.paint.figureDrawn.emit()

    def buttonthickpen(self):
        thickpen, ok_pressed = QInputDialog.getInt(
            self, "Толщина линии", "Введите толщину линии",
            1, 1, 30, 1)
        if ok_pressed:
            self.paint.thickpen = thickpen

    def tabledb(self):
        if self.tab_5.currentIndex() == 2:
            self.tableview.show()
            self.paint.hide()
            db = QSqlDatabase.addDatabase('QSQLITE')
            db.setDatabaseName('changelog.sqlite')
            db.open()
            self.model = QSqlRelationalTableModel(self, db)
            self.model.setTable('changes')
            self.model.setRelation(2, QSqlRelation("figures", "id", "figure"))
            self.model.select()
            self.tableview.setModel(self.model)
        else:
            self.tableview.hide()
            self.paint.show()

    def figuredrawn(self):
        self.btnback.setDisabled(False)
        self.btnreturn.setDisabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Program()
    ex.show()
    sys.exit(app.exec())
