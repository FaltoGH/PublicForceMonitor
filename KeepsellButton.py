from PyQt5 import QtGui
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import Qt, pyqtSignal, QEventLoop
from PyQt5.QtGui import QColor, QCursor, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
QCheckBox, QCompleter, QDoubleSpinBox, QFileDialog, QGridLayout, QGroupBox,
QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QMainWindow, QMenu,
QMessageBox, QPushButton, QRadioButton, QSlider, QTableWidget,
QTableWidgetItem, QVBoxLayout, QWidget)

class KeepsellButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.a = 0
    
    def mousePressEvent(self, e:QMouseEvent):
        super().mousePressEvent(e)
        if e.button() == Qt.RightButton:
            self.a ^= 1
            if self.a == 0:
                self.setText('Keepsell Stocks ▼')
            elif self.a == 1:
                self.setText('Keepsell Stocks ▲')
