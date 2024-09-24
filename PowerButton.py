from PyQt5 import QtGui
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import Qt, pyqtSignal, QEventLoop
from PyQt5.QtGui import QColor, QCursor, QIcon, QMouseEvent
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
QCheckBox, QCompleter, QDoubleSpinBox, QFileDialog, QGridLayout, QGroupBox,
QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QMainWindow, QMenu,
QMessageBox, QPushButton, QRadioButton, QSlider, QTableWidget,
QTableWidgetItem, QVBoxLayout, QWidget)

class PowerButton(QRadioButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mode = 0
    
    def mousePressEvent(self, e:QMouseEvent):
        super().mousePressEvent(e)
        if e.button() == Qt.RightButton:
            if self.mode == 0:
                self.mode = 1
                self.setStyleSheet('color: red')
                self.setText('영향력+')
            elif self.mode == 1:
                self.mode = -1
                self.setStyleSheet('color: blue')
                self.setText('영향력-')
            else:
                self.mode = 0
                self.setStyleSheet('')
                self.setText('영향력')