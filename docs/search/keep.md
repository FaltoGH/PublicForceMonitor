# keep
선택한 날짜 범위에서
최근 20일 중 평균거래단가가 4번 이상 증가/감소한 종목을
표시한다.

keep는 다음 4개가 정의된다.
- 평균매수단가 감소
- 평균매수단가 증가
- 평균매도단가 감소
- 평균매도단가 증가

감소 점수 함수는 다음과 같다.
arr는 평균거래단가의 배열이다.
```py
def score(arr: list) -> int:
    ret = 0
    for i in range(len(arr) - 1):
        if arr[i] > arr[i + 1]:
            ret += 1
    return ret
```

최소 노출 점수: 4

정렬: 점수 내림차순