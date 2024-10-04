import math

from Global import i18n
from RightPushButton import RightPushButton


class VolumeButton(RightPushButton):
    def __init__(self, centralwidget):
        super().__init__()
        self.centralwidget = centralwidget
        self.mode = 1
        """1: Big volume, 0: Small volume"""
        self.mode1()

    def mode1(self):
        self.setText(i18n[8])
        self.setStyleSheet("color: red")
        self.setToolTip("큰 거래량 소팅")
        self.mode = 1

    def mode0(self):
        self.setText(i18n[9])
        self.setStyleSheet("color: blue")
        self.setToolTip("작은 거래량 소팅")
        self.mode = 0

    def _clicked(self):
        scoreboard = {}
        for code in self.centralwidget.data:
            chartrows = list(self.centralwidget.data[code][4].values())[
                self.centralwidget.get_slice_for_code(code)
            ]
            if len(chartrows) >= 10 and chartrows[-1][1] > 0:
                listVolume = [x[1] for x in chartrows if x[1] > 0]
                if len(listVolume) >= 5:
                    todayv = listVolume[-1]
                    listVolume.sort(reverse=self.mode == 1)
                    top = listVolume[:3]
                    if self.mode == 1:
                        if todayv >= top[-1]:
                            ranking = top.index(todayv)#0,1,2
                            log10todayv = math.log(todayv, 10)
                            score = ranking + (1 - log10todayv / 10)
                            scoreboard[code] = score
                    else:
                        if todayv <= top[-1]:
                            ranking = top.index(todayv)#0,1,2
                            log10todayv = math.log(todayv, 10)
                            score = ranking + log10todayv / 10
                            scoreboard[code] = score
        self.centralwidget.qcb_autobookmark_check_or_not(scoreboard)
        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1])
        self.centralwidget.scoreboard2list(scoreboard)

    def rightclicked(self):
        if self.mode == 0:
            self.mode1()
        else:
            self.mode0()
