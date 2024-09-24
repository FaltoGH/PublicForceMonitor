from Global import generate_new_arrslice
from RightPushButton import RightPushButton


class MountainButton(RightPushButton):
    def __init__(self, centralwidget):
        super().__init__()
        self.setText('↗ Mountain')
        self.mode = 'up'
        self.setStyleSheet('color: red')
        self.setToolTip('평균단가의 변화율을 비교한다.')
        self.centralwidget = centralwidget

    def _clicked(self):
        centralwidget = self.centralwidget
        nvst = centralwidget.investor
        atad = centralwidget.atad
        arrslice = centralwidget.arrslice
        mode = self.mode

        scoreboard = {}

        for code in atad:
            buy = atad[code][0][nvst][0]
            arrslice = generate_new_arrslice(buy, centralwidget.arrslice, centralwidget.maxlen)
            buy = buy[arrslice]
            if len(buy) < 2:
                continue

            sell = atad[code][0][nvst][1][arrslice]

            if mode == 'up':
                if buy[-1] <= buy[0]:
                    continue
            else:
                if sell[-1] >= sell[0]:
                    continue

            try:
                bmax, bmin, smax, smin = max(buy), min(buy), max(sell), min(sell)
            except ValueError as e:
                if e.args[0] == 'max() arg is an empty sequence':
                    continue
                else:
                    raise e

            try:
                bs = (bmax - bmin) / (bmax + bmin)
                ss = (smax - smin) / (smax + smin)
            except ZeroDivisionError:
                continue
            if mode == 'up':
                f = bs - ss
            else:
                f = ss - bs
            if f > 0:
                scoreboard[code] = f * 100

        centralwidget.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x:x[1], reverse=True)
        centralwidget.scoreboard2list(scoreboard)

    def rightclicked(self):
        if self.mode == 'up':
            self.mode = 'down'
            self.setStyleSheet('color: blue')
            self.setText('↘ Mountain')
        else:
            self.mode = 'up'
            self.setStyleSheet('color: red')
            self.setText('↗ Mountain')