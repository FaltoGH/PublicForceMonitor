i18n = ["분석자료 만들기","분석자료 읽기",
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
    "데이터 다운로드"
]

import datetime
import csv

def generate_new_arrslice(arr: list, arrslice: slice, maxlen: int):
    if len(arr) == maxlen:
        return arrslice
    difference = maxlen - len(arr)
    return slice(
        max(arrslice.start - difference, 0), max(arrslice.stop - difference, 1)
    )


def gen_lbb(arrprice: list):
    "len(arg0) == 20"
    ma20 = sum(arrprice) / 20
    deviation = []
    for x in arrprice:
        deviation.append(x - ma20)
    deviation2 = []
    for x in deviation:
        deviation2.append(x**2)
    variance = sum(deviation2) / 20
    standard_deviation = variance**0.5
    lbb = ma20 - 2 * standard_deviation
    return lbb


def gen_arrlbb(arrprice: list):
    "len(arg0) >= 20"
    arrlbb = []
    for i in range(len(arrprice) - 19):
        lbb = gen_lbb(arrprice[i : i + 20])
        arrlbb.append(lbb)
    return arrlbb


def gen_arrsign(chartrows: list):
    """arg0 == [[c, v, vm, o, h, l], [...]]
    len(arg0) >= 20"""
    arrcloseprice = []
    arrtypicalprice = []
    for chartrow in chartrows:
        closeprice = chartrow[0]
        highprice = chartrow[4]
        lowprice = chartrow[5]
        typicalprice = closeprice + highprice + lowprice
        typicalprice /= 3
        arrtypicalprice.append(typicalprice)
        arrcloseprice.append(closeprice)

    # 거래정지 거르는 알고리즘
    if chartrow[1] == 0:
        return []
    # -----------------------

    latestprice = arrcloseprice[-1]
    arrlbb = gen_arrlbb(arrtypicalprice)
    arrsign = []
    for index, chartrow in enumerate(chartrows[19:]):
        indexoftotal = index + 19
        closeprice = arrcloseprice[indexoftotal]
        if closeprice >= arrlbb[index]:
            continue
        openprice = chartrow[3]
        if closeprice >= openprice:
            continue
        lowprice = chartrow[5]

        for index2, chartrow2 in enumerate(chartrows[indexoftotal + 1 :]):
            if chartrow2[4] >= lowprice:  # 고가가 사인저가보다 높으면
                if chartrow2[0] >= chartrow2[3]:  # 양봉이면
                    break
                elif (
                    chartrow2[0] > arrlbb[index + index2 + 1]
                ):  # 종가가 lbb 위에 있으면
                    break
        else:
            arrsign.append((indexoftotal, (closeprice / latestprice - 1) * 100))
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


def weight(buyrows: list, sellrows: list):
    ret = []
    for nvst in range(6, 19):
        a = 0
        array = []
        for i in range(len(buyrows)):
            a += buyrows[i][nvst] + sellrows[i][nvst]
            array.append(a)
        ret.append(array)
    return ret


def power(buyrows: list, sellrows: list):
    ret = []
    rang = range(len(buyrows))
    for nvst in range(6, 19):
        buy = [buyrow[nvst] for buyrow in buyrows]
        sell = [abs(sellrow[nvst]) for sellrow in sellrows]
        buysell = [buy[i] + sell[i] for i in rang]
        volumex2 = [buyrow[4] * 2 for buyrow in buyrows]
        powe = [buysell[i] / volumex2[i] * 100 if volumex2[i] != 0 else 0 for i in rang]
        ret.append(powe)

    return ret


def direction(buyrows: list, sellrows: list):
    ret = []
    rang = range(len(buyrows))
    for nvst in range(6, 19):
        buy = [buyrow[nvst] for buyrow in buyrows]
        sell = [sellrow[nvst] for sellrow in sellrows]
        buysell = [buy[i] + abs(sell[i]) for i in rang]
        netbuy = [buy[i] + sell[i] for i in rang]
        directio = [
            netbuy[i] / buysell[i] * 100 if buysell[i] != 0 else 0 for i in rang
        ]
        ret.append(directio)
    return ret
