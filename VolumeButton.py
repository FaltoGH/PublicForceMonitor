import math

from Constants import Constants
from Global import i18n
from RightPushButton import RightPushButton


class VolumeButton(RightPushButton):
    def __init__(self, centralwidget):
        super().__init__()
        self.centralwidget = centralwidget
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
        mode = self.mode

        scoreboard = {}

        for code in self.centralwidget.data:
            chartrows = list(self.centralwidget.data[code][4].values())
            arrslice = self.centralwidget.get_slice_for_code(code)
            chartrows = chartrows[arrslice]
            if chartrows[-1][1] == 0:
                continue
            if len(chartrows) < 10:
                continue
            arrv = []
            for chartrow in chartrows:
                v = chartrow[1]
                if v > 0:
                    arrv.append(v)
            if len(arrv) < 5:
                continue
            todayv = arrv[-1]
            arrv.sort(reverse=mode==1)
            top = arrv[:3]
            if mode == 1:
                if todayv < top[-1]:
                    continue
                ranking = top.index(todayv)
                log10todayv = math.log(todayv, 10)
                score = ranking + (1 - log10todayv / 10)
                scoreboard[code] = score
            else:
                if todayv > top[-1]:
                    continue
                ranking = top.index(todayv)
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
