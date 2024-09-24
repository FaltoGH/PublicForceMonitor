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

class QRangeSlider(QWidget):
    rangeChanged = pyqtSignal(int, int)

    def __init__(self, maximum=999):
        super().__init__()
        qvbl = QVBoxLayout(self)
        qvbl.setSpacing(0)
        qvbl.setContentsMargins(0, 0, 0, 0)
        self.start = QSlider(1)
        self.start.setContentsMargins(0, 0, 0, 0)
        qvbl.addWidget(self.start)
        self.end = QSlider(1)
        self.end.setContentsMargins(0, 0, 0, 0)
        qvbl.addWidget(self.end)
        self.start.setMaximum(maximum)
        self.end.setMaximum(maximum)
        self.end.setValue(maximum)
        self.startvalue = 0
        self.endvalue = maximum
        self.start.valueChanged.connect(self._startvaluechanged)
        self.end.valueChanged.connect(self._endvaluechanged)
    
    def _startvaluechanged(self, value):
        self.startvalue = value
        if value >= self.endvalue:
            self.start.setValue(self.endvalue - 1)
        self.rangeChanged.emit(self.startvalue, self.endvalue)
    
    def _endvaluechanged(self, value):
        self.endvalue = value
        if value <= self.startvalue:
            self.end.setValue(self.startvalue + 1)
        self.rangeChanged.emit(self.startvalue, self.endvalue)
    
    def setMaximum(self, maximum):
        self.start.setMaximum(maximum)
        self.end.setMaximum(maximum)
