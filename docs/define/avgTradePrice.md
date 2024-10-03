# avgTradePrice
평균 거래 단가는 각 세력에 대해 종목별, 일자별로 정의된다.
평균 거래 단가를 계산하는 의사 코드는 다음과 같다.
```
avgBuyPrices = []
avgSellPrices = []
buyMoney = 0
buyVolume = 0
sellMoney = 0
sellVolume = 0
# S[i]: i번째 일자의 매도량(0 또는 양수)
# B[i]: i번째 일자의 매수량(0 또는 양수)
# C[i]: i번재 일자의 종가(양수)
# 0으로 나눌 시 0으로 취급
# adjust(A): 1차원 float 배열에서의 모든 0을 그 배열에서 처음 나오는 양수로 대체
# e.g.) adjust([0,0,...,0,1.2,4.5,3.7])=[1.2,1.2,...,1.2,1.2,4.5,3.7]
for i in range(len(B)):
    netbuy=B[i]-S[i]
	money=C[i]*netbuy
	if netbuy > 0:
	    buyVolume += netbuy
		buyMoney += money
	else:
	    sellVolume += netbuy
		sellMoney += money
	avgBuyPrices.append(buyMoney / buyVolume)
	avgSellPrices.append(sellMoney / sellVolume)
	adjust(avgBuyPrices)
	adjust(avgSellPrices)
```
평균 거래 단가를 선택하면 차트에는 매수는 빨간 선, 매도는 파란 선으로 표시된다.
