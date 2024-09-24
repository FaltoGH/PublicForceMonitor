from RightPushButton import RightPushButton


class CrossStocksButton(RightPushButton):
    def __init__(self, centralwidget):
        super().__init__()
        self.clicked.connect(centralwidget.qpb_crossstocks_clicked)
        self.mode0()

    def mode0(self):
        self.setText('Cross Stocks')
        self.mode = 0
        self.setStyleSheet('color: red')
        self.setToolTip('마지막 날에 평균매수단가가 평균매도단가를 넘은 주식')

    def mode1(self):
        self.setText('Cross Stocks')
        self.mode = 1
        self.setStyleSheet('color: blue')
        self.setToolTip('마지막 날에 평균매도단가가 평균매수단가를 넘은 주식')

    def rightclicked(self):
        if self.mode == 0:
            self.mode1()
        else:
            self.mode0()