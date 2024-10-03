# pickle
세력모니터는 주식 데이터를 pickle 형태로 저장한다.
키움증권에서 받아온 데이터는 data.p로 저장한다.
data.p를 토대로 분석 데이터를 만든 것은 atad.p로 저장한다.
이 문서는 pickle에 담긴 dict의 구조를 설명하기 위해 만들어졌다.

## 용어 정의
n차 key는 원천 dict 바로 아래의 key이다. 즉 dict.keys()이다.
n차 value는 n차 key까지 넣었을 때 나오는 value를 뜻한다.
(n+1)차 key는 n차 value의 key이다.

e.g., data의 1차 key 중 하나는 "005930"이다.
data["005930"]은 1차 value이다.
data["005930"][4]["20240829"]는 3차 value이다.
이때 "20240829"는 data의 3차 key이다.

## data.p
data.p에는 dict 하나가 담겨있다.

### 1차 key
dict의 keys는 세력모니터에 사용할 모든 종목코드와 "000000"이다.
따라서 모든 종목코드를 얻고 싶다면 data.keys()로 iteration을 돌리고
"000000"만 제외시키면 된다. data.keys()에 있는 키들은 모두 문자열이다.

### 일반 종목코드의 keys(2차 key)
다음 key는 모두 int이다.

주식일봉차트는 4 . . . [c, v, vm, o, h, l] (opt10081)
- 8자리 yyyyMMdd date를 3차 key로 갖는다.
- 이 dict는 3차 key에 대해 오름차순으로 정렬되어있다.
- 3차 value는 list [현재가, 거래량, 거래대금, 시가, 고가, 저가]다.
- 3차 value list 안에 들어있는 것은 모두 int이다.

매수는 5 (opt10059)
- 8자리 yyyyMMdd date를 key로 갖는다.
- 이 dict는 3차 key에 대해 오름차순으로 정렬되어있다.
- 3차 value는 list [현재가, 대비기호, 전일대비, 등락율, 누적거래량, 누적거래대금,
개인투자자, 외국인투자자, 기관계, 금융투자, 보험, 투신, 기타금융, 은행, 연기금등,
사모펀드, 국가, 기타법인, 내외국인]이다. list length는 19이다.
- 3차 value list 안에 들어있는 것은 모두 음이 아닌 int이다.

매도는 6 (opt10059)
- 매수와 동일한 속성.
- 단, 3차 value list 안에 들어있는 것은 모두 **양이 아닌** int이다.
(매도량은 음수로 표현된다.)

유통주식수는 7
- 2차 value는 int이다. 유통주식수 데이터가 정수로 parse되지 못할 경우 1이다.

이름은 8
- value 종목명은 str이다.
- 앞뒤 공백이 없는 길이 1 이상의 한글이 포함될 수 있는 문자열이다.

코스피닥구분은 11 (KOSPI: 0, not KOSPI: 1)
- 0과 1은 모두 int이다.

### "000000"의 keys(2차 key)
다음 key는 모두 int이다.

KOSPI 업종 차트는 9 (opt20006)
- 8자리 yyyyMMdd date를 key로 갖는다.
- 이 dict는 3차 key에 대해 오름차순으로 정렬되어있다.
- 3차 value는 list [현재가, 거래량, 시가, 고가, 저가, 거래대금]이다.
- 3차 value list 안에 들어있는 것은 모두 int이다.

KOSDAQ 업종 차트는 10 (opt20006)
- KOSPI 업종 차트와 동일한 속성.

## atad.p

### atad.p의 1차 key
1차 key는 data.p에서의 1차 key인 모든 종목코드이다.
(단, "000000"은 제외된다.)

### atad.p의 2차 key
2차 key는 모두 int이다.

평균거래단가는 0
- 2차 value는 (13,2,N) list이다. 0차원 index는 투자자 index이다.
[개인투자자, 외국인투자자, 기관계, 금융투자, 보험, 투신, 기타금융, 은행, 연기금등,
사모펀드, 국가, 기타법인, 내외국인]
- 1차원 index는 0 또는 1인데, 0이면 평균매수단가, 1이면 평균매도단가이다.
- 2차원 index는 날짜 오름차순의 index이다.
- e.g., atad["005930"][0][11][1][-1]:
삼성전자에서의 기타법인의 마지막 날의 평균매도단가

보유비중은 1
Type: list
Item Type: int
Dimension: (13,N) (N is the total number of days)

영향력은 2
Type: list
Item Type: float
Dimension: (13,N) (N is the total number of days)

방향은 3
Type: list
Item Type: float
Dimension: (13,N) (N is the total number of days)
