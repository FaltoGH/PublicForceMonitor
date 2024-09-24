from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QApplication,
QCheckBox, QCompleter, QFileDialog, QGridLayout, QGroupBox,
QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QMainWindow, QMenu,
QMessageBox, QPushButton, QRadioButton, QVBoxLayout, QWidget,
QTableWidgetItem, QTableWidget)

class CodeNameDateScoreTableWidget(QTableWidget):
    def __init__(self, centralwidget):
        super().__init__(centralwidget)
        self.centralwidget = centralwidget
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['Code', 'Name', 'Date', 'Score'])
        self.verticalHeader().hide()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setMinimumWidth(333)

    def setItem(self, row: int, column: int, item: QTableWidgetItem) -> None:
        self.centralwidget.savestackcount = 0
        return super().setItem(row, column, item)