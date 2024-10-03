# RS (Relative Strength)
C(i): i번째 날의 종가

M(i): i번째 날의 지수 종가.
KOSPI 종목이면 KOSPI 지수,
KOSDAQ 종목이면 KOSDAQ 지수를 기준으로 한다.

R(i): i번째 날의 RS
R(i) := ( C(i) / C(0) ) / ( M(i) / M(0) )
R(i)는 0 이상의 유리수이다.
