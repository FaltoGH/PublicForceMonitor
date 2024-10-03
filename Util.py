import os
import pickle
import time
import datetime
from typing import Any
import warnings

from Constants import Constants

class Util:
    def assert_equal(x,y)->None:
        """
        두 인수를 비교하고 서로 다르다면 오류를 발생시킵니다.
        """
        if x != y:
            raise AssertionError("not equal",x,y)

    def calc_eta(current:int, total:int, start_time:float)->datetime.timedelta:
        """
        남은 시간을 계산합니다.
        """
        now=time.time()
        if current > 0:
            seconds=(now - start_time) * (total / current - 1)
            return datetime.timedelta(0, seconds)
        else:
            return datetime.timedelta(0, 1)

    def pickleload(filedir:str)->Any:
        """
        Load pickle object from given file path.
        """
        with open(filedir, 'rb') as rbf:
            return pickle.load(rbf)
        
    def is_ascending(x:list) -> bool:
        """
        리스트가 오름차순으로 정렬되어있는지의 여부를 확인합니다.

        오름차순 정렬이라면 True, 아니라면 False를 반환합니다.
        """
        if len(x) < 2:
            return True
        
        prev = x[0]

        for item in x[1:]:
            if prev > item:
                return False
            prev = item

        return True

    def pickledump(obj:Any, filedir:str)->None:
        with open(filedir, 'wb') as wbf:
            pickle.dump(obj, wbf)
    
    def get_progress_msg(current:int, total:int, start_time:float,
        current_task:str)->str:
        if total==0:total=1
        eta=Util.calc_eta(current,total,start_time)
        return "%d/%d | %.2f%% | ETA %s | %s"%(
            current, total, (current/total*100), eta, current_task)

    def adjust0(mylist:list)->None:
        """
        1차원 float 배열을 입력받고, 그 배열 안의 모든 0을
        배열에서 처음으로 나오는 양수로 대체합니다. 만약 그런 양수가 없을 경우
        아무것도 하지 않습니다.

        e.g.,
        [0, 0, 1.2, 2.3, 0, 2.4] -> [1.2, 1.2, 1.2, 2.3, 1.2, 2.4]
        
        [0, 0, 0] -> [0, 0, 0]

        mylist: 1차원 float 배열
        """
        a = 0
        for x in mylist:
            if x > 0:
                a = x
                break
        if a > 0:
            for index, x in enumerate(mylist):
                if x == 0:
                    mylist[index] = a

    @staticmethod                    
    def price(chartrows:list, buyrows:list, sellrows:list)->list:
        """
data[code][5]
data[code][6]
- type: dict
- key type: str
- key: yyyyMMdd
- It is sorted by ascending order.
- value type: list
- value: [현재가, 대비기호, 전일대비, 등락율, 누적거래량,
누적거래대금, 개인투자자, 외국인투자자, 기관계, 금융투자,
보험, 투신, 기타금융, 은행, 연기금등,
사모펀드, 국가, 기타법인, 내외국인]
Length is 19.

data[code][4]
- type: dict
- key type: str
- key: yyyyMMdd
- It is sorted by ascending order.
- value type: list
- value: [c,v,m,o,h,l]
They are all non-negative integers.

# params
buyrows, sellrows: Type is int. Demension is (600,19).
chartrows: Type is int. Demension is (600,6).
This function calculates avgTradePrice.
Type is float. Demension is (13,2,600).

# returns
returns avgTradePrices.
(13,[0],600) is buy.
(13,[1],600) is sell.
"""
        ret = []
        for F in range(6,19):
            avgBuyPrices = []
            avgSellPrices = []
            buyMoney=0
            buyVolume=0
            sellMoney=0
            sellVolume=0
            for i in range(len(buyrows)):
                netbuy = buyrows[i][F] + sellrows[i][F]
                close=chartrows[i][0]
                money = abs(close) * netbuy
                if netbuy > 0:
                    buyVolume += netbuy
                    buyMoney += money
                elif netbuy < 0:
                    sellVolume += netbuy
                    sellMoney += money
                avgBuyPrice = buyMoney / buyVolume if buyVolume != 0 else 0
                avgSellPrice = sellMoney / sellVolume if sellVolume != 0 else 0
                avgBuyPrices.append(avgBuyPrice)
                avgSellPrices.append(avgSellPrice)
            Util.adjust0(avgBuyPrices)
            Util.adjust0(avgSellPrices)
            ret.append([avgBuyPrices, avgSellPrices])
        return ret
    
    def float2time(f:float) -> str:
        return datetime.datetime.fromtimestamp(f).strftime('%Y-%m-%d %H:%M:%S')
