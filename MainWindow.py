import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QCompleter,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from CentralWidget import CentralWidget
from Util import Util

class MainWindow(QMainWindow):
    def __init__(self, app:QApplication):
        super().__init__()
        self.statusbar = self.statusBar()
        self.setWindowTitle("세력모니터 1.2")
        self.setGeometry(99, 99, 99, 99)
        self.centralwidget = CentralWidget(self, app)
        self.setCentralWidget(self.centralwidget)
        menubar = self.menuBar()
        menu = menubar.addMenu("기능")
        action = menu.addAction("종료(&X)")
        action.triggered.connect(self.close)
        menu.addSeparator()
        action = menu.addAction("파일 체크")
        action.triggered.connect(self.checkfile)

    def checkfile(self):
        dirlist = os.listdir()
        if ("atad.p" in dirlist) and ("data.p" in dirlist):
            mtime0 = os.path.getmtime("atad.p")
            timestr0 = Util.float2time(mtime0)
            mtime1 = os.path.getmtime("data.p")
            timestr1 = Util.float2time(mtime1)
            QMessageBox.information(
                self, "", "download time: %s\ngenerate time: %s" % (timestr1, timestr0)
            )
        else:
            QMessageBox.information(
                self, "", "atad.p, data.p 둘 중 하나 이상의 파일이 존재하지 않습니다."
            )

    def closeEvent(self, event):
        # pickledump(self.centralwidget.bookmarks, 'bookmarks.p')
        # sys.exit()
        print("Main window is closed.")
