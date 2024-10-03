import csv
import datetime
import os
import sys
import time
import warnings
import platform
import shutil
import urllib.request
import zipfile
from threading import Thread

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
from MainWindow import MainWindow


def main():
    # Must construct a QApplication before a QWidget
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon("icon.png"))

    print("Python " + sys.version)

    if (sys.version_info.major, sys.version_info.minor) >= (3, 7):
        pass
    else:
        QMessageBox.warning(
            None,
            "forcemonitorpy",
            "Python 버전이 3.7 미만입니다. 3.7 또는 그 이상의 버전을 사용하기를 권장합니다.",
        )

    if platform.architecture()[0] != "64bit":
        QMessageBox.warning(
            None,
            "forcemonitorpy",
            "Python이 64비트 환경이 아닙니다. 32비트 환경에서 실행할 시 MemoryError가 발생할 수 있습니다.",
        )

    mainwindow = MainWindow(app)
    mainwindow.show()
    print("Executing application...")
    app.exec_()
    print("End of application.")


if __name__ == "__main__":
    main()
