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
                    
    def price(chartrows:list, buyrows:list, sellrows:list)->list:
        """
        평균거래단가를 계산하고 (13,2,N) float list를 반환합니다.
        (13,[0],N)은 평균매수단가, (13,[1],N)은 평균매도단가입니다.
        """

        ret = []

        for nvst in range(6, 19):

            meanbuyprice = []
            meansellprice = []
            sumbuypv, sumbuyv, sumsellpv, sumsellv = 0, 0, 0, 0

            for i in range(len(buyrows)):
                assert buyrows[i][nvst]>=0
                assert sellrows[i][nvst]<=0

                # 순매수
                netbuy = buyrows[i][nvst] + sellrows[i][nvst]
                netbuy:int

                # 거래대금
                pv = abs(chartrows[i][Constants.IDX_81_CLOSE]) * netbuy
                pv:int

                if pv > 0:
                    sumbuyv += netbuy
                    sumbuypv += pv
                elif pv < 0:
                    sumsellv += netbuy
                    sumsellpv += pv

                abuyp = sumbuypv / sumbuyv if sumbuyv != 0 else 0
                asellp = sumsellpv / sumsellv if sumsellv != 0 else 0

                assert abuyp >= 0
                assert asellp >= 0

                meanbuyprice.append(abuyp)
                meansellprice.append(asellp)

            Util.adjust0(meanbuyprice)
            Util.adjust0(meansellprice)

            assert len(meanbuyprice) == len(buyrows)
            ret.append([meanbuyprice, meansellprice])

        #19-6=13, the number of investors
        assert len(ret) == 13 

        return ret
    
    def float2time(f:float) -> str:
        return datetime.datetime.fromtimestamp(f).strftime('%Y-%m-%d %H:%M:%S')

    def get_existing_kiwoom_data_downloaded_before()->dict:
        """
        이전에 다운로드받아놓은 데이터를 data.p에서 불러옵니다.
        
        파일이 존재하지 않거나 불러오기에 실패할 경우 비어 있는 dict()를 반환합니다.
        """
        if os.path.exists(Constants.PATH_DATAP):
            with open(Constants.PATH_DATAP, 'rb') as f:
                try:
                    return pickle.load(f)
                except EOFError as ex:
                    warnings.warn("Cannot load data.p. return default. Exception is %s"%ex)
                    time.sleep(3)
        return dict()
