from PyQt5 import QtGui
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import Qt, pyqtSignal, QEventLoop
from PyQt5.QtGui import QColor, QCursor, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAbstractItemView, QAction,
QApplication, QCheckBox, QCompleter, QDoubleSpinBox,
QFileDialog, QGridLayout, QGroupBox, QHBoxLayout,
QInputDialog, QLabel, QLineEdit, QListWidget,
QMainWindow, QMenu, QMessageBox, QPushButton,
QRadioButton, QSlider, QTableWidget,
QTableWidgetItem, QVBoxLayout, QWidget)

class CodeNameDateScoreTableWidgetItem(QTableWidgetItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.code = None
        self.name = None
        self.date = None
        self.score = None
        self.hline = None
        self.vline = None
        self.memo = None
