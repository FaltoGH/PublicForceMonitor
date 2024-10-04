import math
import typing

from Global import i18n
from RightPushButton import RightPushButton


def _index(lis: list, value: typing.Any) -> int:
    """
    Return first index of value.

    Returns -1 if the value is not present.
    """
    try:
        return lis.index(value)
    except ValueError:
        return -1


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
                    ranking = _index(top, todayv)  # -1,0,1,2
                    if ranking >= 0:
                        scoreboard[code] = ranking + (
                            1 - math.log10(todayv) / 10
                            if self.mode == 1
                            else math.log10(todayv) / 10
                        )
        self.centralwidget.qcb_autobookmark_check_or_not(scoreboard)
        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1])
        self.centralwidget.scoreboard2list(scoreboard)

    def rightclicked(self):
        if self.mode == 0:
            self.mode1()
        else:
            self.mode0()
