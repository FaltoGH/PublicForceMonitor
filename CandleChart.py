import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from PyQt5.QtWidgets import QScrollBar, QSlider, QGridLayout, QWidget

class CandleChart(QWidget):
    def __init__(self):
        super().__init__()
        self.isfirst = True
        self.wasmaximum = True
        figure = plt.figure()
        canvas = FigureCanvasQTAgg(figure)
        ax = figure.add_subplot(111)

        qsb_scroll = QScrollBar(1)
        qsb_scroll.valueChanged.connect(self.qsb_scroll_valuechanged)
        qsb_scroll.setMaximum(0)
        qsb_scroll.setPageStep(99)

        qs_range = QSlider(1)
        qs_range.setMaximumWidth(99)
        qs_range.setMinimum(2)
        qs_range.setEnabled(False)
        
        qs_range.valueChanged.connect(self.qs_range_valuechanged)
     
        layout = QGridLayout(self)
        layout.addWidget(canvas, 0, 0, 1, 2)
        layout.addWidget(qsb_scroll, 1, 0)
        layout.addWidget(qs_range, 1, 1)

        self.loc = 0
        self.ax = ax
        self.canvas = canvas

        self.qs_range_value = 1
        self.qs_range_value:int

        self.qsb_scroll = qsb_scroll
        self.qs_range = qs_range

        self.low = []
        self.low:list

        self.high = []
        self.high:list

    def setlenlist(self, lenlist):
        self.wasmaximum = self.qs_range.value() == self.qs_range.maximum()
        # main
        self.qs_range.setMaximum(lenlist)
        self.qs_range.setEnabled(True)
        self.lenlist = lenlist
        if self.isfirst:
            self.isfirst = False
            self.qs_range.setValue(self.qs_range.maximum())
        elif self.wasmaximum:
            self.qs_range.setValue(self.qs_range.maximum())

    def qs_range_valuechanged(self, value:int):
        low, high = self.low, self.high
        minprice = min(low[0:value])
        maxprice = max(high[0:value])
        self.qs_range_value = value
        self.ax.set_xlim(-2, value+1)
        self.ax.set_ylim(minprice*0.98, maxprice*1.02)
        self.qsb_scroll.setMaximum(self.lenlist-value)
        self.qsb_scroll.setValue(self.qsb_scroll.maximum())
        self.canvas.draw()

    def qsb_scroll_valuechanged(self, value:int):
        lows=self.low[value:value+self.qs_range_value]
        minprice = min(lows) if len(lows)>0 else 1
        highs=self.high[value:value+self.qs_range_value]
        maxprice = max(highs) if len(highs)>0 else 1
        self.ax.set_xlim(value-2, value+self.qs_range_value+1)
        self.ax.set_ylim(minprice*0.98, maxprice*1.02)
        self.canvas.draw()
