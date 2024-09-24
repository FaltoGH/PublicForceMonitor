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

class RightPushButton(QPushButton):
    """
    Provides abstract class of right mouse click button.

    clicked event is connected in self._clicked()

    right click event is connected in self.rightclicked()
    """
    def __init__(self):
        super().__init__()
        self.clicked.connect(self._clicked)
    
    def _clicked(self)->None:
        pass

    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        super().mousePressEvent(e)
        if e.button() == Qt.RightButton:
            self.rightclicked()
    
    def rightclicked(self)->None:
        pass
