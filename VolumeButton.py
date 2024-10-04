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
        centralwidget = self.centralwidget
        data = centralwidget.data
        arrslice = centralwidget.arrslice
        mode = self.mode

        scoreboard = {}

        for code in data:
            chartrows = list(data[code][4].values())
            arrslice = centralwidget.get_slice_for_code(code)
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
            if mode == 1:
                arrv.sort(reverse=True)
                top = arrv[:3]
                if todayv < top[-1]:
                    continue
                ranking = top.index(todayv)
                log10todayv = math.log(todayv, 10)
                score = ranking + (1 - log10todayv / 10)
                scoreboard[code] = score
            else:
                arrv.sort()
                top = arrv[:3]
                if todayv > top[-1]:
                    continue
                ranking = top.index(todayv)
                log10todayv = math.log(todayv, 10)
                score = ranking + log10todayv / 10
                scoreboard[code] = score

        centralwidget.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1])
        centralwidget.scoreboard2list(scoreboard)

    def rightclicked(self):
        if self.mode == 0:
            self.mode1()
        else:
            self.mode0()
