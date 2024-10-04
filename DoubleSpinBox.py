from PyQt5 import QtGui
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import Qt, pyqtSignal, QEventLoop
from PyQt5.QtGui import QColor, QCursor, QIcon, QMouseEvent
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QCheckBox,
    QCompleter,
    QDoubleSpinBox,
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
    QSlider,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class DoubleSpinBox(QDoubleSpinBox):

    # do not move this line into __init__!
    # it will cause error!
    returnPressed = pyqtSignal()

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, e: QtGui.QKeyEvent) -> None:
        if e.key() == 16777220:
            self.returnPressed.emit()
        return super().keyPressEvent(e)
