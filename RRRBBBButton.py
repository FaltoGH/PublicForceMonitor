from Global import i18n
from RightPushButton import RightPushButton


class RRRBBBButton(RightPushButton):
    def __init__(self, centralwidget):
        super().__init__()
        self.clicked.connect(centralwidget.qpb_redredred_clicked)
        self.mode0()

    def mode0(self):
        self.setText(i18n[11])
        self.mode = 0
        self.setStyleSheet('color: red')
        self.setToolTip('영향력 빨간 거')

    def mode1(self):
        self.setText(i18n[12])
        self.mode = 1
        self.setStyleSheet('color: blue')
        self.setToolTip('영향력 파란 거')

    def rightclicked(self):
        if self.mode == 0:
            self.mode1()
        else:
            self.mode0()