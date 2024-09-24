from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
QCheckBox, QCompleter, QFileDialog, QGridLayout, QGroupBox,
QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QMainWindow, QMenu,
QMessageBox, QPushButton, QRadioButton, QTableWidget,
QTableWidgetItem, QVBoxLayout, QWidget)

class DipperstocksButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buyorsell = 0
        self.setStyleSheet('color:red')
    
    def mousePressEvent(self, e:QMouseEvent):
        super().mousePressEvent(e)
        if e.button() == Qt.RightButton:
            if self.buyorsell == 0:
                self.buyorsell = 1
                self.setStyleSheet('color:blue')
            else:
                self.buyorsell = 0
                self.setStyleSheet('color:red')
