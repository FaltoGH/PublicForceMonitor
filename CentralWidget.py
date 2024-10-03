import csv
import datetime
import os
import sys
import time
import warnings
import platform
import shutil
import urllib.request
import zipfile
from threading import Thread

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QCursor, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QCheckBox,
    QCompleter,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMenu,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from CandleChart import CandleChart
from ClosestocksButton import ClosestocksButton
from CodeNameDateScoreTableWidget import CodeNameDateScoreTableWidget
from CodeNameDateScoreTableWidgetItem import CodeNameDateScoreTableWidgetItem
from Constants import Constants
from CrossStocksButton import CrossStocksButton
from DipperstocksButton import DipperstocksButton
from DoubleSpinBox import DoubleSpinBox
import FeatureFlag
from KeepbuyButton import KeepbuyButton
from KeepsellButton import KeepsellButton
from MountainButton import MountainButton
from PowerButton import PowerButton
from QRangeSlider import QRangeSlider
from RRRBBBButton import RRRBBBButton
from Util import Util
from Global import (
    i18n,
    generate_new_arrslice,
    csvload,
    weight,
    power,
    direction,
    slice100,
    generatenow,
    writeintereststock,
    gen_arrsign,
    keepbuy,
    keepbuy2,
    parse,
)
import Global
from VolumeButton import VolumeButton

# Disable DeprecationWarning temporarily.
# Idea from https://stackoverflow.com/a/50519680
_2024_0004 = warnings.warn
warnings.warn = lambda *args, **kwargs: None
import mpl_finance

warnings.warn = _2024_0004
del _2024_0004

_BOOKMARK_COLOR = QColor(0x99FF99)


class CentralWidget(QWidget):
    def __init__(self, mainwindow, app: QApplication):
        super().__init__(mainwindow)
        self.mainwindow = mainwindow
        self.app = app
        self.investor = 0
        self.info = 0
        self.crtstockcode = "005930"
        self.resultcodelist = []
        self.block = False
        self.isatadreceived = False
        self.selecteditem = None
        self.savestackcount = 0

        self.arrslice: slice = slice(0)
        "Indicates the slice of selected date range."

        # try:
        #     self.bookmarks = pickleload('bookmarks.p')
        # except FileNotFoundError:
        self.bookmarks = []

        self._design()
        self._connect()

    def _design(self):
        plt.rc("font", family="Malgun Gothic")
        matplotlib.rcParams["axes.unicode_minus"] = False
        candlechart = CandleChart()
        self.canvas = candlechart.canvas
        self.ax = candlechart.ax
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax2 = self.ax.twinx()
        self.ax2.set_yticks([])
        self.qle_stock = QLineEdit("")
        self.qle_stock.setPlaceholderText("삼성전자")
        self.qgb_directsearch = QGroupBox(i18n[15])
        self.q_investor = []
        for invname in [
            "개인투자자",
            "외국인투자자",
            "기관계",
            "금융투자",
            "보험",
            "투신",
            "기타금융",
            "은행",
            "연기금등",
            "사모펀드",
            "국가",
            "기타법인",
            "내외국인",
        ]:
            self.q_investor.append(QRadioButton(invname))
        self.q_investor[0].setChecked(True)
        self.q_info = []
        for infoname in [
            "평균거래단가",
            "보유비중증감",
            "영향력",
            "방향",
            "RS",
            "Bollinger",
        ]:
            if infoname == "영향력":
                self.powerbutton = PowerButton("영향력")
                self.q_info.append(self.powerbutton)
            else:
                self.q_info.append(QRadioButton(infoname))
        self.q_info[0].setChecked(True)
        self.qpb_datafromkiwoom = QPushButton(i18n[28])
        self.qpb_analyzedata = QPushButton(i18n[0])
        self.qpb_loadatad = QPushButton(i18n[1])
        self.qgb_basiccontrol = QGroupBox(i18n[14])
        self.qlw_stocklist = CodeNameDateScoreTableWidget(self)
        self.qgb_filterselect = QGroupBox(i18n[13])
        self.qgb_infoselect = QGroupBox("Info Select")
        self.qpb_droppedstocks = QPushButton("Dropped Stocks")
        self.qpb_droppedstocks.setToolTip(
            "마지막 날의 평균매수단가가 그 전 날보다 떨어진 주식"
        )
        self.qpb_expensivestocks = QPushButton(i18n[3])
        self.qpb_expensivestocks.setToolTip(
            "마지막 날의 종가가 개인투자자, 외국인투자자, 기관계의 각 평균매수단가보다 더 큰 주식"
        )
        self.qpb_dipperstocks = DipperstocksButton("Dipper Stocks")
        self.qpb_dipperstocks.setToolTip("평균거래단가의 모양이 국자인 주식")
        self.qpb_crossstocks = CrossStocksButton(self)
        self.qpb_keepbuystocks = KeepbuyButton("%s ▼" % i18n[5])
        self.qpb_keepbuystocks.setStyleSheet("color:red")
        self.qpb_keepbuystocks.setToolTip(
            "평균매수단가가 4번 이상 내려간/올라간 주식 (최대 400개)"
        )
        self.qpb_keepsellstocks = KeepsellButton("%s ▼" % i18n[6])
        self.qpb_keepsellstocks.setStyleSheet("color:blue")
        self.qpb_keepsellstocks.setToolTip(
            "평균매도단가가 4번 이상 내려간/올라간 주식 (최대 400개)"
        )
        self.qpb_closestocks = ClosestocksButton("Close Stocks")
        self.qpb_closestocks.setStyleSheet("color:red")
        self.qpb_closestocks.setToolTip("평균거래단가의 변동폭이 좁은 주식")
        self.qcb_autobookmark = QCheckBox(i18n[10])
        self.qgb_particularstocks = QGroupBox(i18n[16])

        self.qlw_bookmarks = QListWidget()
        self.bookmarks.sort()
        self.qlw_bookmarks.setMinimumWidth(60)
        self.qpb_savedir = QPushButton("Open Save Directory")
        self.menu = QMenu()
        self.qpb_ascendingsearch = QPushButton(i18n[19])
        self.qpb_descendingsearch = QPushButton(i18n[20])
        self.qgb_autosearch = QGroupBox(i18n[17])
        self.qpb_save = QPushButton(i18n[21])
        self.qpb_del = QPushButton(i18n[22])
        self.ql_stockcount = QLabel("0 result")
        self.qgb_graph = QGroupBox("Graph")
        self.qgb_graph.setMinimumHeight(400)
        self.qgb_bookmarks = QGroupBox(f"{i18n[18]} ({len(self.bookmarks)})")
        self.qpb_savebookmarks = QPushButton(i18n[23])
        self.qpb_delallbookmarks = QPushButton(i18n[24])
        self.qpb_importcsv = QPushButton(i18n[25])

        self.qwidgets_dataneeded = [
            self.qgb_filterselect,
            self.qgb_infoselect,
            self.qgb_particularstocks,
            self.qgb_autosearch,
            self.qgb_directsearch,
            self.qgb_bookmarks,
        ]
        for qwidget_dataneeded in self.qwidgets_dataneeded:
            qwidget_dataneeded.setEnabled(False)

        qbl = QVBoxLayout()
        qbl.addWidget(self.ql_stockcount)
        qbl.addWidget(self.qlw_stocklist)
        qbl.addWidget(self.qpb_ascendingsearch)
        qbl.addWidget(self.qpb_descendingsearch)
        qbl.addWidget(self.qpb_save)
        qbl.addWidget(self.qpb_del)
        self.qgb_autosearch.setLayout(qbl)

        qbl = QVBoxLayout()
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_droppedstocks)
        qbl.addWidget(self.qpb_expensivestocks)
        self.qpb_cheapstocks = QPushButton(i18n[4])
        self.qpb_cheapstocks.setToolTip("싼 주식")
        self.qpb_cheapstocks.clicked.connect(self.qpb_cheapstocks_clicked)
        qbl.addWidget(self.qpb_cheapstocks)
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_dipperstocks)
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_crossstocks)
        qbl.addWidget(self.qpb_keepbuystocks)
        qbl.addWidget(self.qpb_keepsellstocks)
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_closestocks)
        self.qpb_spikestocks = QPushButton("Spike Stocks")
        self.qpb_spikestocks.clicked.connect(self.qpb_spikestocks_clicked)
        self.qpb_spikestocks.setToolTip("보유비중증감의 폭이 급격히 늘어난 주식")
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_spikestocks)
        self.qpb_redmountain = MountainButton(self)
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_redmountain)
        self.qpb_boutique = QPushButton(i18n[7])
        self.qpb_boutique.clicked.connect(self.qpb_boutique_clicked)
        self.qpb_boutique.setToolTip(
            "선택한 세력이 갑자기 영향력이 압도적으로 커진 주식"
        )
        self.qpb_bollinger = QPushButton("Bollinger")
        self.qpb_bollinger.clicked.connect(self.qpb_bollinger_clicked)
        self.qpb_bollinger.setToolTip("Bollinger Buy Sign")
        qbl.addWidget(self.qpb_boutique)
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_bollinger)
        self.qdsb_level = DoubleSpinBox()
        qbl.addWidget(self.qdsb_level)
        self.qpb_volume = VolumeButton(self)
        qbl.addWidget(self.qpb_volume)
        qbl.addWidget(self.qcb_autobookmark)
        self.qpb_redredred = RRRBBBButton(self)
        qbl.addWidget(self.qpb_redredred)
        self.qgb_particularstocks.setLayout(qbl)

        qbl = QVBoxLayout()
        qbl.addWidget(self.qle_stock)
        self.qpb_addstock2bookmark = QPushButton(i18n[2])
        self.qpb_addstock2bookmark.clicked.connect(self.qpb_addstock2bookmark_clicked)
        qbl.addWidget(self.qpb_addstock2bookmark)
        self.qgb_directsearch.setLayout(qbl)

        qbl = QHBoxLayout()
        qbl.addWidget(self.qpb_datafromkiwoom)
        qbl.addWidget(self.qpb_analyzedata)
        qbl.addWidget(self.qpb_loadatad)
        if FeatureFlag.PRO:
            qbl.addWidget(self.qpb_savedir)
        self.qgb_basiccontrol.setLayout(qbl)

        qbl = QVBoxLayout()
        qbl.addWidget(self.qlw_bookmarks)
        qbl.addWidget(self.qpb_savebookmarks)
        qbl.addWidget(self.qpb_delallbookmarks)
        qbl.addWidget(self.qpb_importcsv)
        self.qpb_export_codelist = QPushButton(i18n[26])
        qbl.addWidget(self.qpb_export_codelist)
        self.qpb_analyze_bookmarks = QPushButton(i18n[27])
        qbl.addWidget(self.qpb_analyze_bookmarks)
        self.qgb_bookmarks.setLayout(qbl)

        qbl = QHBoxLayout()
        for qwidget_inv in self.q_investor:
            qbl.addWidget(qwidget_inv)
        self.qgb_filterselect.setLayout(qbl)

        qbl = QHBoxLayout()
        for qwidget_info in self.q_info:
            qbl.addWidget(qwidget_info)
        self.qgb_infoselect.setLayout(qbl)

        qbl = QHBoxLayout()
        qbl.addWidget(candlechart)
        self.qgb_graph.setLayout(qbl)

        qvbl = QVBoxLayout()
        qvbl.addWidget(self.qgb_directsearch)
        qvbl.addWidget(self.qgb_particularstocks)

        a99 = QGridLayout()
        a99.addWidget(self.qgb_graph, 0, 0)
        a99.addWidget(self.qgb_filterselect, 1, 0)
        a99.addWidget(self.qgb_infoselect, 2, 0)
        a99.addWidget(self.qgb_basiccontrol, 3, 0)

        a99.addLayout(qvbl, 0, 1, 4, 1)

        a99.addWidget(self.qgb_autosearch, 0, 2, 4, 1)

        a99.addWidget(self.qgb_bookmarks, 0, 3, 4, 1)

        qhbl = QHBoxLayout()

        self.qs_timeleaper = QRangeSlider()
        qhbl.addWidget(self.qs_timeleaper)
        self.ql_timeleaper = QLabel("1970-01-02\n~1970-01-03")
        qhbl.addWidget(self.ql_timeleaper)
        a99.addLayout(qhbl, 4, 0, 1, 4)

        self.setLayout(a99)

        self.candlechart = candlechart

    def _connect(self):

        for x in self.q_investor:
            x.clicked.connect(self.q_investor_clicked)
        for x in self.q_info:
            x.clicked.connect(self.q_info_clicked)
        self.qle_stock.returnPressed.connect(self.qle_stock_returnPressed)
        self.qlw_stocklist.currentItemChanged.connect(
            self.qlw_stocklist_currentItemChanged
        )
        self.qlw_stocklist.customContextMenuRequested.connect(self.showmenu)
        self.qpb_datafromkiwoom.clicked.connect(self.qpb_datafromkiwoom_clicked)
        self.qpb_analyzedata.clicked.connect(self.qpb_analyzedata_clicked)
        self.qpb_loadatad.clicked.connect(self.qpb_loadatad_clicked)
        self.qpb_droppedstocks.clicked.connect(self.qpb_droppedstocks_clicked)
        self.qpb_crossstocks.clicked.connect(self.qpb_crossstocks_clicked)
        self.qpb_keepbuystocks.clicked.connect(self.qpb_keepbuystocks_clicked)
        self.qpb_keepsellstocks.clicked.connect(self.qpb_keepsellstocks_clicked)
        self.qpb_save.clicked.connect(self.qpb_save_clicked)
        self.qpb_del.clicked.connect(self.qpb_del_clicked)
        self.qpb_expensivestocks.clicked.connect(self.qpb_expensivestocks_clicked)
        self.qpb_dipperstocks.clicked.connect(self.qpb_dipperstocks_clicked)
        self.qpb_savedir.clicked.connect(self.qpb_savedir_clicked)
        self.qpb_ascendingsearch.clicked.connect(self.qpb_ascendingsearch_clicked)
        self.qpb_descendingsearch.clicked.connect(self.qpb_descendingsearch_clicked)
        self.qlw_bookmarks.currentItemChanged.connect(
            self.qlw_bookmarks_currentItemChanged
        )
        self.qpb_savebookmarks.clicked.connect(self.qpb_savebookmarks_clicked)
        self.qpb_delallbookmarks.clicked.connect(self.qpb_delallbookmarks_clicked)
        self.qpb_closestocks.clicked.connect(self.qpb_closestocks_clicked)
        self.qpb_importcsv.clicked.connect(self.qpb_importcsv_clicked)
        self.qs_timeleaper.rangeChanged.connect(self.qs_timeleaper_valuechanged)
        self.qdsb_level.returnPressed.connect(self.qdsb_level_returnpressed)
        for x in ["qpb_analyze_bookmarks", "qpb_export_codelist"]:
            exec("self.%s.clicked.connect(self.%s_clicked)" % (x, x))

    def qpb_addstock2bookmark_clicked(self):
        code = self.crtstockcode
        if code not in self.bookmarks:
            self.bookmarks.append(code)
        self.qlw_bookmarks_showlist()

    def qpb_analyze_bookmarks_clicked(self):
        openfilenames = QFileDialog.getOpenFileNames(
            directory="C:\\KiwoomHero4\\temp", filter="*.csv"
        )[0]
        if openfilenames:
            scoreboard = {}
            for openfilename in openfilenames:
                rows = csvload(openfilename)[1:]
                for row in rows:
                    code = row[0][1:]
                    if code in scoreboard:
                        scoreboard[code] += 1
                    else:
                        scoreboard[code] = 0
            self.scoreboard2list(
                sorted(list(scoreboard.items()), key=lambda x: x[1], reverse=1)
            )

    def download(self) -> None:
        """
        데이터를 다운받아 data.p에 피클 형태로 저장합니다.
        """
        self.mainwindow.statusbar.showMessage("Downloading data from server...")
        urllib.request.urlretrieve(
            "http://api.motrader.co.kr:25565/data.zip", "data.zip"
        )
        self.mainwindow.statusbar.showMessage("Download done! Extracting zip file...")

        with zipfile.ZipFile("data.zip") as f:
            f.extract("data.p")

        try:
            os.remove("data.zip")
        except:
            pass

        self.mainwindow.statusbar.showMessage("Download done!")
        self.setEnabled(True)

    def qpb_datafromkiwoom_clicked(self):
        reply = QMessageBox.question(self, i18n[28], "새로운 데이터를 받을까요?")
        if reply == QMessageBox.Yes:
            self.setEnabled(False)
            Thread(target=self.download, daemon=True).start()

    def convertcode2name(self, code):
        return self.data[code][Constants.K_NAME]

    def analyze(self):
        self.setEnabled(False)

        data = Util.pickleload(Constants.PATH_DATAP)
        codelist = list(data.keys())
        codelist.remove("000000")
        atad = {}

        start_time = time.time()

        for index, code in enumerate(codelist):
            code: str

            buyrows = list(data[code][Constants.K_BUY].values())
            sellrows = list(data[code][Constants.K_SELL].values())
            chartrows = list(data[code][4].values())
            atad_code = {}
            atad_code[0] = Util.price(chartrows, buyrows, sellrows)
            atad_code[1] = weight(buyrows, sellrows)
            atad_code[2] = power(buyrows, sellrows)
            atad_code[3] = direction(buyrows, sellrows)
            atad[code] = atad_code

            msg = Util.get_progress_msg(index, len(codelist), start_time, code)
            self.mainwindow.statusbar.showMessage(msg)
            self.app.processEvents()

        Util.pickledump(atad, Constants.PATH_ATADP)

        self.setEnabled(True)
        QMessageBox.information(self, "", "새로운 분석 데이터를 생성했습니다.")
        self.mainwindow.statusbar.showMessage("분석 데이터 생성 완료")

    def q_investor_clicked(self):
        for i, x in enumerate(self.q_investor):
            if x.isChecked():
                self.investor = i
                break
        else:
            raise Exception

        self.qpb_drawchart_clicked2()

    def q_info_clicked(self):
        for i, x in enumerate(self.q_info):
            if x.isChecked():
                self.info = i
                break
        else:
            raise Exception
        self.qpb_drawchart_clicked2()

    def qs_timeleaper_valuechanged(self, startvalue, endvalue):
        if self.isatadreceived:
            self.startdateint = startvalue
            self.enddateint = endvalue
            arrdate = list(self.data["005930"][4].keys())
            lenarrdate = len(arrdate)
            self.qs_timeleaper.setMaximum(lenarrdate - 1)
            startdate0 = arrdate[startvalue]
            try:
                enddate0 = arrdate[endvalue]
            except IndexError:
                return
            startdate1 = datetime.datetime.strptime(startdate0, "%Y%m%d").strftime(
                "%Y-%m-%d"
            )
            enddate1 = datetime.datetime.strptime(enddate0, "%Y%m%d").strftime(
                "%Y-%m-%d"
            )
            self.ql_timeleaper.setText(f"{startdate1}\n~{enddate1}")
            self.arrslice = slice(startvalue, endvalue + 1)

    def atadreceivedevent(self):
        self.data = Util.pickleload(Constants.PATH_DATAP)
        self.kospi = self.data["000000"][Constants.M_KOSPI]
        self.kosdaq = self.data["000000"][Constants.M_KOSDAQ]
        del self.data["000000"]

        for qwidget_dataneeded in self.qwidgets_dataneeded:
            qwidget_dataneeded.setEnabled(True)
        bookmark_display = [
            f"{x},{self.data[x][Constants.K_NAME]}" for x in self.bookmarks
        ]
        self.qlw_bookmarks.clear()
        self.qlw_bookmarks.addItems(bookmark_display)
        self.name2code = {}
        self.codelist = []
        self.namelist = []
        for key, value in self.data.items():
            self.name2code[value[Constants.K_NAME]] = key
            self.codelist.append(key)
            self.namelist.append(value[Constants.K_NAME])

        completer = QCompleter(self.namelist)
        self.qle_stock.setCompleter(completer)

        self.arrslice = slice(0, 600)

        self.isatadreceived = True

    def qpb_analyzedata_clicked(self):
        if os.path.exists(Constants.PATH_DATAP):
            reply = QMessageBox.question(
                self, "", "새로운 분석 데이터를 생성할까요? (예상 시간: 10초)"
            )
            if reply == QMessageBox.Yes:
                self.analyze()
        else:
            QMessageBox.warning(
                self, "", "먼저 키움으로부터 새로운 데이터를 받아야 합니다."
            )

    def qpb_loadatad_clicked(self):
        if os.path.exists(Constants.PATH_ATADP):
            reply = QMessageBox.question(
                self, "", "과거에 생성된 분석 데이터를 불러올까요? (예상 시간: 2초)"
            )
            if reply == QMessageBox.Yes:
                self.atad = Util.pickleload(Constants.PATH_ATADP)
                timestr = Util.float2time(os.path.getmtime(Constants.PATH_ATADP))
                self.atadreceivedevent()
                QMessageBox.information(
                    self, "", f"{timestr}에 생성된 분석 데이터를 불러왔습니다."
                )
        else:
            QMessageBox.warning(self, "", "먼저 새로운 분석 데이터를 생성해야 합니다.")

    def qpb_delallbookmarks_clicked(self):
        if len(self.bookmarks):
            reply = QMessageBox.question(
                self,
                "",
                "북마크한 종목을 모두 삭제할까요? (검색 결과도 같이 없어집니다!)",
            )
            if reply == QMessageBox.Yes:
                self.bookmarks.clear()
                self.qlw_bookmarks_showlist()
                self.resultcodelist.clear()
                self.qlw_stocklist.clearContents()
                self.ql_stockcount_showlen()
        else:
            QMessageBox.warning(self, "", "삭제할 종목이 없습니다!")

    def qpb_savebookmarks_clicked(self):
        if not self.bookmarks:
            QMessageBox.warning(self, "", "저장할 종목이 없습니다!")
            return

        reply = QMessageBox.question(self, "", "북마크한 종목을 저장할까요?")
        if reply == QMessageBox.Yes:
            codes = self.bookmarks
            code100s = slice100(codes)
            now = generatenow()
            for index, code100 in enumerate(code100s):
                filename = f"bookmark{now}{index}"
                filedir = f"{Constants.SAVEDIR}\\{filename}.csv"
                writeintereststock(filedir, code100)
            QMessageBox.information(
                self, "", f"{len(codes)}개의 북마크한 종목을 저장했습니다."
            )

    def qpb_export_codelist_clicked(self):
        if not self.bookmarks:
            QMessageBox.warning(self, "", "수출할 북마크가 없다.")
            return

        codelist = self.bookmarks
        filename, answer = QInputDialog.getText(
            self, "QInputDialog", "어떤 파일명으로 저장할 건가요?"
        )
        if not answer:
            return

        filedir = f"{Constants.SAVEDIR}\\{filename}.csv"
        writeintereststock(filedir, codelist)
        QMessageBox.information(
            self, "", f"{len(codelist)}개의 북마크한 종목을 저장했습니다."
        )

    def qlw_bookmarks_currentItemChanged(self):
        if self.block:
            return

        def f():
            time.sleep(1e-323)
            item = self.qlw_bookmarks.currentItem()
            if not item:
                return
            self.crtstockcode = item.text().split(",")[0]
            self.qpb_drawchart_clicked2()

        Thread(target=f, daemon=True).start()

    def qle_stock_returnPressed(self):
        text = self.qle_stock.text()
        code = self.name2code.get(text)
        if code == None:
            for name in self.namelist:
                if text in name:
                    code = self.name2code[name]
                    self.qle_stock.setText(name)
                    break
            else:
                return

        self.crtstockcode = code
        self.qpb_drawchart_clicked2()

    def qpb_del_clicked(self):
        crtrow = self.qlw_stocklist.currentRow()
        if crtrow == -1:
            return
        item = self.qlw_stocklist.takeItem(crtrow, 0)
        if item == None:
            return
        code = item.code
        self.resultcodelist.remove(code)
        self.qlw_stocklist.removeRow(crtrow)
        self.ql_stockcount_showlen()

    def ql_stockcount_showlen(self):
        a0 = len(self.resultcodelist)
        r = f"{a0} results" if a0 >= 2 else f"{a0} result"
        self.ql_stockcount.setText(r)

    def get_slice_for_code(self, jmcode: str) -> slice:
        """
        일봉 차트의 전체 길이가 600일봉이 아닌 종목들을 위해
        slice를 재생성해 줍니다.
        """
        return generate_new_arrslice(len(self.data[jmcode][4]), self.arrslice)

    def qpb_drawchart_clicked2(self):  # GUI에 차트를 그리는 유일무이한 함수
        investor = self.investor
        info = self.info

        self.ax.clear()
        self.ax2.clear()

        code = self.crtstockcode

        data = self.data

        self.drawchart(self.data[code][4], self.ax)
        self.ax.set_title(f"{self.data[code][8]} ({code})")

        arrslice = self.get_slice_for_code(code)

        # 평균거래단가
        if info == 0:
            self.ax2.axis("off")
            buyarray = self.atad[code][0][investor][0]
            sellarray = self.atad[code][0][investor][1]
            self.ax.plot(buyarray)
            self.ax.plot(sellarray)
            self.ax.get_lines()[0].set_color("red")
            self.ax.get_lines()[1].set_color("blue")
            self.ax.grid()

        # 보유비중증감
        elif info == 1:
            self.ax2.axis("on")
            array = self.atad[code][1][investor]
            stock = self.data[code][7]
            array = [x / (stock * 10) for x in array]
            self.ax2.plot(array)
            self.ax2.set_ylabel("%")
            self.ax.grid()

        # 영향력
        elif info == 2:
            self.ax2.axis("on")
            array = self.atad[code][2][investor]
            self.ax2.plot(array)
            self.ax2.set_ylabel("%")
            self.ax.grid()

            if self.powerbutton.mode != 0:
                array_part = array[arrslice]
                try:
                    array_part_average = sum(array_part) / len(array_part)
                except ZeroDivisionError as e:
                    print(609, e)
                    return
                self.ax2.axhline(array_part_average, color="red", linewidth=1)
                if self.powerbutton.mode == 1:
                    array_part_max = max(array_part)
                    self.ax2.axhline(array_part_max, color="red", linewidth=1)
                elif self.powerbutton.mode == -1:
                    array_part_min = min(array_part)
                    self.ax2.axhline(array_part_min, color="red", linewidth=1)

            directionarray = self.atad[code][3][investor]
            for i in range(len(directionarray)):
                value = directionarray[i]
                x = [i - 0.5, i + 0.5]
                y = array[i]
                if value == 100:
                    color, alpha = "red", 0.5
                elif 0 < value < 100:
                    color, alpha = "orange", 0.1
                elif value == 0:
                    color, alpha = "yellow", 0.6
                elif -100 < value < 0:
                    color, alpha = "cyan", 0.1
                else:
                    color, alpha = "blue", 0.5
                self.ax2.fill_between(x, y, alpha=alpha, color=color)

        # 방향
        elif info == 3:
            self.ax2.axis("on")
            array = self.atad[code][3][investor]
            self.ax2.plot(array)
            self.ax2.axhline(0, color="#000000", linewidth=2)
            self.ax2.set_ylabel("%")
            self.ax.grid()

        # RS
        elif info == 4:
            self.ax2.axis("on")
            chartrows = list(self.data[code][4].values())
            standard = chartrows[0][0]
            array = [chartrow[0] / standard for chartrow in chartrows]

            market = self.data[code][11]
            if market == 0:
                marketrows = list(self.kospi.values())
            else:
                marketrows = list(self.kosdaq.values())

            standard = marketrows[0][0]
            marketarray = [marketrow[0] / standard for marketrow in marketrows]

            rpsarray = [(a / b * 100) for a, b in zip(array, marketarray)]

            self.ax2.plot(rpsarray)
            self.ax2.axhline(100, color="#000000", linewidth=2)
            self.ax2.set_ylabel("%")
            self.ax.grid()

        # Bollinger
        elif info == 5:
            self.ax2.axis("on")
            self.ax.grid()
            chartrows = list(data[code][4].values())[self.arrslice]
            arrsign = gen_arrsign(chartrows)

            for sign in arrsign:
                index = sign[0]
                price = chartrows[index][0]
                vline = index
                hline = price
                self.ax.axvline(arrslice.start + vline, color="black", linewidth=1)
                self.ax.axhline(hline, color="black", linewidth=1)
            self.canvas.draw()

        self.ax2.axvline(arrslice.start, color="green", linewidth=1)
        self.ax2.axvline(arrslice.stop - 1, color="green", linewidth=1)

        if (
            (self.selecteditem)
            and (info != 5)
            and (self.selecteditem.code == self.crtstockcode)
        ):
            if (self.selecteditem.memo == "onlypower") and (info == 2):
                self.ax2.axhline(self.selecteditem.hline, color="purple", linewidth=1)
            else:
                vline = self.selecteditem.vline
                hline = self.selecteditem.hline
                if vline:
                    self.ax.axvline(arrslice.start + vline, color="black", linewidth=1)
                if hline:
                    self.ax.axhline(hline, color="black", linewidth=1)

        self.candlechart.qs_range_valuechanged(self.candlechart.qs_range.value())
        self.candlechart.qsb_scroll_valuechanged(self.candlechart.qsb_scroll.value())

    def drawchart(self, chartdict: dict, ax):
        Open, High, Low, Close, Date = [], [], [], [], []
        for key, value in list(chartdict.items())[
            -len(self.data[self.crtstockcode][Constants.K_BUY]) :
        ]:
            Open.append(value[3])
            High.append(value[4])
            Low.append(value[5])
            Close.append(value[0])
            Date.append(key)

        date_len = len(Date)
        self.chart_len = date_len

        self.candlechart.high = High
        self.candlechart.low = Low
        self.candlechart.setlenlist(self.chart_len)

        day_list = []
        name_list = []
        lendate = len(Date)
        for i, day in enumerate(Date):
            if i % (int(lendate / 19) + 1) == 0:
                day_list.append(i)
                name_list.append(str(day)[-4:])
        ax.xaxis.set_major_locator(ticker.FixedLocator(day_list))
        ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))
        mpl_finance.candlestick2_ohlc(
            ax, Open, High, Low, Close, width=0.5, colorup="r", colordown="b"
        )
        self.higharr = High
        self.lowarr = Low

    def qlw_stocklist_currentItemChanged(self):
        if self.block:
            return

        def f():
            time.sleep(1e-323)
            selecteditems = self.qlw_stocklist.selectedItems()
            lenselecteditems = len(selecteditems)
            if not (1 <= lenselecteditems <= 7):
                return
            selecteditem = selecteditems[0]
            code = selecteditem.code
            self.crtstockcode = code
            self.selecteditem = selecteditem
            self.qpb_drawchart_clicked2()

        Thread(target=f, daemon=True).start()

    def qpb_ascendingsearch_clicked(self):
        self.qpb_search_clicked(0)

    def qpb_descendingsearch_clicked(self):
        self.qpb_search_clicked(1)

    def qpb_search_clicked(self, reverse):
        scoreboard = {}
        investor = self.investor
        info = self.info

        if info == 0:
            for code in self.atad.keys():
                try:
                    arrslice = self.get_slice_for_code(code)
                    start = self.atad[code][0][investor][0][arrslice][0]
                    last = self.atad[code][0][investor][0][arrslice][-1]
                    scoreboard[code] = (last / start - 1) * 100 if start != 0 else 0
                except IndexError:
                    continue

        elif info == 1:
            for code in self.atad.keys():
                try:
                    arrslice = self.get_slice_for_code(code)
                    array = self.atad[code][1][investor]
                    stock = self.data[code][7]
                    array = [x / (stock * 10) for x in array]
                    array = array[arrslice]
                    scoreboard[code] = array[-1] - array[0]

                except IndexError:
                    continue

        elif info == 2:
            for code in self.atad.keys():
                arrslice = self.get_slice_for_code(code)
                array = self.atad[code][2][investor][arrslice]
                if self.powerbutton.mode == 0:
                    try:
                        scoreboard[code] = array[-1]
                    except IndexError:
                        continue
                else:
                    try:
                        array_average = sum(array) / len(array)
                    except ZeroDivisionError:
                        continue
                    if self.powerbutton.mode == 1:
                        array_max = max(array)
                        scoreboard[code] = array_max - array_average
                    elif self.powerbutton.mode == -1:
                        array_min = min(array)
                        scoreboard[code] = array_average - array_min

        elif info == 4:
            print(NotImplemented, 673)

        elif info == 5:
            print(NotImplemented, 1551)

        else:
            for code in self.atad.keys():
                try:
                    arrslice = self.get_slice_for_code(code)
                    scoreboard[code] = self.atad[code][info][investor][arrslice][-1]
                except IndexError:
                    continue

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=reverse)
        self.scoreboard2list(scoreboard)

    def qcb_autobookmark_check_or_not(self, scoreboard: dict) -> None:
        if self.qcb_autobookmark.isChecked():
            for code in scoreboard.keys():
                if code not in self.bookmarks:
                    self.bookmarks.append(code)
        self.qlw_bookmarks_showlist()

    def qpb_droppedstocks_clicked(self):  # particular stocks
        scoreboard = {}
        for key, value in self.atad.items():
            try:
                arrslice = self.get_slice_for_code(key)
                yesterday = value[0][self.investor][0][arrslice][-2]
            except IndexError as e:
                print(696, key, e, end="\r")
                continue

            today = value[0][self.investor][0][arrslice][-1]

            score = (today / yesterday - 1) * 100 if today != 0 else 0
            if score < 0:
                scoreboard[key] = score

        self.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1])
        self.scoreboard2list(scoreboard)

    def qpb_bollinger_clicked(self):  # particular stocks
        days_count = self.arrslice.stop - self.arrslice.start
        if days_count < 20:
            QMessageBox.warning(
                self, "", "기간은 최소 20일이어야 합니다.. (현재 %s일)" % days_count
            )
            return

        codenamedatescoreindexprice = []
        for key, value in self.data.items():
            arrslice = self.get_slice_for_code(key)
            chartrows = list(value[4].values())[arrslice]
            if len(chartrows) < 20:
                continue
            arrsign = gen_arrsign(chartrows)
            for sign in arrsign:
                index = sign[0]
                price = chartrows[index][0]
                code = key
                name = value[8]
                date = list(value[4].keys())[arrslice][index]
                score = sign[1]
                score = round(score, 2)
                codenamedatescoreindexprice.append(
                    (code, name, date, score, index, price)
                )
        codenamedatescoreindexprice.sort(key=lambda x: x[3], reverse=1)

        r = []
        bookmarked = []
        self.resultcodelist = []
        for code, name, date, score, index, price in codenamedatescoreindexprice:
            self.resultcodelist.append(code)
            row = []
            if code in self.bookmarks:
                for x in [code, name, date, score]:
                    item = CodeNameDateScoreTableWidgetItem("%s" % x)
                    item.code = code
                    item.vline = index
                    item.hline = price
                    item.setBackground(_BOOKMARK_COLOR)
                    row.append(item)
                bookmarked.append(row)
            else:
                for x in [code, name, date, score]:
                    item = CodeNameDateScoreTableWidgetItem("%s" % x)
                    item.code = code
                    item.vline = index
                    item.hline = price
                    row.append(item)
                r.append(row)

        items = bookmarked + r

        self.qlw_stocklist.clearContents()
        lenitems = len(items)
        self.qlw_stocklist.setRowCount(lenitems)
        for x in range(lenitems):
            for y in range(4):
                self.qlw_stocklist.setItem(x, y, items[x][y])
        self.qlw_stocklist.resizeRowsToContents()
        self.qlw_stocklist.resizeColumnsToContents()

        self.ql_stockcount_showlen()
        return None

    def qpb_boutique_clicked(self):  # particular stocks
        """
        선택한 세력이 갑자기 영향력이 압도적으로 커진 주식을
        결과 창에 표시한다.
        """
        scoreboard = {}
        for key, value in self.atad.items():
            arrslice = self.get_slice_for_code(key)
            array = value[2][self.investor][arrslice]
            score = Global.crushing(array)
            if score > 2:
                scoreboard[key] = score

        self.qcb_autobookmark_check_or_not(scoreboard)
        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
        self.scoreboard2list(scoreboard)

    def qpb_expensivestocks_clicked(self) -> None:  # particular stocks
        """
        검색 기간의 마지막 날에 대해서,
        개인투자자, 외국인투자자, 기관계의 각 평균매수단가 중 가장 비싼 값보다
        그 날의 종가가 더 비싼 주식들을 결과 창에 표시한다.
        """

        scoreboard = {}
        for code in self.atad.keys():
            try:
                arrslice = self.get_slice_for_code(code)
                maxAvgBuyPrice = 0

                for i in (0, 1, 2):
                    maxAvgBuyPrice = max(
                        maxAvgBuyPrice, self.atad[code][0][i][0][arrslice][-1]
                    )

                lastClosePrice = list(self.data[code][4].values())[arrslice][-1][0]

            except IndexError as e:
                print(code, e, end="\r")
                continue

            if lastClosePrice > maxAvgBuyPrice > 0:
                scoreboard[code] = (lastClosePrice / maxAvgBuyPrice - 1) * 100

        self.qcb_autobookmark_check_or_not(scoreboard)
        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
        self.scoreboard2list(scoreboard)

    def qpb_cheapstocks_clicked(self):
        scoreboard = {}
        for code in self.atad.keys():
            if code == "028150":
                continue  ##

            try:
                arrslice = self.get_slice_for_code(code)
                a = self.atad[code][0][0][0][arrslice][-1]
                b = self.atad[code][0][1][0][arrslice][-1]
                c = self.atad[code][0][2][0][arrslice][-1]
                d = self.atad[code][0][0][1][arrslice][-1]
                e = self.atad[code][0][1][1][arrslice][-1]
                f = self.atad[code][0][2][1][arrslice][-1]
                latestprice, latestvolume = list(self.data[code][4].values())[arrslice][
                    -1
                ][0:2]
                if latestvolume == 0:
                    continue
                lowest = min(a, b, c, d, e, f)
                score = lowest / latestprice - 1
            except IndexError as e:
                print(code, e, end="\r")
                continue

            if score > 0:
                scoreboard[code] = score * 100

        self.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=1)
        self.scoreboard2list(scoreboard)

    def qpb_dipperstocks_clicked(self):  # particular stocks

        nvst = self.investor

        scoreboard = {}

        buyorsell = self.qpb_dipperstocks.buyorsell

        for code in self.atad.keys():
            arrslice = self.get_slice_for_code(code)
            array = self.atad[code][0][nvst][buyorsell][arrslice]
            a = self.finddipper(array)
            if a:
                scoreboard[code] = a

        self.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=1)
        self.scoreboard2list(scoreboard)

    def qpb_spikestocks_clicked(self):
        scoreboard = {}

        nvst = self.investor

        for code in self.atad.keys():
            arrslice = self.get_slice_for_code(code)
            array2 = self.atad[code][1][nvst][arrslice]
            if len(array2) < 6:
                continue
            stock = self.data[code][7]
            array = [x / (stock * 10) for x in array2]
            changearr = []
            for i in range(len(array))[-6:-1]:
                change = abs(array[i] - array[i + 1])
                changearr.append(change)
            rangearray = abs(max(array) - min(array))
            maxchange = max(changearr)
            if maxchange > rangearray * 0.5:
                scoreboard[code] = maxchange

        self.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=1)
        self.scoreboard2list(scoreboard)

    def qpb_crossstocks_clicked(self):  # particular stocks
        scoreboard = {}
        if self.qpb_crossstocks.mode == 0:
            for code in self.atad.keys():
                arrslice = self.get_slice_for_code(code)
                barray = self.atad[code][0][self.investor][0][arrslice]
                sarray = self.atad[code][0][self.investor][1][arrslice]
                if not (len(barray) >= 2 and len(sarray) >= 2):
                    continue
                cond0 = sarray[-1] == sarray[-2]
                cond2 = barray[-2] < sarray[-2]
                cond3 = sarray[-1] < barray[-1]
                if cond0 and cond2 and cond3:
                    scoreboard[code] = (barray[-1] / barray[-2] - 1) * 100
        else:
            for code in self.atad.keys():
                arrslice = self.get_slice_for_code(code)
                barray = self.atad[code][0][self.investor][0][arrslice]
                sarray = self.atad[code][0][self.investor][1][arrslice]
                if not (len(barray) >= 2 and len(sarray) >= 2):
                    continue
                cond0 = barray[-1] == barray[-2]
                cond2 = sarray[-2] < barray[-2]
                cond3 = barray[-1] < sarray[-1]
                if cond0 and cond2 and cond3:
                    scoreboard[code] = (sarray[-1] / sarray[-2] - 1) * 100

        self.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=1)
        self.scoreboard2list(scoreboard)

    def qdsb_level_returnpressed(self):
        codenamescorehline = []
        scoreboard = {}
        level = self.qdsb_level.value()
        if self.investor == 0:
            for code in self.atad.keys():
                try:
                    arrslice = self.get_slice_for_code(code)
                    minpower = min(self.atad[code][2][self.investor][arrslice])
                except ValueError:
                    continue
                difference = level - minpower
                if difference >= 0:
                    codenamescorehline.append(
                        [code, self.convertcode2name(code), difference, level]
                    )
                    scoreboard[code] = difference
        else:
            for code in self.atad.keys():
                try:
                    arrslice = self.get_slice_for_code(code)
                    maxpower = max(self.atad[code][2][self.investor][arrslice])
                except ValueError:
                    continue
                difference = maxpower - level
                if difference >= 0:
                    codenamescorehline.append(
                        [code, self.convertcode2name(code), difference, level]
                    )
                    scoreboard[code] = difference

        self.qcb_autobookmark_check_or_not(scoreboard)

        codenamescorehline = sorted(codenamescorehline, key=lambda x: x[2], reverse=1)

        r = []
        bookmarked = []
        self.resultcodelist = []
        for code, name, score, hline in codenamescorehline:
            self.resultcodelist.append(code)
            score = round(score, 2)
            if code in self.bookmarks:
                row = []
                for x in [code, name, "", score]:
                    item = CodeNameDateScoreTableWidgetItem("%s" % x)
                    item.code = code
                    item.hline = hline
                    item.memo = "onlypower"
                    item.setBackground(_BOOKMARK_COLOR)
                    row.append(item)
                bookmarked.append(row)
            else:
                row = []
                for x in [code, name, "", score]:
                    item = CodeNameDateScoreTableWidgetItem("%s" % x)
                    item.code = code
                    item.hline = hline
                    item.memo = "onlypower"
                    row.append(item)
                r.append(row)

        items = bookmarked + r

        self.qlw_stocklist.clearContents()
        lenitems = len(items)
        self.qlw_stocklist.setRowCount(lenitems)
        for x in range(lenitems):
            for y in range(4):
                self.qlw_stocklist.setItem(x, y, items[x][y])
        self.qlw_stocklist.resizeRowsToContents()
        self.qlw_stocklist.resizeColumnsToContents()

        self.ql_stockcount_showlen()

    def qpb_keepbuystocks_clicked(self):
        a = self.qpb_keepbuystocks.a
        self.qpb_keepbuyorsell_clicked(a)

    def qpb_keepsellstocks_clicked(self):
        a = self.qpb_keepsellstocks.a
        self.qpb_keepbuyorsell_clicked(a + 2)

    def qpb_keepbuyorsell_clicked(self, a: int) -> None:  # particular stocks
        """
        최근 20일 중 평균거래단가가 4번 이상 증가/감소한 종목을 표시한다.
        Args:
         a:
          - 0: Keepbuy Stocks ▼
          - 1: Keepbuy Stocks ▲
          - 2: Keepsell Stocks ▼
          - 3: Keepsell Stocks ▲
        Raises:
         AssertionError: a is not in (0,1,2,3).
        """

        assert a in (0, 1, 2, 3)

        dict_scoreboard = {}

        for code in self.atad.keys():
            arrslice = self.get_slice_for_code(code)
            arr = self.atad[code][0][self.investor][a > 1][arrslice][-20:]
            score = keepbuy(arr) if a % 2 == 0 else keepbuy2(arr)

            if score >= 4:
                dict_scoreboard[code] = score

        list_scoreboard = sorted(
            dict_scoreboard.items(), key=lambda x: x[1], reverse=True
        )[:400]
        self.qcb_autobookmark_check_or_not(dict_scoreboard)
        self.scoreboard2list(list_scoreboard)

    def qpb_closestocks_clicked(self):  # particular stocks
        scoreboard = {}

        nvst = self.investor

        if self.arrslice.start == 0:
            for code in self.atad:
                arrslice = self.get_slice_for_code(code)
                try:
                    마지막날매수 = self.atad[code][0][nvst][0][arrslice][-1]
                    마지막날매도 = self.atad[code][0][nvst][1][arrslice][-1]
                except IndexError as e:
                    print(code, e, end="\r")
                    continue
                if 마지막날매수 == 마지막날매도:
                    scoreboard[code] = 0
                    continue
                else:
                    a, b = max(마지막날매수, 마지막날매도), min(
                        마지막날매수, 마지막날매도
                    )
                try:
                    scoreboard[code] = (a - b) / a * 100
                except ZeroDivisionError:
                    scoreboard[code] = -b * 100
        else:
            for code in self.atad:
                arrslice = self.get_slice_for_code(code)
                b = 0 if self.qpb_closestocks.a == 0 else 1
                arr = self.atad[code][0][nvst][b][arrslice]
                try:
                    if arr[-1] == 0:
                        continue
                except IndexError:
                    continue
                rows = list(self.data[code][4].values())[arrslice]
                Close = [row[0] for row in rows]
                try:
                    if max(Close) == min(Close):  # 거래 정지 종목 제외시키기
                        continue
                except ValueError as e:
                    if e.args[0] == "max() arg is an empty sequence":
                        continue
                    else:
                        raise e
                maxvalue = max(arr)
                minvalue = min(arr)
                price_variation = (maxvalue - minvalue) / ((maxvalue + minvalue) / 2)
                scoreboard[code] = price_variation * 100

        self.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1])
        self.scoreboard2list(scoreboard)

    def qpb_redredred_clicked(self):
        scoreboard = {}
        investor = self.investor

        for key in self.atad.keys():
            arrslice = self.get_slice_for_code(key)
            array = self.atad[key][2][investor][arrslice]
            directionarray = self.atad[key][3][investor][arrslice]
            if self.qpb_redredred.mode == 0:
                red = 0
                others = 0
                for i in range(len(directionarray)):
                    value = directionarray[i]
                    if value == 100:
                        red += array[i]
                    # else:
                    #     others += array[i]
                score = red  # / (others + 1)
            else:
                blue = 0
                others = 0
                for i in range(len(directionarray)):
                    value = directionarray[i]
                    if value == -100:
                        blue += array[i]
                    # else:
                    #     others += array[i]
                score = blue  # / (others + 1)
            if score > 3:
                scoreboard[key] = score

        self.qcb_autobookmark_check_or_not(scoreboard)

        scoreboard = sorted(scoreboard.items(), key=lambda x: x[1], reverse=True)
        self.scoreboard2list(scoreboard)

    def qpb_save_clicked(self):
        if not self.resultcodelist:
            QMessageBox.warning(self, "", "저장할 종목이 없습니다!")
            return

        reply = QMessageBox.question(
            self, "", f"위에서부터 최대 {Constants.MAXSTOCK}개 종목을 저장할까요?"
        )
        if reply == QMessageBox.Yes:
            codes = [x for x in self.resultcodelist[: Constants.MAXSTOCK]]
            filename = f"search{generatenow()}"
            filedir = f"{Constants.SAVEDIR}\\{filename}.csv"
            writeintereststock(filedir, codes)
            QMessageBox.information(
                self, "", f"{filedir}에 {len(codes)}개의 종목을 저장하였습니다."
            )

            self.block = True

            start = self.savestackcount * 100
            stop = (self.savestackcount + 1) * 100
            for x in range(start, stop):
                for y in range(4):
                    self.qlw_stocklist.takeItem(x, y)
            self.savestackcount += 1

            self.block = False
            self.resultcodelist = self.resultcodelist[Constants.MAXSTOCK :]

            self.ql_stockcount_showlen()

    def qpb_savedir_clicked(self):
        os.startfile(Constants.SAVEDIR)

    def qpb_importcsv_clicked(self):
        fp = QFileDialog.getOpenFileName(self)[0]
        if fp == "":
            return 0
        csvcodelist = parse(fp).keys()
        nocode = []
        yescode = []
        for code in csvcodelist:
            if code in self.codelist:
                yescode.append(code)
            else:
                nocode.append(code)
        self.bookmarks += yescode
        self.bookmarks = list(set(self.bookmarks))
        self.qlw_bookmarks_showlist()
        if nocode:
            QMessageBox.warning(
                self, "", f"{nocode}가 데이터에 없으므로 무시되었습니다."
            )

    def scoreboard2list(self, scoreboard: list):
        """
        Display a given scoreboard on QTableWidget.
        Args:
         scoreboard:
          Type is list.
          [(code1,score1),(code2,score2),...]
          code is str. score is int or float.
        """
        r = []
        bookmarked = []
        self.resultcodelist = []
        for code, score in scoreboard:
            self.resultcodelist.append(code)
            name = self.data[code][8]
            score = round(score, 2)
            if code in self.bookmarks:
                row = []
                for x in [code, name, "", score]:
                    item = CodeNameDateScoreTableWidgetItem("%s" % x)
                    item.code = code
                    item.setBackground(_BOOKMARK_COLOR)
                    row.append(item)
                bookmarked.append(row)
            else:
                row = []
                for x in [code, name, "", score]:
                    item = CodeNameDateScoreTableWidgetItem("%s" % x)
                    item.code = code
                    row.append(item)
                r.append(row)

        items = bookmarked + r

        self.qlw_stocklist.clearContents()
        lenitems = len(items)
        self.qlw_stocklist.setRowCount(lenitems)
        for x in range(lenitems):
            for y in range(4):
                self.qlw_stocklist.setItem(x, y, items[x][y])
        self.qlw_stocklist.resizeRowsToContents()
        self.qlw_stocklist.resizeColumnsToContents()

        self.ql_stockcount_showlen()

    def showmenu(self):
        a0 = QAction(i18n[2], triggered=self.addbookmark)
        a1 = QAction("Remove Bookmark", triggered=self.removebookmark)
        self.menu.addActions([a0, a1])
        self.menu.exec_(QCursor.pos())

    def addbookmark(self):
        items = self.qlw_stocklist.selectedItems()
        for item in items:
            item.setBackground(_BOOKMARK_COLOR)
            code = item.code
            if code not in self.bookmarks:
                self.bookmarks.append(code)
        self.qlw_bookmarks_showlist()

    def removebookmark(self):
        items = self.qlw_stocklist.selectedItems()
        for item in items:
            item.setBackground(Qt.color0)
            code = item.code
            if code in self.bookmarks:
                self.bookmarks.remove(code)
        self.qlw_bookmarks_showlist()

    def qlw_bookmarks_showlist(self):
        self.qlw_bookmarks.clear()
        self.bookmarks.sort()
        bookmark_display = [f"{x},{self.data[x][8]}" for x in self.bookmarks]
        self.qlw_bookmarks.addItems(bookmark_display)
        self.qgb_bookmarks.setTitle(f"{i18n[18]} ({len(self.bookmarks)})")

    def finddipper(self, array):
        if len(array) < 3:
            return False

        a0 = array[-1]
        a1 = array[-2]
        if not a1 < a0 * 0.99:
            return False

        yellow_max = a1 * 1.01
        yellow_min = a1 * 0.99

        index = None
        for index, x in list(enumerate(array[:-2]))[::-1]:
            if index == 0:
                return False
            if not yellow_min <= x <= yellow_max:
                break

        a3 = array[index]
        if not a0 * 0.99 < a3 < a0 * 1.01:
            return False

        a4 = array[index - 1]
        if not a3 * 0.99 < a4 < a3 * 1.01:
            return False

        return a0 / a1 * 100
