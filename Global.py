"""
Provides global information that can be accessed from every python module in
this project. Do not import any custom project modules in this file.
"""

import datetime
import csv

i18n = [
    "분석자료 만들기",
    "분석자료 읽기",
    "종목 북마크",
    "수익률 상위종목",
    "수익률 하위종목",
    "매수 우세 종목",
    "매도 우세 종목",
    "세력 스파이크",
    "최대 거래량",
    "최소 거래량",
    "자동 북마크",
    "연속매수종목",
    "연속매도종목",
    "세력선택",
    "데이터 처리",
    "종목 입력",
    "종목 검색",
    "검색창",
    "북마크 종목창",
    "오름차순",
    "내림차순",
    "100종목 저장",
    "선택종목 삭제",
    "종목 저장",
    "종목 삭제",
    "csv 파일 읽기",
    "종목코드 내보내기",
    "북마크 종목 분석하기",
    "데이터 다운로드",
]

def generate_new_arrslice(length: int, arrslice: slice) -> slice:
    """
    # params
    length: Length of array, typically the number of chart candle days.
    arrslice: The slice which respects to 600 days.
    """
    if length == 600:
        return arrslice
    difference = 600 - length
    return slice(
        max(arrslice.start - difference, 0), max(arrslice.stop - difference, 1)
    )

def get_typical_price(chartrow:list)->float:
    """
    chartrow: [c, v, vm, o, h, l]
    https://en.wikipedia.org/wiki/Typical_price
    """
    close = chartrow[0]
    high = chartrow[4]
    low = chartrow[5]
    tPrice = close + high + low
    tPrice /= 3
    return tPrice

def gen_lbb(arrprice:list):
    """
    # arguments
    - arrprice
      - len(arrprice) == 20

    # returns
    Lower Bollinger Band(N=20, K=2)
    from given 20 days prices.
    """
    ma20 = sum(arrprice) / 20
    squares = []
    for price in arrprice:
        squares.append((price - ma20)** 2)
    variance = sum(squares) / 20
    standard_deviation = variance ** 0.5
    lbb = ma20 - 2 * standard_deviation
    return lbb

def gen_arrlbb(arrprice:list):
    """
    # arguments
    - arrprice
      - len(arrprice) >= 20
    
    # returns
    Lower Bollinger Band list of length len(arrprice)-19.
    """
    arrlbb = []
    for i in range(len(arrprice) - 19):
        lbb = gen_lbb(arrprice[i:i+20])
        arrlbb.append(lbb)
    return arrlbb

def gen_arrsign(chartrows:list)->list:
    """
    # arguments
    - chartrows
      - [[c, v, vm, o, h, l], [...]]
      - len(chartrows) >= 20
    """
    # 마지막 날의 거래량이 0이라면
    # 거래 정지일 확률이 높다.
    if chartrow[-1][1] == 0:
        return []
    if len(chartrows) < 20:
        return []
    lastClosePrice = chartrow[-1][0]
    typicalPrices = [get_typical_price(x) for x in chartrows]
    LBBs = gen_arrlbb(typicalPrices)
    arrsign = []
    for index, chartrow in enumerate(chartrows[19:]):
        absIndex = index + 19
        close = chartrow[0]
        openp = chartrow[3]
        low = chartrow[5]
        # 종가가 min(LBB,시가)보다 작으면
        if close < min(LBBs[index],openp):
            for index2, chartrow2 in enumerate(chartrows[absIndex+1:]):
                # 고가가 기준저가 이상이면서 종가가 min(시가-1,LBB)보다 크면
                if chartrow2[4] >= low and chartrow2[0] > min(chartrow2[3]-1,LBBs[index+index2+1]):
                    break
            else:
                arrsign.append((absIndex, (close / lastClosePrice - 1) * 100))
    return arrsign


def csvload(fp: str):
    with open(fp, "r") as f:
        reader = csv.reader(f)
        listreader = list(reader)
    return listreader


def parse(fp):
    rows = csvload(fp)
    head = rows[0]
    rows = rows[1:]
    stockdict = {}
    if "종목코드" in head:
        index = {"종목코드": head.index("종목코드"), "현재가": head.index("현재가")}
        for row in rows:
            code = row[index["종목코드"]]
            if code == "":
                continue
            code = code[-6:]
            price = row[index["현재가"]]
            price = price.replace(",", "")
            price = int(price)
            stockdict[code] = price
    else:
        for row in rows:
            code = row[0]
            stockdict[code.removeprefix("'")] = 0
    return stockdict


def slice100(mylist: list):
    r = []
    for i in range(0, len(mylist), 100):
        r.append(mylist[i : i + 100])
    return r


def writeintereststock(filedir, codelist):
    with open(filedir, "wt") as wtf:
        wtf.writelines([",\n", *[f"'{code},\n" for code in codelist]])
    return None


def generatenow():
    r = datetime.datetime.now().strftime("%H%M%S")
    return r


def keepbuy(arr):
    ret = 0
    for i in range(len(arr) - 1):
        if arr[i] > arr[i + 1]:
            ret += 1
    return ret


def keepbuy2(arr):
    ret = 0
    for i in range(len(arr) - 1):
        if arr[i] < arr[i + 1]:
            ret += 1
    return ret


def ignore_too_small_number(x):
    if x < 2:
        return 0
    else:
        return x


def crushing(mylist: list):
    mylist = list(map(ignore_too_small_number, mylist))
    if len(mylist) < 2:
        return False, 0
    _mylist = mylist.copy()
    mylist_max = max(_mylist)
    _mylist.remove(mylist_max)
    mylist_max2 = max(_mylist)
    try:
        score = mylist_max / mylist_max2
    except ZeroDivisionError:
        score = 0
    return (score > 2), score


def weight(buyrows:list, sellrows:list) -> list:
    """
    보유비중
    """
    ret = []
    for nvst in range(6, 19):
        a = 0
        array = []
        for i in range(len(buyrows)):
            a += buyrows[i][nvst] + sellrows[i][nvst]
            array.append(a)
        ret.append(array)
    return ret

def power(buyrows:list, sellrows:list)->list:
    """
    영향력 (atad[code][2])
    
    # returns
    Type is list.
    Element type is float.
    Dimension is (F,N).
    """
# data[code][5]
# data[code][6]
# - type: dict
# - key type: str
# - key: yyyyMMdd
# - It is sorted by ascending order.
# - value type: list
# - value: [현재가, 대비기호, 전일대비, 등락율, 누적거래량,
# 누적거래대금, 개인투자자, 외국인투자자, 기관계, 금융투자,
# 보험, 투신, 기타금융, 은행, 연기금등,
# 사모펀드, 국가, 기타법인, 내외국인]
# Length is 19.
# buyrows, sellrows: Type is int. Demension is (600,19).
    ret = []
    N=len(buyrows)
    for F in range(6, 19):
        buy = [buyrow[F] for buyrow in buyrows]
        sell = [abs(sellrow[F]) for sellrow in sellrows]
        buysell = [buy[i] + sell[i] for i in range(N)]
        volumex2 = [buyrow[4] * 2 for buyrow in buyrows]
        powe = [buysell[i] / volumex2[i] * 100 if volumex2[i] != 0 else 0 for i in range(N)]
        ret.append(powe)
    return ret

def direction(buyrows:list, sellrows:list)->list:
    """
    방향 (atad[code][3])

    # returns
    Type is list.
    Element type is float.
    Dimension is (F,N).
    """
    ret = []
    N=len(buyrows)
    for F in range(6, 19):
        buy = [buyrow[F] for buyrow in buyrows]
        sell = [sellrow[F] for sellrow in sellrows]
        buysell = [buy[i] + abs(sell[i]) for i in range(N)]
        netbuy = [buy[i] + sell[i] for i in range(N)]
        directio = [netbuy[i] / buysell[i] * 100 if buysell[i] != 0 else 0 for i in range(N)]
        ret.append(directio)
    return ret
